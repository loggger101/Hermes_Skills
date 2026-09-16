# Flowsint Pipeline Architecture Patterns (verified from reconurge/flowsint @ 1820569, v1.2.12)

Source: full source-level read of the repo (325 py files / ~47k LOC Python+TS). Flowsint is an OSINT graph
exploration tool — but its architecture is a clean reference for **any multi-source data pipeline that
chains transformations and writes to a store**: three strict layers, decorator auto-discovery, two-phase
execution, declarative config as first-class extension mechanism, LLM-assisted generation with hard
validation, per-run audit logs, and an embedded agent skill documenting how to extend it.

## 1. The three-layer split (types / tools / enrichers) — separation of concerns that holds

| layer | package | knows about | returns |
|---|---|---|---|
| **Types** | `flowsint-types` (39 built-in: Domain, Ip, Email, Individual, Breach, CryptoWallet…) | nothing external; pure Pydantic models + graph metadata | validated entities |
| **Tools** | `tools/` under enrichers pkg (subfinder, dnsx, naabu, httpx, whoisxml, sirene…) | one external utility/API each; NO types, NO graph | raw dicts/lists/strings |
| **Enrichers** | `flowsint_enrichers/<input_type>/to_<output>.py` (~52) | orchestration: tools + types + vault + graph | typed results + graph writes |

Rules that keep it honest (from their docs, enforced in practice):
- A tool wraps EXACTLY one external utility. "Don't combine multiple data sources in a single tool —
  that's what enrichers are for." Tools return plain Python structures; the *enricher* converts to types.
- Enricher file location encodes its contract: `<input_type_lower>/to_<target>.py`. Directory = input type.
- One escape hatch, explicitly named: `n8n/connector.py` with `InputType = Any / OutputType = Any` for
  user webhook workflows — the ONLY place `Any` is allowed as a type (their own skill doc lists it in anti-patterns).

**Portability**: this maps directly onto pipeline design — schema layer (pydantic models), source adapters
(one external system each, raw output), transformation jobs (typed I/O + side effects isolated to one phase).

## 2. Auto-discovery registry (no manual registration)

Both types and enrichers register via decorator at import time; discovery walks the package tree:

```python
# load_all_enrichers() — os.walk over the installed package path
for root, dirs, files in os.walk(package_path):
    dirs[:] = [d for d in dirs if not d.startswith("__pycache__")]   # prune in place
    ...
    for filename in files:
        if not filename.endswith(".py") or filename.startswith("_"): continue  # private modules skipped
        module_name = f"{module_prefix}.{filename[:-3]}"
        if module_name in sys.modules: continue                              # already imported
        try:
            importlib.import_module(module_name)   # triggers @flowsint_enricher decorators
        except Exception as e:
            print(f"Warning: Failed to import {module_name}: {e}", file=sys.stderr)  # WARN, don't fail
```

Properties worth copying verbatim:
- **Subdirs work without `__init__.py`** — os.walk + dotted module names; adding a new input-type dir needs zero plumbing.
- **Idempotent**: `_enrichers_loaded` global flag -> early return on second call (safe to invoke from multiple entry points).
- **One broken module must not kill discovery**: import errors are logged and skipped — an optional-dependency failure in one enricher can't hide the other 51. (Trade-off: a typo'd new file fails silently-ish; their troubleshooting doc says "restart API + check stderr".)
- Registry exposes `list()`, `list_by_categories()`, `list_by_input_type()` where input type `"any"` matches everything — this is what makes flows chainable by type compatibility.

## 3. Two-phase execution model (scan / postprocess) with strict params

Base-class contract (`enricher_base.py`):
- `execute(values)` = `async_init()` -> `preprocess(values)` [Pydantic TypeAdapter validation, invalid items skipped silently + one warning if ALL invalid] -> `await scan(preprocessed)` [pure data gathering — NO graph writes here] -> `postprocess(results, preprocessed)` [graph nodes/relationships only] -> `graph_service.flush()`.
- **Params are a strict model built at init**: `create_model("ParamsModel", __config__=ConfigDict(extra="forbid"), ...)` from the declared params schema — unknown param keys raise instead of being ignored. vaultSecret fields are deliberately optional in that model (deferred resolution; see cron-job-authoring/references/vault-crypto-pattern.md).
- `InputType`/`OutputType` are class attributes as **base types, not lists** (`Domain`, never `List[Domain]`) — the base generates JSON schemas via `TypeAdapter(...).json_schema()` and handles list wrapping. Schema generation even handles `$defs`/`$ref` indirection explicitly (nested-type case) with a documented fallback shape.
- Every exception in `execute` is caught, logged (`Logger.error`), and returns `[]` — one bad enricher can't take down its flow; the orchestrator records it as an error step instead.

