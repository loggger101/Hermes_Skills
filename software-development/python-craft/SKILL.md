---
name: python-craft
description: "Python craft: style, typing, patterns, testing, packaging."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [python, coding-style, typing, patterns, testing, packaging, maintainability, best-practices]
    category: software-development
    related_skills: [test-driven-development, requesting-code-review, systematic-debugging, simplify-code]

---

# Python Craft

Guide for writing Python that holds up under review, across engineers, and over time. Covers style, typing, common patterns, testing approach, and packaging. Not a tutorial — assume Python competency; focus on what separates "works" from "good."


## What This Skill Does

Python craft: style, typing, patterns, testing, packaging.

## When to Use

- Starting a new Python project and want a style/pattern baseline
- Reviewing Python code and need a reference for what to flag
- Refactoring Python that's grown awkward
- Setting up a project's linting, typing, and testing toolchain

## Toolchain Defaults

| Concern | Tool | Why |
|---|---|---|
| Formatting | `ruff format` (or `black`) | Deterministic, zero debate |
| Linting | `ruff check` | Fast, replaces flake8/isort/pylint for most projects |
| Type checking | `mypy --strict` (or `--ignore-missing-imports`) | Catches whole classes of bugs; strict is the goal |
| Testing | `pytest` | fixture model, parametrize, no boilerplate |
| Coverage | `pytest --cov` + `coverage` | Know what you're not testing |
| Pre-commit | `pre-commit` framework | Run lint/format/type on commit, not after |

```bash
pip install ruff mypy pytest pytest-cov pre-commit
```

### Ruff config (pyproject.toml)

Pin the Ruff version in your pre-commit config and update it periodically — Ruff ships new rules frequently, and an unpinned install can change behavior across machines.

```toml

### Mypy config

```toml
[tool.mypy]
python_version = "3.11"
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
```

Start permissive if the codebase isn't typed yet; tighten over time. The goal is `disallow_untyped_defs = true` eventually.

### Pre-commit config (.pre-commit-config.yaml)

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff-format
      - id: ruff-check
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-PyYAML]
```

```bash
pre-commit install
```

## Style

### Indentation and line length

- 4 spaces, no tabs.
- 100 chars soft limit. Break lines before a binary operator:
  ```python
  result = (some_long_function(argument_one, argument_two)
            + another_value
            - final_thing)
  ```
- Wrap docstrings at 72 chars for CLI readability.

### Imports

- Standard library first, third-party second, local app third. Blank line between groups.
- `ruff` with `I` (isort) selected handles this automatically.
- No wildcard imports (`from module import *`).
- Avoid circular imports — extract shared bits.

### Naming

| Thing | Convention | Example |
|---|---|---|
| Module / file | `snake_case.py` | `user_service.py` |
| Function / method | `snake_case` | `get_user_by_id` |
| Variable | `snake_case` | `active_users` |
| Constant | `UPPER_SNAKE` | `MAX_RETRIES` |
| Class | `PascalCase` | `UserProfile` |
| Exception | `PascalCase` ending in `Error` | `ValidationError` |
| Private / internal | leading underscore | `_internal_cache` |

A single leading `_` signals "implementation detail, don't depend on it" — it's still public API. Name mangling (`__name`) is rare and usually signals confused class hierarchy. Prefer composition.

### Type hints

Type hints are part of the function signature, not decoration. Add them to all new code. For existing code, add as you touch functions.

```python
from typing import Any

def get_user(user_id: int, include_deleted: bool = False) -> User | None:
    ...

def process_batch(items: collections.abc.Sequence[Item]) -> list[Result]:
    ...

def log_event(event: object) -> None:
    ...
```

- Prefer `X | None` over `Optional[X]`.
- Prefer `collections.abc` abstracts over concrete types for parameters (`Sequence`, `Mapping`, `Iterable`) unless you need mutability.
- Avoid `Any` unless genuinely unconstrained — it silences mypy.
- Return types and parameter types are mandatory in new code. Local variable types can be omitted when obvious from assignment — but function signatures must be fully typed.

