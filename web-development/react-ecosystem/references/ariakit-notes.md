# Ariakit `@ariakit/react` 0.4.40: store-driven accessible primitives (server-rendered and driven in jsdom)

Source: [ariakit/ariakit](https://github.com/ariakit/ariakit) (8.6k stars, pushed daily). npm `@ariakit/react` **0.4.40**
(MIT; peers react/react-dom 17 to 19), installed with React 19.3.0 and jsdom on Node/Windows. About 60 probes in two
scripts: `renderToStaticMarkup` for the SSR column, `react-dom/client` + `act` + jsdom for behaviour. jsdom has no layout, so
anything that depends on geometry or real focus-visibility is marked **jsdom-limited**. Not covered: Form/FormStore
validation, Toolbar/Menubar, Hovercard, Command, styling, the experimental `@ariakit/solid` and `@ariakit/tailwind` packages.

## Licence split (read before copying code)

The README says `packages/` and non-Plus `examples/` are MIT, **`examples/` marked Plus are for paying Ariakit Plus customers
only, and `app/` (the website) is proprietary with no licence granted.** Installing from npm is MIT; copying an example file
from the repo or website needs a per-file licence check.

## Package surface

- `@ariakit/react` is now a thin shell: its only dependency is `@ariakit/react-components@0.6.1`; the monorepo also publishes
  `@ariakit/components`, `react-store`, `react-utils`, `store`, `utils` (`sideEffects: false`, ESM). Import from `@ariakit/react`
  only; the lower layers are not API.
- **190 exports: 152 components, 38 hooks.** Families: Button, Checkbox, Collection, Combobox, Command, Composite (+Group, Row,
  Hover, Typeahead), Dialog, Disclosure, Focusable, FocusTrap, Form*, Hovercard, Menu/MenuBar, Popover, Radio, Role, Select,
  Separator, Tab, Toolbar, Tooltip, VisuallyHidden, plus `use*Store`, `use*Context` and `useStoreState`.
- `useMenubarStore`/`useMenuBarStore` (and the `Context` pair) both exist: two spellings of the same hook.

## The three ideas that explain the API

1. **Store + component.** `const dialog = Ak.useDialogStore()` then `<Dialog store={dialog}>` and `<DialogDisclosure store={dialog}>`.
   The `*Provider` components (`DialogProvider`, `TabProvider`, ...) put the store in context so children drop the `store` prop.
   Read store state with `Ak.useStoreState(store, 'value')` (selector form), not by reading `store.getState()` in render.
2. **`render` prop, not `asChild`.** `<Button render={<a href="/x" />}>Link</Button>` rendered exactly `<a href="/x">Link</a>`
   (no `type="button"`, no role added). `Role.div`/`Role.span` are the bare element with the render/prop machinery.
3. **Components are the DOM element**: no wrapper divs for Button/Tab/Checkbox/Disclosure; popover-family components do add one
   absolutely-positioned wrapper (`style="position:absolute;top:0;left:0;width:max-content"`) around the listbox/menu.

## Server-rendered output (React 19.3, ids are `_R_n_` from `useId`)

| Component | HTML emitted |
|---|---|
| `Button` | `<button type="button">` |
| `Button disabled` | `aria-disabled="true"`, `disabled=""`, `style="pointer-events:none"`, `data-truly-disabled="true"` |
| `Button disabled accessibleWhenDisabled` | `aria-disabled="true"` only, `data-truly-disabled="false"`: stays focusable |
| `Tab` / `TabList` / `TabPanel` | `role=tablist` + `aria-orientation`, `role=tab` + `aria-selected`, `role=tabpanel` + `aria-labelledby` + `hidden` + `display:none` |
| `Disclosure` + `DisclosureContent` | `aria-expanded="false"`; content `hidden=""` `display:none`, still in the HTML |
| `DialogDisclosure` + closed `Dialog` | `aria-haspopup="dialog"`, `aria-expanded`; the dialog itself is **not** in the HTML, only `<span style="position:fixed" hidden>` |
| open `Dialog` (`defaultOpen`, `portal={false}`) | `role="presentation" data-backdrop` div, then `role="dialog" tabindex="-1" data-dialog data-open`; `DialogHeading` is an `<h1>` |
| `Select` | `role=combobox` button with `aria-haspopup="listbox"`; shows the current value; a default `aria-hidden` SVG chevron; `SelectItem` with no children prints its `value` |
| `SelectPopover` / `Menu` / `ComboboxPopover` | closed but **in the HTML**: `role=listbox`/`menu`, `hidden`, `display:none`, items rendered |
| `Combobox` | `<input role=combobox aria-autocomplete=list aria-haspopup=listbox aria-expanded=false autoComplete=off>` |
| `Checkbox` | `<input type=checkbox aria-checked>` (a real input, not a div) |
| `VisuallyHidden` | clip-path/1px inline style, no class |
| `Tooltip` + `TooltipAnchor` | anchor unchanged; tooltip is the same hidden `position:fixed` placeholder span |
| `Separator` | `<hr role=separator aria-orientation=horizontal>` |

Consequences: **a closed Dialog and Tooltip contribute no content for SEO/no-JS**, while Select/Menu/Combobox lists and Tab
panels do. **Without `defaultSelectedId`, server-rendered Tabs have every tab `aria-selected="false"` and every panel hidden**
(a first-paint with no visible panel until hydration picks one): pass `defaultSelectedId`.

## Behaviour (jsdom + `act`)

- **Disabled buttons never fire `onClick`** (0 of 2 handlers fired, `disabled` or `accessibleWhenDisabled`); the second still takes
  focus (`document.activeElement` was the button).
- **Disabled composite items stay reachable by arrow keys.** Tabs A (selected), B (`disabled`), C: ArrowRight from A moved focus
  to **B**, which carries `aria-disabled` and `tabindex=-1` (roving tabindex: the tab stop moved to B too). Roving `tabindex` was
  `null` on the active stop and `-1` on the rest. Do not expect "skip disabled" without checking `focusable`/`accessibleWhenDisabled`.
- **Select** opens on click with `aria-expanded=true`, `hidden` cleared and focus on the **currently selected item** (`ib`, value
  `b`); clicking another item set the store value (`a`) and closed the popover (`hidden` back).
- **Dialog**: a click on `DialogDisclosure` set `data-open`, the `role=dialog` node was moved by the default portal **out of the
  React root** (parent was a body-level div, not `#root`), and `#root` got `aria-hidden="true"` (no `inert`) while open. Escape
  set `hidden` on the dialog (it stays in the DOM). Focus landed on the dialog container rather than the inner input and did not
  return to the opener after Escape: **jsdom-limited** (probably because tabbable detection needs layout; not confirmed), check in a real browser
  before claiming either.
- Misuse is loud: `FormInput` outside a `Form` throws `FormInput must be wrapped in a Form component.`
- Testing notes: React's `act` warns "update to DialogBackdrop/DialogImpl was not wrapped in act" for Ariakit's timer-based
  updates; `await new Promise(r => setTimeout(r, 50))` inside the test after each interaction settles them. `ResizeObserver` has
  to be stubbed for popovers.

## When to pick it (judgement, not measured)

Choose Ariakit when the hard part is the **interaction model**: searchable Select/Combobox, composite widgets with roving
focus, nested Menus, Command palettes. Choose shadcn/ui (see `shadcn-cli-4-notes.md`) when you want copy-in styled
components; shadcn now defaults to Base UI, so compare the primitive layer, not the old Radix assumption. Ariakit ships
no styles, so budget the CSS yourself (the Tailwind package is experimental).
