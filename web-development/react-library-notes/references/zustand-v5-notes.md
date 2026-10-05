---
description: "Zustand 5.0.15 traps run against React 19.3 + jsdom: fresh-object selector loops, removed equality arg, setState replace flag, persist shallow merge and dropped versions, async hydration"
source_repo: pmndrs/zustand (MIT)
tested_version: "zustand 5.0.15, react / react-dom 19.3.0, jsdom 30.1.2, Node 22.23.2 on Windows 11; two scripts (about 90 lines) rendering real components inside act(). Package exports listed from the installed package"
verified_date: "2026-10-05"
---

# Zustand 5 (5.0.15): what actually happens

`SKILL.md` names Zustand 5 as the default client-state store. These are the behaviours worth knowing before writing
one, each reproduced with real React 19 rendering. Rule of thumb: server data belongs in a query cache, not here.

## Public surface in v5 (read from the installed package)

| Import | Exports |
|---|---|
| `zustand` | `create`, `createStore`, `useStore` only. **No default export** (`import create from 'zustand'` gives `undefined`) |
| `zustand/react/shallow` | `useShallow` |
| `zustand/shallow` | `shallow` (compare function; `shallow({a:1},{a:1})` is `true`) |
| `zustand/traditional` | `createWithEqualityFn`, `useStoreWithEqualityFn` |
| `zustand/middleware` | `combine, createJSONStorage, devtools, persist, redux, subscribeWithSelector, unstable_ssrSafe` (`immer` lives at `zustand/middleware/immer` and needs the `immer` peer) |

Peer dependencies: `react >= 18`, `@types/react`, `immer >= 9.0.6`, `use-sync-external-store >= 1.2.0`.
**`zustand/traditional` fails to import until you add `use-sync-external-store` yourself** (`ERR_MODULE_NOT_FOUND` from
`esm/traditional.mjs`): it is an optional peer, so npm does not install it.

## Traps, each reproduced

| # | Code | Observed |
|---|---|---|
| 1 | `const {a, b} = useStore(s => ({a: s.a, b: s.b}))` | **Throws `Maximum update depth exceeded`** on first render. A selector returning a new object every call changes the snapshot every time |
| 1b | same selector wrapped: `useStore(useShallow(s => ({a: s.a, b: s.b})))` | renders (`3`). Fix: `useShallow`, or select primitives one by one |
| 2 | `useStore(s => s.a, alwaysEqual)` | the second argument is **ignored**: text changed from 1 to 2 after `setState({a: 2})`. Custom equality needs `createWithEqualityFn` from `zustand/traditional` |
| 2b | `createWithEqualityFn(init, Object.is)` with selector `s => ({v: s.a})` and `shallow` | `setState({a: 1})` (same value) caused **0** re-renders |
| 3 | `store.setState({n: 5}, true)` (replace flag) on a store with an action | state keys become `["n"]`: **the action `inc` is gone** (`typeof inc` is `undefined`). Replace only with a complete state object |
| 4 | `plain.subscribe(s => s.a, listener)` on a plain store | `listener` is **never called** (the selector is taken as the listener). Wrap the creator in `subscribeWithSelector` to get `(value, prev)`; with it, changing only `b` did not fire and changing `a` fired `[2, 1]` |
| 7 | `const st = useStore()` (whole store) in a component | re-renders on a change to an unrelated key (1 extra render for `setState({b: 2})`) |

## `persist`

| # | Situation | Observed |
|---|---|---|
| 5 | Stored `{theme:'dark', ui:{sidebar:true}}`; code default now has `ui:{sidebar:false, density:'compact'}` | result `{"theme":"dark","ui":{"sidebar":true}}`: **`density` lost**. Default merge is shallow; supply `merge` (deep) or `migrate` |
| 5b | Stored `version: 0`, code `version: 1`, no `migrate` | stored value **discarded** (`theme` back to `'light'`); only a `console.error` ("State loaded from storage couldn't be migrated since no migrate function was provided") |
| 5c | `partialize: st => ({n: st.n})` | storage held `{"state":{"n":1},"version":0}`: actions never stored |
| 6 | Async storage (`getItem` returns a promise) | `n` was `0` and `hasHydrated()` `false` right after `create`; 20 ms later `n` was `7`, `true`. Gate rendering on `persist.hasHydrated()` / `onFinishHydration` |

Always set `version` and a `migrate` function the first time a persisted shape might change, and `partialize` to keep
secrets and derived data out of storage.

## Working pattern (assembled from the findings above; this snippet itself was not executed)

```ts
const useCart = create<CartState>()(
  persist(
    (set) => ({ items: [], add: (i) => set((s) => ({ items: [...s.items, i] })) }),
    { name: 'cart', version: 1, partialize: (s) => ({ items: s.items }),
      migrate: (old, v) => v === 0 ? { items: (old as any).list ?? [] } : (old as CartState) },
  ),
)
const items = useCart((s) => s.items)                     // one slice, primitive/stable reference
const { add, clear } = useCart(useShallow((s) => ({ add: s.add, clear: s.clear })))
```

Not run: devtools, SSR/Next.js hydration (`unstable_ssrSafe`), `immer`, the `redux` middleware, TypeScript typing of
`create<T>()()`, and bundle size claims.