### Docstrings

Google-style is slightly more readable in most editors.

```python
def fetch_users(
    limit: int = 100,
    offset: int = 0,
    *,
    active_only: bool = True,
) -> list[User]:
    """Fetch users from the API with pagination.

    Args:
        limit: Maximum users to return. Must be > 0.
        offset: Number of users to skip.
        active_only: If True, exclude deactivated users.

    Returns:
        A list of User objects. May be empty.

    Raises:
        ValueError: If limit <= 0.
        APIError: If the upstream service is unavailable.
    """
```

- Document args, returns, and raises for public functions.
- Document the *why* for non-obvious behavior — the signature tells what, the docstring tells why.
- Keep one-line summaries short and imperative ("Fetch users", not "This function fetches users").

## Patterns

### Functions over classes (by default)

Prefer plain functions and dataclasses over class hierarchies unless you have a real reason for polymorphism.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class User:
    id: int
    name: str
    email: str

def normalize_user(raw: dict[str, object]) -> User:
    return User(
        id=int(raw["id"]),
        name=str(raw["name"]).strip(),
        email=str(raw["email"]).lower(),
    )
```

### dataclasses for data containers

Use `dataclass` for anything that's mostly data with a bit of behavior. Gives `__init__`, `__repr__`, `__eq__`, and a clear field list for free.

```python
@dataclass(frozen=True)
class Config:
    host: str
    port: int
    timeout: float = 30.0
```

- `frozen=True` makes the object hashable and prevents accidental mutation. Use it unless you have a reason not to.
- For validation, use `__post_init__` or a factory function.

### Named tuples vs dataclasses

- `NamedTuple` for lightweight, immutable, tuple-like records where you want index access too.
- `dataclass` when you want defaults, validation, or methods.
- Don't use plain `tuple` for structured data with more than 2 fields — readability trap.

### Context managers for resource handling

Always use `with` for resources that need cleanup. Write custom context managers with `contextlib.contextmanager` or a `__enter__`/`__exit__` class.

```python
from contextlib import contextmanager
from pathlib import Path

@contextmanager
def temporary_file(path: str):
    Path(path).touch()
    try:
        yield path
    finally:
        Path(path).unlink(missing_ok=True)

with temporary_file("/tmp/scratch.txt") as p:
    do_something(p)
# automatically cleaned up
```

### Avoid mutable default arguments

The classic gotcha.

```python
# WRONG
def add_item(item: str, items: list[str] = []) -> list[str]:
    items.append(item)
    return items

