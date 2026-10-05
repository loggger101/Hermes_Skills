---
description: "Pydantic 2.13.5 on Python 3.14: what lax mode accepts from LLM-style input, Optional-is-required, extras ignored, model_copy/construct/assignment skip validation, exclude_unset, union smart mode, inf to null"
source_repo: pydantic/pydantic (MIT); contribution AI policy from its CONTRIBUTING.md
tested_version: "pydantic 2.13.5 + pydantic-core 2.46.5 on Python 3.14.6 (Windows, uv venv); about 40 one-call checks, warnings forced on. Validators run in both before and after modes; Settings, dataclasses, TypedDict and custom types were not exercised"
verified_date: "2026-10-05"
---

# Pydantic v2 validation behaviour, as seen by LLM-output code

`SKILL.md` builds on Pydantic models (via instructor). These are the defaults that decide whether a malformed model reply is
accepted, silently coerced, or rejected. Each line is one call.

## What lax mode accepts (the default)

| Input -> field | Result |
|---|---|
| `"5"` -> `int` | `5` |
| `5.0` -> `int` | `5`; `5.5` -> **error** `int_from_float` |
| `True` -> `int` | `1` (a bool is accepted as an int) |
| `5` -> `str` | **error** `string_type` (v2 no longer stringifies numbers) |
| `"yes"`, `"on"`, `"1"` -> `bool` | `True`; `2` and `"maybe"` -> error `bool_parsing` |
| `"nan"`, `"inf"` -> `float` | accepted (`nan`, `inf`) |
| epoch seconds `1791204444` and milliseconds `1791204444000` -> `datetime` | both parse to `2026-10-05T12:47:24+00:00` (magnitude-guessed) |
| `0.1` (float) -> `Decimal` | `Decimal('0.1')` (goes through `str`) |
| `"2026-10-05"` -> `date` | same result via `model_validate` and `model_validate_json` |
| `Literal['a','b']` given `'c'` | error `literal_error` |

`model_validate(data, strict=True)` rejects `"5"` for `int` (`int_type`); `StrictInt` rejects `True` too. For LLM output,
lax mode is usually what you want for ints and bools, but it also means `"yes"` becomes `True` without complaint: use
`Literal` or `StrictBool` where the exact token matters.

## Defaults that surprise

| Case | Behaviour |
|---|---|
| Unknown extra keys | **ignored silently** (`M(zzz=1)` dumps without it). `ConfigDict(extra="forbid")` turns a typo (`aa=2`) into `extra_forbidden` |
| `Optional[int]` with no default | **required** in v2: `Opt()` fails with `missing`. Write `= None` |
| Mutable defaults (`items: list[int] = []`) | copied per instance (`[1]` vs `[]`): safe in Pydantic, unlike plain classes |
| `Union[int, str]` | smart mode keeps the exact type: `"5"` stays `'5'`, `5` stays `5`; `Union[str, int]` with `5` also stays `5` |
| JSON dump of `inf` / `nan` | serialised as **`null`** (`{"f":null}`), so a round trip loses the value |
| Field named `copy` | allowed but warns that it shadows a `BaseModel` attribute; a field named `model_name` raised no warning in 2.13 |

## Operations that skip validation

| Call | Result |
|---|---|
| `Model(...).model_copy(update={'age': 'not-an-int'})` | no validation: `age == 'not-an-int'` |
| `Model.model_construct(name=5)` | no validation: `name == 5` |
| `m.age = 'oops'` | accepted by default; with `ConfigDict(validate_assignment=True)` it raises `int_parsing` |

If a value came from a model reply, re-validate with `Model.model_validate(m.model_dump())` after any `model_copy(update=...)`.

## Dumps and partial writes

| Call on `User(name='a')` (fields `email: Optional[str] = None`, `age: int = 0`) | Result |
|---|---|
| `model_dump()` | `{'name': 'a', 'email': None, 'age': 0}` (defaults written) |
| `model_dump(exclude_unset=True)` | `{'name': 'a'}` (only what the caller provided) |
| `User(name='a', email=None).model_dump(exclude_unset=True)` | `{'name': 'a', 'email': None}`: an explicit `None` **counts as set** |
| `model_dump(exclude_none=True)` | drops every `None`, including ones the caller set deliberately |

This is the partial-write trap behind flowsint's 2026-09-20 fix (an upsert that wrote unset fields as null): for PATCH or upsert
use `exclude_unset=True`, and decide explicitly whether `None` means "clear" or "absent".

## Validators and errors

- A `mode="before"` validator can coerce (`"7"` -> `7`) and the normal one then runs; an after-validator raising `ValueError`
  becomes a `ValidationError` with type `value_error`; `AssertionError` gives `assertion_error`.
- `ValidationError.errors()` entries carry `loc`, `type` and `msg`; `error_count()` is the number of errors. These are what
  instructor feeds back to the model on retry, so name fields and write messages a model can act on.
- `@computed_field` on a property **requires a return type annotation** (`PydanticUserError` otherwise).
- `M.model_json_schema()` returns a plain JSON-Schema dict (`properties`, `required`, `title`, `type`).

## Contributing to pydantic

Its `CONTRIBUTING.md` has an "AI policy": AI use is welcome if you certify you understand the code; PRs may be closed for
quality, mass submission across repositories, or incoherent AI-written descriptions. See
`github/agent-oss-contributions/references/ai-policies-of-starred-repos.md`.

Not run: pydantic-settings, dataclass/TypedDict adapters, discriminated unions, generics, performance, v1 compatibility.
