---
name: pygame
description: "Use when building or testing pygame/SDL games."
version: v0.9.0
author: Hermes Agent (ported from starred-repo research)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [pygame, sdl2, games]
    related_skills: [manim-video, p5js]
---

## When to Use

- When working on: Use when building or testing pygame/SDL games.

## What This Skill Does

Distilled from the pygame/pygame repo itself (`examples/aliens.py`, `examples/headless_no_windows_needed.py`, `test/__main__.py` runner + `base_test.py`, main branch as of 2026-09-04). The API reference lives in their docs;


# Pygame (SDL2) — patterns and traps

Distilled from the pygame/pygame repo itself (`examples/aliens.py`, `examples/headless_no_windows_needed.py`,
`test/__main__.py` runner + `base_test.py`, main branch as of 2026-09-04). The API reference lives in their docs;
this is what an agent gets wrong or re-discovers painfully.

## When to use / not use

- Use for: windowed games, SDL-based apps, image/audio processing via pygame's C-accelerated surface ops,
  headless rendering (thumbnails, procedural textures), game logic that must be testable without a display.
- Don't use for: browser games (→ `p5js` skill), video output (→ `manim-video` / `ascii-video`).

## Headless first — the pattern that unlocks everything else

pygame runs with **no windowing system at all** on servers/CI/cron/background jobs. The exact sequence, from
their own example:

```python
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"   # MUST be set BEFORE importing pygame
import pygame as pg
pg.display.init()                          # some platforms need this for parts of pg
screen = pg.display.set_mode((1, 1))       # a 1x1 surface is enough to unlock image ops
```

- The env var **before the import** is the load-bearing part — SDL reads it at init. Setting it after `import pygame` does nothing.
- What works headless: `image.load/save`, `transform.scale/smoothscale/flip`, `draw.*`, fonts (after display.init), surfarray/sndarray numpy bridges, masks. This makes thumbnail generation, procedural texture baking, and — most importantly — **testing game logic** possible anywhere.
- Audio does NOT work headless; guard it (see below).

## Canonical main loop (the shape of every pygame app)

Order matters at each stage:

```python
import pygame as pg

if pg.get_sdl_version()[0] == 2:
    pg.mixer.pre_init(44100, 32, 2, 1024)   # BEFORE pg.init() — audio params only take effect pre-init
pg.init()
if pg.mixer and not pg.mixer.get_init():     # pygame can be built without mixer; degrade gracefully
    print("Warning, no sound")
    pg.mixer = None

bestdepth = pg.display.mode_ok((W, H), 0, 32)   # ask SDL what it will actually give you
screen = pg.display.set_mode((W, H), 0, bestdepth)

# Load assets AFTER set_mode: convert() needs the display's pixel format to exist yet.
def load_image(f):
    s = pg.image.load(f)
    return s.convert()          # per-display-format copy; blits are dramatically faster after this

clock = pg.time.Clock()
while running:
    for event in pg.event.get():        # PUMP EVERY FRAME — see traps
        if event.type == pg.QUIT:
            running = False
    ...update state...                  # input via key.get_pressed(), collisions, timers
    screen.fill(BG)                     # or dirty-rect clear (see below)
    ...draw...
    pg.display.flip()                   # full redraw; use display.update(dirty_rects) instead if you have them
    clock.tick(60)                      # frame CAP — not sleep(); tick also returns elapsed ms for dt

pg.quit()   # at the very end, after the loop
```

- `clock.tick(fps)` caps framerate AND is your delta-time source. Never `time.sleep` in a game loop (it drifts and ignores vsync).
- Fullscreen toggle: back up with `screen.copy()`, re-run `set_mode(... | pg.FULLSCREEN)`, **re-blit the backup** — set_mode resets the surface contents, so skipping the blit gives you a blank screen.

## Sprite/Group architecture (their object model)

One class per object type; groups are what make objects "live" and drive updates:

```python
class Alien(pg.sprite.Sprite):
    def __init__(self, *groups):            # pass groups in the constructor — that's how it joins them
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = ...
        self.rect = self.image.get_rect()   # rect is THE collision/position object; keep it current
    def update(self, *args):                # called once per frame by every Group you're in
        self.rect.move_ip(dx, 0)            # move_ip MUTATES; .move returns a new Rect (classic bug source)
        if not screenrect.contains(self.rect):
            ...
```