# RIGHT
def add_item(item: str, items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    items.append(item)
    return items
```

### Comprehensions over explicit loops (when readable)

```python
# Good
squared = [x ** 2 for x in numbers if x > 0]

# Overused — when nested or complex, use a loop
result = [
    transform(x, y)
    for x in xs
    for y in ys
    if predicate(x, y)
    and not some_side_condition(x)
]
```

If a comprehension needs a comment to explain it, use a loop.

### Generator expressions for large data

```python
# Memory-efficient
total = sum(x ** 2 for x in huge_sequence if x > 0)
```

### Error handling

- Fail fast. Raise on invalid input at the boundary, not deep in the call stack.
- Use specific exceptions, not bare `Exception`.
- Don't silently swallow exceptions. If you catch and continue, log why.
- Custom exceptions live in the module that defines the error condition, not a generic `errors.py` dumping ground.

```python
class ConfigurationError(Exception):
    """Raised when configuration is missing required fields."""

def load_config(path: str) -> Config:
    raw = read_yaml(path)
    if "host" not in raw:
        raise ConfigurationError(f"Missing 'host' in {path}")
    return Config(host=raw["host"], port=raw.get("port", 8080))
```

### Avoid global state

Globals make code hard to test and reason about. Pass state explicitly.

```python
# BAD
_cache = {}
def get_cached(key: str) -> object:
    if key not in _cache:
        _cache[key] = compute(key)
    return _cache[key]

# GOOD
class Cache:
    def __init__(self):
        self._store: dict[str, object] = {}
    def get(self, key: str, compute: Callable[[str], object]) -> object:
        if key not in self._store:
            self._store[key] = compute(key)
        return self._store[key]
```

### Dependency injection over importing modules directly

Makes testing possible without mocking modules.

```python
# BAD — hard to test without patching the import
import db
def get_user(id: int) -> User:
    return db.fetch_user(id)

# GOOD — injectable
def get_user(id: int, fetch: Callable[[int], User] = db.fetch_user) -> User:
    return fetch(id)

# In tests:
get_user(42, fetch=lambda id: User(id=id, name="test"))
```

### pathlib over os.path

```python
from pathlib import Path

data_dir = Path("data")
config_path = data_dir / "config" / "settings.yaml"
if config_path.exists():
    raw = config_path.read_text()
```

**Windows gotcha:** `os.path.relpath` on Windows produces backslash-separated strings that silently fail comparison against forward-slash strings (JSON skill refs, regex patterns, substring filters). Always normalize with `str(p).replace('\\', '/')` before substring matching, or prefer `pathlib.Path` throughout and convert at comparison boundaries. See `references/windows-path-separator-trap.md` for the reproduction recipe and fix.

## Testing Approach

See `test-driven-development` for RED-GREEN-REFACTOR discipline. This section covers Python-specific testing craft.

### pytest basics

```python
import pytest
from myapp import add, divide

def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_divide_by_zero_raises():
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)
```

### Parametrize for data-driven tests

```python
@pytest.mark.parametrize(
    "a, b, expected",
    [(1, 2, 3), (-1, 1, 0), (0, 0, 0), (1000000, 1, 1000001)],
)
def test_add(a: int, b: int, expected: int):
    assert add(a, b) == expected
```

### Fixtures for setup

```python
@pytest.fixture
def sample_user() -> User:
    return User(id=1, name="Test User", email="test@example.com")

def test_user_email_lowercase(sample_user: User):
    assert sample_user.email == "test@example.com"
```

- Keep fixtures focused. A fixture that sets up 15 things is doing too much.
- Use `scope` only when needed (`scope="session"` for expensive shared setup).

### Test naming

Test names describe behavior, not implementation.

```python
# GOOD
def test_returns_empty_list_when_no_matches():
    ...

# BAD
def test_filter_function():           # what does it do?
def test_filter_returns_list():      # vague
```

### What to test

- Public API behavior, not private implementation.
- Happy path + error paths + edge cases (empty input, None, large input, boundary values).
- Integration points: does the function actually call the dependency correctly?
- Pure functions: test exhaustively. Side-effecting code: test the effect, not internals.

### What NOT to test

- Python itself (don't test that `+` adds integers).
- Implementation details that change when you refactor (private method return values, internal state).
- Third-party library behavior (test that you called it correctly, not that it works).

### Test organization

```
project/
  src/myapp/
    __init__.py
    core.py
    api.py
  tests/
    conftest.py          # shared fixtures
    test_core.py
    test_api.py
    fixtures/            # test data files
```

One test file per module, named `test_<module>.py`. Group test functions by behavior within the file.

### Coverage

Run with `pytest --cov=myapp --cov-report=term-missing`. Target 80%+ on new code. Don't chase 100% — not worth it for trivial getters/setters. Look at *what's missing*, not the percentage.

### Mocking

- Mock at the boundary, not inside the function. Inject dependencies, then pass a mock.
- `unittest.mock` or `pytest-mock`. Prefer `pytest-mock`'s `mocker` fixture.
- Don't mock what you don't own without a wrapper — wrap third-party calls in your own function, mock the wrapper.

```python
def test_send_notification_calls_gateway(mocker):
    gateway = mocker.Mock()
    gateway.send.return_value = True
    result = send_notification("user@example.com", gateway=gateway)
    gateway.send.assert_called_once_with("user@example.com", subject="Hello")
    assert result is True
