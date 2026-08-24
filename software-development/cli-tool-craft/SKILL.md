---
name: cli-tool-craft
description: "CLI tools: subcommands, config validation, env substitution."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [CLI, argparse, subcommands, config-validation, env-substitution, config-inheritance, click, typer]
    category: software-development
    related_skills: [python-craft]
---

# CLI Tool Craft

Practical guide for building CLI tools that are pleasant to use and easy to maintain — subcommand patterns, config systems with validation and inheritance, environment variable substitution, output formatting, testing, and the common mistakes that make CLIs frustrating.

## When to Use

- Building a command-line tool for a pipeline, training system, data processing workflow, or dev utility
- Adding subcommands to an existing script that's grown too many flags
- Designing a config system that supports validation, defaults, inheritance, and environment substitution
- Making a CLI testable and discoverable (help text, error messages, consistent output)

**Don't use** a CLI when a GUI/dashboard is the primary interface (use Streamlit or a web UI), or when the tool is a one-off script that will never be reused. CLIs are for repeated command-line use by someone (possibly future-you) who wants help text, sensible errors, and predictable behavior.

## Subcommand Patterns

### Why subcommands

A script that grows flags for every operation becomes unreadable: `script.py --train --config x --export --format onnx --population 200 --opponent balanced --gens 100`. Subcommands group related operations: `crp train --config x --gens 100`, `crp export --format onnx`, `crp tournament --opponent balanced`. Each subcommand has its own flags; unrelated flags don't clutter each other.

### argparse subcommands

```python
import argparse

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="crp", description="Clash Royale pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # train
    train_p = subparsers.add_parser("train", help="Run evolution training")
    train_p.add_argument("--config", default="default.yaml")
    train_p.add_argument("--gens", type=int, default=100)
    train_p.add_argument("--pop", type=int, default=200, dest="population")
    train_p.add_argument("--resume", default=None)

    # export
    export_p = subparsers.add_parser("export", help="Export a model")
    export_p.add_argument("run_dir", help="Path to run directory")
    export_p.add_argument("--format", choices=["onnx", "torchscript", "numpy", "json"], default="numpy")
    export_p.add_argument("--output", "-o", default=None)

    # tournament
    tour_p = subparsers.add_parser("tournament", help="Run a tournament")
    tour_p.add_argument("--opponent", default="balanced")
    tour_p.add_argument("--agents", type=int, default=200)
    tour_p.add_argument("--format", choices=["swiss", "round_robin", "single_elim"], default="swiss")

    return parser
```

### Pattern: parse, dispatch

```python
def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "train":
        run_training(config_path=args.config, generations=args.gens, population=args.population, resume=args.resume)
    elif args.command == "export":
        export_model(args.run_dir, format=args.format, output=args.output)
    elif args.command == "tournament":
        run_tournament(opponent=args.opponent, agents=args.agents, format=args.format)
```

Keep `main()` thin — parse, dispatch, done. Each subcommand function is its own thing.

### Alternatives to argparse

- **click**: decorator-based, good for nested commands and complex option interactions. More concise for multi-command tools.
- **typer**: typed, modern, built on click. Good if you want type hints to drive the CLI.
- **argparse**: standard library, no dependency, fine for most tools. Use it unless you have a reason to reach for click/typer.

For a tool with 10+ subcommands, click/typer's decorator style is cleaner than argparse's builder style. For a tool with 2–5 subcommands, argparse is fine and has zero dependencies.

## Config Systems

A good config system for a pipeline tool handles:

1. **Schema/validation** — catch bad config early, with clear errors.
2. **Defaults** — sensible defaults so the user doesn't have to specify everything.
3. **Inheritance** — base configs that specific configs extend (e.g., a "balanced" opponent preset that other opponents build on).
4. **Environment variable substitution** — `${VAR:-default}` so secrets and machine-specific paths stay out of the config file.
5. **Clear error messages** — when config is wrong, tell the user what and where.

### Schema-based validation

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class TrainingConfig:
    population: int = 200
    generations: int = 100
    mutation_rate: float = 0.1
    opponent: str = "balanced"
    resume: Optional[str] = None

    def validate(self):
        if self.population < 10:
            raise ConfigError(f"population must be >= 10, got {self.population}")
        if self.generations < 1:
            raise ConfigError(f"generations must be >= 1, got {self.generations}")
        if not 0 < self.mutation_rate < 1:
            raise ConfigError(f"mutation_rate must be in (0, 1), got {self.mutation_rate}")
```

Validate after loading, before using. Catch the error at config load time, not three hours into a training run.

### Config loading with env substitution

```python
import os, re

def substitute_env(value: str) -> str:
    """Replace ${VAR:-default} with env var or default."""
    pattern = re.compile(r'\$\{([^}:]+)(?::-([^}]*))?\}')
    def replacer(m):
        var = m.group(1)
        default = m.group(2) or ""
        return os.environ.get(var, default)
    return pattern.sub(replacer, value)

def load_config(path: str) -> dict:
    with open(path) as f:
        raw = yaml.safe_load(f)
    # Substitute env vars in all string values recursively
    return substitute_in_place(raw)
