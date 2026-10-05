---
description: "Python logging with loguru 0.7.3: setup, brace-format traps, diagnose=True secret leak, rotation/retention, serialize, stdlib interception"
source_repo: Delgan/loguru (MIT)
tested_version: loguru 0.7.3 (pip --target, Windows, Python 3.14); every behaviour below was run, none is from the README alone
verified_date: "2026-10-05"
---

# Logging with loguru

`loguru` replaces the `logging` handler/formatter/logger boilerplate with one global `logger`. Use it for scripts, CLIs and
services you own; for a **library** other people import, use the stdlib `logging` so you do not impose a sink on them.

## Minimal setup

```python
import sys
from loguru import logger

logger.remove()                                           # drop the default stderr sink (id 0) before adding your own
logger.add(sys.stderr, level="INFO", colorize=False)      # explicit sink
logger.add("app_{time:YYYY-MM-DD}.log", rotation="10 MB", retention=5, compression="zip",
           enqueue=True, level="DEBUG", diagnose=False, backtrace=True)
```

- The default sink is stderr at DEBUG with ANSI colours. In a captured (non-tty) Windows subprocess it **still emitted colour codes**,
  so pass `colorize=False` on any sink whose output an agent, CI log or file reader will parse.
- File sinks write UTF-8 (a log line with an em dash and an arrow round-tripped correctly on Windows).
- Rotation + retention + compression worked: 60 lines of ~65 bytes with `rotation="1 KB", retention=2, compression="zip"` left the live
  `a_2026.log` plus exactly two `.log.zip` archives. `enqueue=True` makes sinks safe across threads and processes; call `logger.complete()` before exit
  to flush the queue.

## Traps (all reproduced)

1. **Braces + arguments raise.** `logger.info("literal {braces} no args")` logs literally, but as soon as you pass any argument the message is
   `str.format`-ed: `logger.info("with arg {braces}", 5)` raises `KeyError: 'braces'`. An f-string whose result contains braces
   (a dict repr) plus an argument raises too: `logger.info(f"state {d}", 1)` -> `KeyError: "'a'"`. The logging call itself crashes, which is
   worse than losing a line. Either use `{}` placeholders with args (`logger.info("state {}", d)`), pass no args with an f-string, or double
   literal braces (`{{`, `}}`).
2. **`diagnose=True` writes local variable values into the traceback**, including secrets. With a function `f(secret_token)` called as `f(secret)`
   the log contained the token value; with `diagnose=False` it did not. The default is `True`, so set `diagnose=False` on every sink that leaves
   your machine or lands in a shared log, and keep `backtrace=True` only if the extended trace is wanted.
3. **`logger.remove()` with no argument removes every sink**, including ones another module added. Keep the id returned by `add()` and
   `remove(id)` for targeted removal.
4. A sink added at `level="INFO"` drops DEBUG records for that sink only; other sinks still receive them.

## Patterns that worked

```python
logger.bind(job="ingest").info("hello")                  # extra fields; with serialize=True they appear in record["extra"]
with logger.contextualize(req="r1"):                      # per-request context without passing a logger around
    logger.info("inside")                                 # format "{extra[req]}|{message}" -> "r1|inside"
logger.opt(lazy=True).debug("x {}", costly)               # costly() is NOT called when DEBUG is filtered out (verified)
@logger.catch                                             # logs the exception with traceback and swallows it; re-raise with reraise=True
def main(): ...
```

- `logger.add(sink, serialize=True)` emits one JSON object per line with keys `text` and `record`; `record["extra"]` holds bound fields. Use it for log shipping.
- **Intercept stdlib logging** so third-party libraries land in the same sinks:

  ```python
  import logging
  class Intercept(logging.Handler):
      def emit(self, record):
          try: level = logger.level(record.levelname).name
          except ValueError: level = record.levelno
          logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())
  logging.basicConfig(handlers=[Intercept()], level=0, force=True)
  ```

  Verified: a `logging.getLogger("lib").warning(...)` call reached the loguru sink. The `depth` shifts the reported caller frame; it gave `name` as
  `__main__` here rather than `lib`, so tune it if the module name in the log matters.

## Testing

pytest's `caplog` captures stdlib `logging`, not loguru. In tests either add a sink that appends to a list
(`logger.add(messages.append, format="{message}")`) inside a fixture and `remove(id)` afterwards, or propagate loguru to stdlib with a
`logging.Handler` sink. Remove the default sink in the fixture so test output stays quiet.

## When not to use it

Libraries (see above); code that must run where only the stdlib is allowed; hot paths that log per iteration (formatting cost is paid
unless you gate with `opt(lazy=True)` or a level check).

Not run here (loguru documentation, stated for completeness): trap 3 and 4, the Testing section, and `catch(reraise=True)`.