```

## Packaging

### Project layout

```
myproject/
  pyproject.toml          # build system + metadata + tool config
  src/
    myproject/            # importable as `import myproject`
      __init__.py
      core.py
      cli.py
  tests/
  README.md
  LICENSE
```

`src/` layout avoids import confusion during development (can't accidentally import the local directory instead of the installed package).

### pyproject.toml

Modern Python uses `pyproject.toml` for everything — build system, metadata, dependencies, tool config.

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "myproject"
version = "0.1.0"
description = "What this does"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.11"
dependencies = [
    "requests>=2.28",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "ruff",
    "mypy",
    "pytest",
    "pytest-cov",
    "pre-commit",
]

[project.scripts]
mycli = "myproject.cli:main"

[tool.ruff]
# ... ruff config ...

[tool.mypy]
# ... mypy config ...
```

### Dependency management

- Pin direct dependencies with a minimum version (`requests>=2.28`), not an exact pin, unless specific reason.
- Use a lock file for reproducible environments: `uv pip compile` or `pip-compile` from pip-tools.
- Keep dev dependencies separate (`project.optional-dependencies.dev`).
- Don't commit virtual environments. Commit `pyproject.toml` and optionally a `requirements.txt` / `uv.lock`.

### Versioning

- SemVer: `MAJOR.MINOR.PATCH`.
- `0.x.y` = API unstable. `1.0.0` = committing to backward compatibility.
- Bump patch for bug fixes, minor for new features (backward-compatible), major for breaking changes.
- Put the version in one place only — `pyproject.toml` — and read it at runtime from package metadata if needed, not from a duplicated `_version.py`.

### Publishing

- Build with `python -m build` (needs `build` package).
- Upload with `twine upload dist/*` or `uv publish`.
- Test the distribution locally before publishing: `pip install dist/myproject-0.1.0.tar.gz` in a fresh venv.

## Common Code Smells in Python

| Smell | What it looks like | Fix |
|---|---|---|
| God object | One class with 30 methods, 15 responsibilities | Split by responsibility |
| God function | One function that does 5 things in sequence | Extract each step |
| Comments explaining what | `# increment i` above `i += 1` | Delete the comment |
| Comments explaining why (good) | `# We retry because API is eventually consistent` | Keep — useful context |
| Stringly-typed | Passing `"admin"` / `"user"` as strings | Use `enum.Enum` or module constants |
| Boolean flag param | `def process(data, dry_run=False)` | Split into two functions or use a strategy |
| Deep nesting | 4-level if/else pyramid | Early returns, guard clauses, extract |
| Mutable class attributes | `class Foo: items = []` (shared across instances) | Move to `__init__` |
| Path comparison without normalization | `os.path.relpath` on Windows yields backslashes; comparing against forward-slash strings silently fails | Normalize with `str(p).replace('\\', '/')` before substring matching; prefer `pathlib.Path` throughout |
| Star import | `from module import *` | Import what you use explicitly |
| Bare except | `except: pass` | Catch specific exceptions at minimum |
| No type hints on public API | `def get(x): ...` | Add types to the signature |
| Copy-paste with tiny variation | 3 functions differing in one line | Extract common part, pass variant as param |
| Reinventing stdlib | Hand-rolled JSON parser, custom LRU cache | Use `json`, `functools.lru_cache`, `collections` |

## Verification Checklist

For new Python code:

- [ ] Formatted with `ruff format` (or black)
- [ ] Lint-clean with `ruff check` (or equivalent)
- [ ] Type-checked with mypy (no new untyped defs in public API)
- [ ] Public functions have docstrings (args, returns, raises)
- [ ] No mutable default arguments
- [ ] No wildcard imports
- [ ] No bare `except` or `except: pass`
- [ ] Tests exist for the new behavior (happy path + error paths)
- [ ] Tests are parametrized where data-driven
- [ ] No new global mutable state
- [ ] Dependencies injected where they need to be mocked in tests
- [ ] `pyproject.toml` updated if new direct dependency added
- [ ] Version bumped if publishing
