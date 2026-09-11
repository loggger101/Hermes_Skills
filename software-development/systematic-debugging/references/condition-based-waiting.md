# Condition-Based Waiting (Replace Arbitrary Timeouts)

Use when tests guess at timing with arbitrary sleeps — flaky tests that pass on fast machines but fail under load or CI, timeouts in parallel runs, waits for async completion.

Source: adapted from obra/superpowers v6.3.0 (`skills/systematic-debugging/condition-based-waiting.md`, MIT). Python implementation included; the upstream TypeScript version ships domain helpers (wait_for_event / wait_for_event_count / wait_for_event_match) built on the same 10ms-poll core.

**Core principle:** Wait for the actual condition you care about, not a guess about how long it takes.

## Before / After

```python
# BEFORE: guessing at timing
time.sleep(0.05)
result = get_result()
assert result is not None          # flaky under load

# AFTER: waiting for the condition
wait_for(lambda: get_result() is not None, "result to appear")
result = get_result()
assert result is not None          # deterministic
```

## Quick Patterns

| Scenario | Pattern |
|----------|---------|
| Wait for event | `wait_for(lambda: next((e for e in events if e.type == 'DONE'), None), "DONE event")` |
| Wait for state | `wait_for(lambda: machine.state, ...)` (or compare explicitly) |
| Wait for count | `wait_for(lambda: len(items) >= 5 and items[4].done, "5 completed items")` |
| Wait for file | `wait_for(lambda: os.path.exists(path), f"file {path}")` |
| Complex condition | `wait_for(lambda: obj.ready and obj.value > 10, ...)` |

## Generic Implementation (poll every 10ms)

```python
import time

def wait_for(condition, description: str, timeout_ms: int = 5000):
    """Poll condition() until truthy; raise with a descriptive error on timeout."""
    start = time.monotonic()
    while True:
        result = condition()          # call the getter INSIDE the loop — fresh data every poll
        if result:
            return result
        if (time.monotonic() - start) * 1000 > timeout_ms:
            raise TimeoutError(f"Timeout waiting for {description} after {timeout_ms}ms")
        time.sleep(0.01)              # 10ms poll — not 1ms (CPU waste), not seconds (latency)
```

Domain helpers follow the same shape and reject with *what was expected* plus, for counts, *how many were actually found*.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Polling too fast (`sleep(0.001)`) — wastes CPU | Poll every 10ms |
| No timeout — loop forever if condition never met | Always include a timeout with a clear error naming the expected state |
| Stale data — cache state before the loop | Call the getter inside the loop for fresh data each poll |

## When an Arbitrary Timeout IS Correct (the legitimate exception)

Only when you are testing actual *timed* behavior (debounce/throttle intervals, tick cadence): first wait for the triggering condition, then sleep a duration derived from known timing — and document why.

```python
# Tool ticks every 100ms; need 2 ticks to verify partial output
wait_for(lambda: any(e.type == 'TOOL_STARTED' for e in events), "tool start")
time.sleep(0.2)   # 2 ticks at 100ms — derived from the tick period, not a guess
```

Requirements: (1) first wait for the triggering condition; (2) duration based on known timing, not guessing; (3) comment explaining WHY. **Always document why when using any arbitrary timeout.**

**Real-world result (upstream session):** 15 flaky tests across 3 files — pass rate 60% -> 100%, execution ~40% faster, no more race conditions.
