# Web Interface Guidelines (UI/UX Review Checklist) [PORTED]

Source: Vercel's **Web Interface Guidelines** — ported verbatim from tech-leads-club/agent-skills' `(design)/web-design-guidelines` skill (`references/guideline.md`, 173 lines), which itself derives from the public `vercel-labs/web-interface-guidelines`. License MIT; attribution: Vercel. Mined 2026-09-17 (final screen). This is a CODE-LEVEL UI review checklist — it complements, not replaces, Core Web Vitals (`static-site-patterns` main body) and the CRO/form/UX audit frameworks in `productivity/website-audit/references/cro-form-ux-checklists.md`.

**How to use:** read target files → check every rule below → output findings grouped by file in clickable `file:line` format, terse (high signal-to-noise; "sacrifice grammar for brevity"). Mark a file `✓ pass` when clean. Framework-specific sections (Hydration Safety) apply only where the stack hydrates — skip them for pure static HTML/CSS/JS sites.

## Accessibility
- Icon-only buttons need `aria-label`; form controls need `<label>` or `aria-label`
- Interactive elements need keyboard handlers (`onKeyDown`/`onKeyUp`)
- `<button>` for actions, `<a>`/`<Link>` for navigation — never `<div onClick>` / `<span>` with click handlers
- Images need `alt` (or `alt=""` if decorative); decorative icons need `aria-hidden="true"`
- Async updates (toasts, validation) need `aria-live="polite"`
- Use semantic HTML (`<button>`, `<a>`, `<label>`, `<table>`) BEFORE reaching for ARIA
- Headings hierarchical `<h1>`–`<h6>`; include a skip link to main content; `scroll-margin-top` on heading anchors

## Focus States
- Interactive elements need visible focus (`focus-visible:ring-*` or equivalent)
- Never `outline-none` / `outline: none` without a focus replacement
- Prefer `:focus-visible` over `:focus` (avoids the ring appearing on click); group compound controls with `:focus-within`

## Forms
- Inputs need `autocomplete` and meaningful `name`; correct `type` (`email`, `tel`, `url`, `number`) + `inputmode`
- Never block paste (`onPaste` + `preventDefault`); labels clickable (`htmlFor` or wrapping the control)
- Disable spellcheck on emails/codes/usernames; checkboxes/radios: label+control share ONE hit target (no dead zones)
- Submit button stays enabled until the request starts, then shows a spinner; errors inline next to fields + focus first error on submit
- Placeholders end with `…` and show an example pattern; `autocomplete="off"` on non-auth fields (avoids password-manager triggers); warn before navigating away with unsaved changes

## Animation
- Honor `prefers-reduced-motion` (reduced variant or disable)
- Animate `transform`/`opacity` only (compositor-friendly); never `transition: all` — list properties explicitly; set correct `transform-origin`
- SVG: transforms on a `<g>` wrapper with `transform-box: fill-box; transform-origin: center`; animations must be interruptible mid-flight

## Typography & Copy
- `…` not `...`; curly quotes “ ” not straight " "; non-breaking spaces in units/shortcuts (`10&nbsp;MB`, `⌘&nbsp;K`)
- Loading states end with `…` ("Loading…"); tabular numerals for columns of numbers
- Active voice ("Install the CLI", not "The CLI will be installed"); Title Case headings/buttons (Chicago); numerals for counts ("8 deployments")
- Specific button labels ("Save API Key" not "Continue"); error messages state the fix/next step, not just the problem; second person

## Content Handling & Images
- Text containers handle long content (`truncate` / `line-clamp-*` / `break-words`); flex children need `min-w-0` to allow truncation
- Handle empty states — never render broken UI for empty strings/arrays; anticipate short, average, and very-long user inputs
- `<img>` needs explicit `width`+`height` (prevents CLS); below-fold: `loading="lazy"`; above-fold critical images: `fetchpriority="high"`

## Performance
- Large lists (>50 items): virtualize (`content-visibility: auto`, or a virtualization lib) — never bare `.map()` over big arrays
- No layout reads in render (`getBoundingClientRect`, `offsetHeight/Width`, `scrollTop`); batch DOM reads/writes, avoid interleaving
- Prefer uncontrolled inputs; controlled ones must be cheap per keystroke; `<link rel="preconnect">` for CDN domains; critical fonts: `preload as="font"` + `font-display: swap`

## Navigation & State
- URL reflects state — filters/tabs/pagination/expanded panels in query params (deep-link ALL stateful UI)
- Links use real `<a>` elements (Cmd/Ctrl+click, middle-click support); destructive actions need a confirmation modal or undo window — never immediate

## Touch, Safe Areas & Theming
- `touch-action: manipulation` (kills double-tap-zoom delay); set `-webkit-tap-highlight-color` intentionally; `overscroll-behavior: contain` in modals/drawers/sheets
- During drag: disable text selection + `inert` on dragged elements; use `autoFocus` sparingly (desktop, single primary input — avoid on mobile)
- Full-bleed layouts need `env(safe-area-inset-*)` for notches; kill unwanted scrollbars (`overflow-x-hidden`, fix the overflow source); flex/grid over JS measurement
- Dark mode: `color-scheme: dark` on `<html>` (fixes scrollbar/inputs), `<meta name="theme-color">` matching page background, explicit colors on native `<select>`

## Locale & i18n
- Dates/times via `Intl.DateTimeFormat`, numbers/currency via `Intl.NumberFormat` — never hardcoded formats; detect language from `Accept-Language` / `navigator.languages`, not IP

## Hydration Safety (framework-only)
- Inputs with `value` need `onChange` (else use uncontrolled); guard date/time rendering against server/client mismatch; `suppressHydrationWarning` only where truly needed

## Anti-patterns to flag (one-line each)
`user-scalable=no` / `maximum-scale=1` · paste-blocking handlers · `transition: all` · `outline-none` without replacement · inline-`onClick` navigation · `<div>`/`<span>` click targets · images without dimensions · unvirtualized large lists · inputs without labels · icon buttons without `aria-label` · hardcoded date/number formats · unjustified `autoFocus`

## Output format (matches our audit convention)
```text
## src/Button.tsx
src/Button.tsx:42 - icon button missing aria-label
src/Button.tsx:55 - animation missing prefers-reduced-motion
✓ pass            ← for clean files
```