**Portability**: "gather phase has no side effects / persist phase has no I/O" is a general pipeline invariant that makes each phase independently testable (their tests instantiate the enricher and call `scan()` directly — postprocess needs a graph, scan doesn't).

## 4. Graph write semantics (Neo4j) — two non-obvious facts from repository.py

- **MERGE key is `(nodeType, nodeLabel, sketch_id)`** — NOT the primary field:
  ```cypher
  MERGE (n:{type} { nodeLabel: $node_label, sketch_id: $sketch_id })
  ON CREATE SET n.created_at = $created_at
  SET n += $props            -- flat props with dotted keys; upsert merges properties
  SET n.deleted_at = null    -- soft-delete resurrection on re-creation
  ```
  Consequence (real, not theoretical): two distinct entities whose `compute_label()` collides in one sketch
  MERGE into the same node. Label design is a correctness concern, not cosmetics — their type docs spend a whole section on it for this reason.
- **Soft deletes everywhere**: relationship MATCH includes `WHERE from.deleted_at IS NULL`; re-creating sets `deleted_at = null` (resurrects). Bulk ops use `UNWIND $node_ids AS ...` batch queries; writes are buffered (`_batch_size = 100`, auto-flush when full, explicit flush at enricher end) and executed via `execute_batch`.
- Relationship MERGE is keyed on `(from_label, to_label, rel_label, sketch_id)` — re-running an enricher updates properties instead of duplicating edges (idempotent re-runs by construction).

## 5. Declarative YAML templates + LLM generation with a hard validation chain

The standout design: **an entire class of enrichers is data, not code**. A template declares input type/key,
HTTP request (`{{var}}` / `{{secrets.NAME}}` placeholders), response parsing (json/xml/text + dot-notation map,
optional array_path), output type, secrets list, retry config. `TemplateEnricher` executes them generically —
SSRF-guarded, URL-sanitized, vault-resolved (see devops/rest-api-client/references/ssrf-guard-and-outbound-http-hardening.md).

The LLM generator (`template_generator_service.py`) is a model of constrained code generation:
1. **System prompt = the full schema spec** + two worked YAML examples + explicit instruction "Output ONLY the
   YAML template. No explanations, no markdown fences."
2. **Schema constraints injected from user selection**: if input/output types were chosen in UI, their JSON schemas are appended with "The `response.map` keys MUST only use fields from this schema" — generation is *anchored to real type definitions*, not free-form.
3. **Post-hoc repair before validation** (two known LLM failure modes handled by regex): strip markdown fences; auto-quote unquoted `{{...}}` placeholders (`: {{x}}` -> `: "{{x}}"`, which would otherwise be invalid YAML). The prompt even warns the model about this ("Unquoted curly braces are invalid YAML") — belt and suspenders.
4. **Hard validation chain**: `yaml.safe_load` (not load) -> must be dict -> construct the Pydantic `Template(**parsed)` (frozen, extra="forbid" models throughout). Any failure raises ValidationError to the user with the reason; nothing unvalidated ever executes.

**Portability**: this is "LLM writes config that a strict validator gates before execution" — strictly better
than LLM-writes-code for any domain where behavior can be expressed declaratively (API integrations, ETL steps,
cron payloads). The pattern: schema-in-prompt + examples + output-only instruction + fence-strip/repair + safe parse + model validation.

## 6. Flow orchestration — per-run JSON audit log with input caching

`FlowOrchestrator` chains enrichers (output of one = input of next, branches supported). Its execution record
is a **JSON file written incrementally** (`enricher_logs/enricher_execution_<sketch>_<scan>.json`) containing:
initial config snapshot, per-step entries (inputs/outputs serialized via `to_json_serializable`, status running->completed/error, error text, timestamp, `execution_time_ms`), a rolling summary block, and final results + reference mapping.

- **Cache key = `f"{node_id}:{str(enricher_inputs)}"`** — same enricher node with identical inputs is never
  re-executed within one flow run (`cache_hit: true` recorded in the log). Cheap memoization that makes
  diamond-shaped flows (two branches converging on the same upstream) free.
- **Fail-fast**: any step error writes its entry and `return results` immediately — no partial downstream execution; status fields make the failure point obvious from the file alone.
- Execution-log updates are read-modify-write of the JSON per step (fine at this scale; note it as a known shape, not best practice for high throughput).

## 7. The embedded agent skill (.claude/skills/flowsint-enricher-builder/SKILL.md) — anatomy worth stealing

The repo ships a Claude Code skill teaching agents to build new enrichers. Structure (178 lines):
- **Opening doctrine**: "You do not memorize the catalog — you know where to look and how the pieces fit. Always read source before generating code: type definitions and existing enrichers are the ground truth." -> followed by an *authoritative source paths table* (what | path) for every relevant file.
- **Decision tree BEFORE code**: "new type or reuse?" — list entities involved, open candidate type files, then Reuse / Extend-existing-type / Create-new with explicit criteria ("different primary key, different label semantics, different graph role"). "Never cram data into a wrong type." Surface the decision to the user before generating.
- **Anatomy + conventions**: minimum enricher skeleton, file-location rule, naming rules (`<input>_to_<output>`, UPPER_SNAKE_CASE relationship verbs), and an explicit *known smell* ("category() strings are inconsistent in source — match what's already used in that directory; don't introduce a third variant").
- **Workflow numbered 1–11** per request (read goal -> open candidates -> decide -> copy closest existing enricher as template -> check tools/ for an existing wrapper -> params schema -> scan with try/except per item -> postprocess -> exports -> tests -> restart).
- **"Anti-patterns — refuse to generate these"** list: hardcoded keys, manual node dicts, silently swallowed exceptions (`every except must log`), hand-casting strings the base class already validates, editing registry.py manually.
- **Closing**: "When the user is wrong" — push back with evidence (show existing fields, explain mismatch, propose cleaner alternative). Don't generate the bad version.

This is a template for any *extension-builder skill*: source-paths table + decide-before-code tree + conventions-with-known-smells + numbered workflow + refuse-list + push-back clause. (See hermes-agent-skill-authoring/references/behavioral-skill-testing.md for how to test discipline skills like this.)

## 8. Docker-tool wrapper patterns (tools/dockertool.py)

- `TERM=dumb` in container env — avoids TTY-related hangs from tools that detect a terminal.
- Every run: `remove=True, detach=False, tty=False, network_mode="bridge", stdin_open=False`.
- **Diagnostic re-run trick**: on DockerException containing "returned non-zero exit status", immediately re-run the identical command and return its output if it succeeds — catches transient daemon hiccups AND surfaces real stdout/stderr for genuine failures. (Unusual; use with care, but clever.)
- `version()` probes by running `--version` in a throwaway container; subfinder's override documents why: "subfinder requires input even when checking version, so we provide a dummy domain" — tool quirks get documented at the call site.
- Output parsing is defensive per-tool (e.g. subfinder filters results through `is_valid_domain(sub) and sub.endswith(domain)` to drop scanner noise), dedupes with a set, returns plain lists.

## 9. Test conventions for pipeline components

Their enricher tests follow a fixed shape: (1) metadata test — name/category/key constants; (2) type-definition
test — InputType/OutputType identity against the types package; (3) one happy-path `scan()` call with a real or
mocked input asserting result count + instance types. Docker-dependent tool tests are isolated behind
`@pytest.mark.docker`. Types get creation/validation/boundary/label-computation/serialization test batteries
(label tested for full, partial-None, and minimal-field cases — because label collisions are graph-correctness bugs).

## 10. Recurring bug classes visible in their PR history (audit checklist)

From ~45 recent merged/closed PRs: naive-vs-aware datetimes (~8 separate fixes across core services/auth/logs),
object-level authz missing on one resource type while others had it, UTF-8 assumptions on social-API outputs,
YAML files read without explicit encoding, Celery/Neo4j healthcheck timeouts too tight for cold starts,
nginx `add_header` inheritance dropping security headers (replace-all semantics). If you audit a similar codebase, grep for: `datetime.now()` without tzinfo; endpoints that check auth but not ownership; `.read()` on text files without encoding=; container healthchecks with default 3s/5s windows.