```

This lets a config say `zoho_client_secret: ${ZOHO_CLIENT_SECRET}` and have it resolved at load time, keeping secrets out of the file.

### Config inheritance via `_base`

```yaml
# configs/opponents/base.yaml
_categories:
  - name: balanced
    deck: [log, barbarians, skeleton,...
```

```yaml
# configs/opponents/balanced.yaml
_base: opponent_base
population: 200
mutation_rate: 0.1
```

```python
def load_config_with_inheritance(path: str) -> dict:
    raw = load_config(path)
    base_path = raw.pop("_base", None)
    if base_path:
        base = load_config(f"configs/{base_path}.yaml")
        # Child overrides base
        result = deep_merge(base, raw)
    else:
        result = raw
    return result
```

Inheritance lets you define a shared base (opponent profiles, default hyperparameters, feature config) and have specific configs extend it. The child's values override the base's. Document the inheritance chain in the config or the help text.

### Config discovery

For a tool with many configs, make them discoverable:

```python
def list_configs(config_dir: str, pattern: str = "*.yaml") -> list[str]:
    return sorted(Path(config_dir).glob(pattern))
```

A `crp configs` subcommand that lists available configs with a one-line description is much better than telling users to read the filesystem.

## Output and Feedback

### Progress for long-running operations

```python
import time

def train_with_progress(generations):
    for gen in range(generations):
        # ... do generation ...
        if gen % 10 == 0 or gen == generations - 1:
            print(f"Generation {gen+1}/{generations}: best fitness {best_fitness:.3f}")
```

For very long runs, a progress bar (`tqdm`) is nicer than periodic prints. For CI/log output, periodic prints are better than a progress bar (progress bars don't log well).

### Structured vs human output

- **Human output**: readable reports, progress, summary tables. For interactive use.
- **Structured output**: JSON, CSV, or a machine-readable format. For piping into other tools, CI, or post-processing.

A tool can offer both: a `--json` flag that switches output to JSON, or a `report` subcommand that produces a structured report file alongside the human-readable console output.

### Error messages

- Say what went wrong, where, and what to do about it.
- Bad: `Error: invalid config`
- Good: `Config error in opponents/balanced.yaml line 12: 'deck' must be a list of card names, got 'logbarbarian'. Available cards: see assets/card_data.json`
- Include the config path, the key, the expected type/values, and what was found.

## Testing CLIs

### What to test

- Each subcommand runs with sensible defaults and produces the expected output.
- Each subcommand fails clearly on bad input (missing required arg, invalid config, bad path).
- Config validation catches bad values with clear errors.
- Help text is present and accurate (`--help` on each subcommand).
- Environment variable substitution works and falls back to defaults.

### How to test

```python
def test_train_defaults(run_dir, tmp_path):
    result = subprocess.run(
        ["crp", "train", "--config", "default.yaml", "--gens", "2", "--pop", "10"],
        capture_output=True, text=True, cwd=run_dir
    )
    assert result.returncode == 0
    assert "Generation" in result.stdout
    # Check that output files were created
    assert (tmp_path / "latest.pth").exists()
```

Run the CLI as a subprocess — that tests the actual entry point, not an internal function. It catches entry-point bugs (arg parsing, dispatch) that unit-testing the internal functions misses.

### Deterministic tests

For CLI tools that run pipelines (training, simulation, data processing), make the test config deterministic:
- Small population, few generations, fixed seed.
- Cheap evaluation (a mock environment, or a tiny real one).
- Assert on structure (files created, output contains expected keys) rather than exact values that might drift.

## Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| One script with 30 flags | Unreadable, flags interact confusingly | Use subcommands to group operations |
| Bad config fails late (hours into a run) | Wasted time, frustrating | Validate config at load time, before using |
| Secrets in config files | Accidental commit, exposure | Use env var substitution, keep secrets in env |
| No help text or stale help | User doesn't know how to use it | Keep `--help` accurate; test it |
| Cryptic error messages | User can't fix the problem | Say what, where, and how to fix |
| CLI not testable | Bugs slip through | Test via subprocess; use small deterministic configs |
| No config discovery | User doesn't know what configs exist | List configs in a subcommand or help text |
| Output not machine-readable | Can't pipe into other tools | Offer `--json` or a structured report subcommand |
| Progress bar in CI logs | Polluted logs, unclear failures | Use periodic prints for CI; progress bars for interactive |
| Subcommand required but not enforced | Runs with no args, does nothing or wrong thing | `required=True` on subparsers, or explicit check |

## Verification Checklist

Before shipping a CLI tool:

- [ ] Each subcommand has `--help` with accurate description and args
- [ ] Required args are enforced; missing args give clear errors
- [ ] Config is validated at load time with clear error messages
- [ ] Secrets use env var substitution, not hardcoded in config
- [ ] Config inheritance is documented and works (child overrides base correctly)
- [ ] Long-running ops show progress (periodic prints or progress bar)
- [ ] Structured output available for CI/pipe use (`--json` or report subcommand)
- [ ] CLI is tested via subprocess (entry point, not just internal functions)
- [ ] Error messages say what went wrong, where, and how to fix
- [ ] Configs are discoverable (list subcommand or documented)
