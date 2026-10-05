# React 19.3.0 core: server rendering, effects, actions, Activity (run live in Node + jsdom)

Source: [react/react](https://github.com/react/react) (MIT; npm `react` 19.3.0, 2026-09-09; dist-tag `latest`). `react`,
`react-dom` 19.3.0 and `jsdom` installed in a scratch ESM project, Node 22.23.2 on Windows; client code rendered with
`createRoot` inside `act()`, server code with `react-dom/server`. About 70 probes in two scripts; every line is an observed
output. Complements `zustand-v5-notes.md` (store behaviour in the same setup) and `nextjs-16-notes.md`.

## Exports worth knowing (19.3.0)

`react` exports `use`, `useActionState`, `useOptimistic`, `useEffectEvent`, `useId`, `useTransition`, `useDeferredValue`,
`useSyncExternalStore`, `cache`, `cacheSignal`, `act`, `Activity`, `ViewTransition` (the last two are symbols);
`forwardRef` and `memo` still exist. `react-dom` exports `preload`, `preinit`, `preconnect`, `prefetchDNS`, `useFormStatus`,
`requestFormReset`, `createPortal`, `flushSync`. **Gone:** `ReactDOM.render`, `hydrate`, `unmountComponentAtNode`, `findDOMNode`,
`React.createFactory`, `React.PropTypes` (all `undefined`). `react-dom/server` has `renderToString`, `renderToStaticMarkup`,
`renderToPipeableStream`, `renderToReadableStream`, `resume`, `resumeToPipeableStream`.

## Server rendering output

| Input | Output |
|---|---|
| `h('div', {className:'a', style:{color:'red', fontSize:12}}, ...)` | `<div class="a" style="color:red;font-size:12px">` |
| children `'a','b',1` | `renderToString`: `<p>a<!-- -->b<!-- -->1</p>` (text-node separators); `renderToStaticMarkup`: `<p>ab1</p>` |
| attribute/text escaping | `title="&quot;q&quot;"`, `&lt;script&gt;&amp;` |
| `disabled: true, readOnly: false, 'aria-label', 'data-x': 1` | `disabled="" aria-label="l" data-x="1"` (false attributes omitted) |
| `useId()` | `_R_0_` (React 19.2+ format; no longer `:r0:`), so CSS selectors written for `:r0:` break |
| `ref` as a plain prop | works for function components, no `forwardRef` needed |
| `<Ctx value="v">` | context object used directly as the provider |
| `<title>`, `<meta>`, `<link rel="stylesheet" precedence>` inside a `div` | **hoisted ahead of the div**: `<link ... data-precedence="default"/><title>T</title><meta .../><div>x</div>` |
| `<style href="a" precedence="low">` | `<style data-precedence="low" data-href="a">` |
| children `undefined, null, false, true, 0, ''` | only `0` renders: `<p>0</p>` |
| lowercase `onclick="x()"` | warning `Invalid event handler property onclick. React events use the camelCase naming convention` and the attribute is dropped |
| a component returning `undefined` | allowed, renders nothing |
| `{a: 1}` or a `Date` as a child | `Error: Objects are not valid as a React child (found: object with keys {a})` |
| `createElement(undefined)` | `Error: Element type is invalid: expected a string ... but got: undefined` |
| a hook outside a component / in a class | `Invalid hook call. Hooks can only be called inside of the body of a function component` (plus `TypeError: Cannot read properties of null (reading 'useState')` when called at module level) |

**`renderToString` and Suspense:** a pending boundary does not wait. Output was
`<!--$!--><template data-msg="Switched to client rendering because the server rendering aborted ... The server used "renderToString" which does not support Suspense ...">...LOADING<!--/$-->`:
the fallback is emitted and the boundary re-renders on the client. `renderToPipeableStream` with `onAllReady` and `use(promise)` waited
and produced `<!--$--><i>data</i><!--/$-->`.

## Client behaviour (jsdom + `act`)

- Effect order without StrictMode on mount then one click: `layout:0, effect:0, layout:1, cleanup:0, effect:1` (layout effects
  run before passive ones; the previous cleanup runs right before the next effect).
- **StrictMode dev double-invokes effects**: `layout:0, effect:0, cleanup:0, layout:0, effect:0` on mount. Effects must be idempotent
  and have real cleanups.
- Two `setState` calls in one click handler caused **1 render**. `setN(n + 1)` twice with a captured `n` ended at **1**; use
  `setN(c => c + 1)` for 2.
- `useOptimistic` inside a `startTransition(async ...)`: text was `a|b(pending)` while the async action ran and `a|b` after
  `setMsgs` committed.
- `useActionState` with a `<form action={fn}>`: submitting through jsdom **threw `TypeError: FormData constructor: Argument 1 could not
  be converted`** because React calls the global `FormData`, which in Node is undici's, not jsdom's. Set
  `globalThis.FormData = dom.window.FormData` before rendering; then the state became `init:v|false`.
- `useEffectEvent` called during render throws `A function wrapped in useEffectEvent can't be called during rendering.`
- `Activity`: `mode="hidden"` renders **nothing in SSR** (`''`) while `mode="visible"` renders the children; on the client a hidden
  tree stays mounted with `style="display: none !important"`, and **state is preserved** across hide/show (`1` after toggling).
- `React.cache(fn)` called twice with the same argument outside a request executed `fn` **twice**: its de-duplication only works
  inside a server render, not in plain client code or scripts.
- Hydration mismatch (`<p>server</p>` vs client `<p>client</p>`): `onRecoverableError` received `Hydration failed because the server
  rendered text didn't match the client. As a result this tree will be regenerated...` and the DOM ended as `client`.
- Dev warnings seen: controlled `value` without `onChange` (`This will render a read-only field`), missing list `key`,
  `Invalid DOM property class/for/tabindex` (use `className`, `htmlFor`, `tabIndex`), and `validateDOMNesting` for a `div`
  inside a `p`.

## Test-setup checklist

1. `globalThis.IS_REACT_ACT_ENVIRONMENT = true`, wrap every render and event in `await act(async () => ...)`.
2. With jsdom set `globalThis.window`, `document`, `navigator` (Node defines its own global `navigator`; I replaced it with `Object.defineProperty`)
   and `FormData`.
3. Dispatch events as `new dom.window.MouseEvent('click', {bubbles: true})`; React listens at the root.
4. Not covered: React Server Components, Server Actions, the React Compiler, `ViewTransition` rendering, DevTools, React Native.
