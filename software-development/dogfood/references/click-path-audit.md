# Click-path audit: buttons that "do nothing" though every function works

Source: [affaan-m/ECC](https://github.com/affaan-m/ECC) `skills/click-path-audit` (MIT, community origin), read at source
level 2026-10-05. The bug class below was **reproduced here with zustand 5.0.15 on Node** (a vanilla `createStore`, no
React), and the mechanical side-effect map was written and run by this repo, not copied from ECC. Nothing was run in a
browser.

## When to reach for it

Exploratory QA (`dogfood`) and static debugging both pass, yet a user says a button does nothing or the screen ends in
the wrong state. Typical after a refactor of a shared store. Static review checks *does the function exist, does it
crash, are the types right*; none of those asks **does the final state match the button label?**

## The bug, reproduced

A "New email" handler calls two store actions in order:

```js
setComposeMode(true)        // sets composeMode = true
selectThread(null)          // also resets composeMode = false (an undeclared side effect)
```

Run live: `composeMode` ended **false**; reordering the calls gave true; one atomic action
`startCompose: () => set({ composeMode: true, selectedThread: null, messages: [] })` gave `true` and `thread = null` with
no ordering dependency. Both functions exist, neither throws, the types are right: that is why code reading misses it.

## Step 1: build the side-effect map mechanically

ECC asks the auditor to read each store action and write `sets / RESETS` by hand. Cheaper and less error-prone: run each
action from a deliberately **dirty** state and diff what changed against the fields the action is supposed to own.

```js
const dirty = () => { const st = mk(); st.setState({ composeMode: true, selectedThread: 'T9', messages: ['x','y'] }); return st; };
const declared = { setComposeMode: ['composeMode'], selectThread: ['selectedThread', 'messages'] };
for (const [name, fields] of Object.entries(declared)) {
  const st = dirty(); const before = { ...st.getState() };
  st.getState()[name](name === 'setComposeMode' ? false : null);
  const after = st.getState();
  const changed = Object.keys(before).filter(k => typeof before[k] !== 'function' && JSON.stringify(before[k]) !== JSON.stringify(after[k]));
  console.log(name, 'undeclared =', changed.filter(k => !fields.includes(k)));
}
```

Output: `setComposeMode: undeclared=[]`, **`selectThread: undeclared=["composeMode"]`**. The control (a clean action) reports
nothing, so the check discriminates. Choose arguments that actually change each field, or a reset to the same value hides
(a reset to `false` from `false` shows no diff).

## Step 2: trace each touchpoint against the map

For every handler list the calls in order, what each writes, what it silently resets, and whether the **final** state
matches the label. Six patterns (ECC's list, with the three I ran marked):

| # | Pattern | Signature | Run here |
|---|---|---|---|
| 1 | Sequential undo | call B resets what call A set | yes: composeMode true -> false |
| 2 | Async race | two promises write the same field; last resolver wins | yes: the 30 ms writer resolved last and won, `loading` ended false |
| 3 | Stale closure | `setCount(count + 1)` twice with a captured `count` | yes: count 1, functional update `c => c + 1` gave 2 |
| 4 | Missing transition | button says Save/Delete/Send, handler only validates or sets a flag | no |
| 5 | Conditional dead path | the guarding state is always false at that point | no |
| 6 | Effect interference | an effect watching the flag resets it | no |

## Report format (one per finding)

`CLICK-PATH-NNN [CRITICAL|HIGH|MEDIUM|LOW]`, touchpoint with `file:line`, pattern, numbered trace
(`call -> sets {...} / RESETS {...}  <- CONFLICT`), expected vs actual, concrete fix. Then add a regression test per
finding (the test is a store-level one like the script above; no DOM needed).

## Scoping (ECC's guidance, kept)

Full-app audits are expensive: map the stores first (one agent), then fan out one agent per page with that map as shared
input. For a single page, or after changing one store action, audit only that action's callers
(`grep -rn 'selectThread(' src`). Skip for API shape bugs (use systematic-debugging), styling, performance.

## Fixes that remove the class instead of the instance

- Prefer one atomic action per user intent (`startCompose`) over callers sequencing two setters.
- Do not let an action reset fields it does not own; if it must, name it for the reset (`resetThreadAndCompose`).
- Add the dirty-state diff above as a unit test per store so a new undeclared reset fails CI.