- `Group.update()` calls each member's `update`; `RenderUpdates.draw(screen)` draws members and **returns the dirty rects** — hand those to `pg.display.update(dirty)` to repaint only what moved. That is their speed optimization; a full `fill`+`flip` every frame is fine for small scenes but dies at scale.
- Lifecycle: `sprite.kill()` removes it from all its groups (use in `update` when done — explosions, off-screen bullets). A sprite "lives" only because some group holds a reference to it.
- Collisions: `pg.sprite.spritecollide(player, aliens, dokill)` and `groupcollide(g1, g2, dokill_g1, dokill_g2)`. The dokill flags decide whether the hit members are removed — read them every time; forgetting one is a "bullets pass through" bug.
- `GroupSingle` for exactly-one semantics ("the most recent alien").

## Testing game logic (their test-suite discipline, worth copying)

Their runner (`test/__main__.py`) does three things that make hang-prone GUI code testable:

1. **Optional subprocess isolation with a kill timer**: by default the suite runs in ONE process; `-s/--usesubprocess` moves each test module into its own subprocess, and `time_out` (default 120 s) kills stalled ones — a hung game loop becomes a failed test instead of a frozen CI. Failed modules are tracked as "untrusty" and re-run at the end so one bad module can't mask the rest. Do the same for any pygame logic you write tests around: wrap execution in a timeout so a hang is detectable and fatal, not silent.
2. **Randomization + seed** (`--randomize`, `--seed`) to catch order-dependent flakes; interactive tests are excluded by default (opt-in `-I`).
3. **Skip, don't fail, on optional hardware**: their pattern is `@unittest.skipIf(not pygame.HAVE_NEWBUF, ...)` / `skipIf(IS_PYPY, ...)`. For your own code: skip when the display/audio device is absent rather than failing — CI boxes have neither.

The structural enabler: **decouple update from render**. If every object's state change lives in a pure-ish `update(dt)` that only reads/writes rects and counters (no blits), you can drive 10,000 frames headless with the dummy driver above and assert on positions/scores without ever opening a window.

## Traps table

| Trap | Symptom | Fix |
|---|---|---|
| `SDL_VIDEODRIVER` set after import | "no display" errors in CI despite setting it | env var BEFORE `import pygame`, always |
| Stopped pumping events | window unresponsive, QUIT never arrives, resize ignored | call `pg.event.get()` every frame even if you ignore most events — the OS delivers input through that queue |
| `.convert()` before set_mode (or not at all) | slow blits; sometimes black/garbled images on some displays | convert AFTER set_mode; re-convert after any fullscreen toggle |
| `rect.move` vs `move_ip` | object doesn't move / moves twice | `move_ip` mutates in place; `.move()` returns a new Rect you must assign back |
| Audio assumed present | crash on machines without audio (or headless) | the two-line degrade pattern above: check `pg.mixer.get_init()`, set to None, guard every play call with `if pg.mixer and sound is not None` |
| Non-BMP formats fail silently-ish | can't load .png/.jpg in a minimal build | `if not pg.image.get_extended(): raise SystemExit(...)` early (their examples do this) |
| `time.sleep` for frame pacing | drift, no vsync, wrong dt | `clock.tick(fps)`; use its return value as dt if you need it |
| Fullscreen toggle without re-blit | blank screen after F11 | copy the surface before set_mode, blit back after |

## Performance rules (in order of impact)

1. `.convert()` every loaded image — per-display pixel format; unconverted blits are many times slower.
2. Dirty-rect rendering (`RenderUpdates` + `display.update(dirty)`) for scenes with lots of static content and few movers.
3. `transform.scale` (fast, MMX/SSE, multithreaded where available) vs `smoothscale` (quality; use only when you actually need it — it's the slow one).
4. Cap with `clock.tick`; batch font renders (render text only when its value changes — their Score sprite caches and re-renders on change only).

## Grounding

Patterns extracted 2026-09-04 from pygame/pygame main: `examples/headless_no_windows_needed.py`
(dummy driver + scale CLI), `examples/aliens.py` (loop, groups, dirty rects, audio degrade, fullscreen
toggle — the canonical reference example in their repo), `test/__main__.py` (subprocess runner with
timeout kill / randomize / interactive opt-in), `src_py/sprite.py` (Group/Sprite API). Repo: 8.9k stars,
active; C core (`src_c`) + pure-Python API layer (`src_py`).
