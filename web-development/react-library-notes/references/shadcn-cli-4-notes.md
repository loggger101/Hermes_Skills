# shadcn CLI 4.21.2: what `init` and `add` actually do (run live on Windows)

Source: [shadcn-ui/ui](https://github.com/shadcn-ui/ui) (MIT). npm `shadcn` **4.21.2** (released 2026-10-05), installed into a
scratch project; the CLI then created and modified a real Vite project (`init -t vite -n demo -p nova -y --no-monorepo`, 93 s, network
required). Node 22.23.2, Windows. Run non-interactively (`CI=1`, stdin closed). Every result below was captured; nothing
was run against Next.js, monorepos, registries other than the default, or the MCP server.

## Commands (from `shadcn --help`)

`init|create`, `apply`, `add`, `diff` (**deprecated**: use `add <name> --diff`), `docs`, `view`, `search|list`, `migrate`, `eject`,
`info`, `build`, `mcp` (`mcp init` configures a client), `preset` (`decode`, `resolve|info`, `url`, `open`), `registry` (`add`,
`validate`). Notable options: `init --template next|start|vite|react-router|laravel|astro`, `--base base|radix|aria` (the component
library underneath), `--preset <name>`, `--monorepo/--no-monorepo`, `--css-variables`, `--rtl`, `--pointer`, `--reinstall`;
`add --dry-run`, `--diff [path]`, `--view [path]`, `--overwrite`, `--all`, `--path`; `apply --only theme,font`.

## `init`: a surprising default and a help-text bug

- **`--defaults` is documented as `--template=next --preset=base-nova`, but `-p base-nova` fails**: `Invalid preset: base-nova.
  Available presets: nova, vega, maia, lyra, mira, luma, sera, rhea`. The working call was `-p nova`; the resulting
  `components.json` then reads `"style": "base-nova"` (preset name plus base). So `style` in the file and the `--preset` value
  differ; do not copy one into the other.
- It created a complete **Vite** project (new `.git`, `.prettierrc`, `eslint.config.js`, `vite.config.ts`, `tsconfig.*`) with:
  `vite ^8`, `react ^19.2.8`, `typescript ~6.0.2`, `eslint ^10`, `@vitejs/plugin-react ^6`, **Tailwind 4 through `@tailwindcss/vite`**
  (no `tailwind.config`), `tw-animate-css ^1.4.0`, `lucide-react ^1.52.0`, `class-variance-authority ^0.7.1`, a Geist variable font
  (`@fontsource-variable/geist`), and three shadcn-owned packages: **`shadcn ^4.21.2`**, **`cn ^0.4.0`**, **`@base-ui/react ^1.8.0`**.
- **The default component base is Base UI, not Radix**: `button.tsx` imports `Button as ButtonPrimitive` from `@base-ui/react/button`
  and `dialog.tsx` from `@base-ui/react/dialog`. Choose `--base radix` at `init` if you depend on Radix primitives.
- **`cn` is now an npm package**, not code in your repo: `src/lib/utils.ts` is the single line `export { cn } from "cn"`, and the
  components `import { cn } from "cn"`. `npm view cn` -> "Fast, small, compiled class-name merging for Tailwind CSS. Drop-in replacement for
  clsx + tailwind-merge", maintainer shadcn, repo `shadcn-ui/cn`. There is no local `clsx`/`tailwind-merge` import to edit.
- `src/index.css` starts with `@import "tailwindcss"; @import "tw-animate-css"; @import "shadcn/tailwind.css"; @import
  "@fontsource-variable/geist";`, then `@custom-variant dark (&:is(.dark *));` and an `@theme inline` block. `shadcn eject` ("inline
  shadcn/tailwind.css and remove the shadcn dependency") exists for owning that file.
- `components.json` fields: `$schema`, `style`, `rsc: false`, `tsx: true`, `tailwind {config: "", css: "src/index.css", baseColor:
  "neutral", cssVariables: true, prefix: ""}`, `iconLibrary: "lucide"`, `rtl`, `aliases {components, utils, ui, lib, hooks}`, `menuColor`,
  `menuAccent`, and an empty `registries: {}`. The alias `@` was wired into both `vite.config.ts` (`resolve.alias`) and the tsconfig `paths`.

## Reading the project and the registry

| Command | Result |
|---|---|
| `info --json` | `project`: framework Vite, `srcDirectory true`, `typescript true`, **`tailwindVersion "v4"`**, `tailwindConfig null`, `tailwindCss "src/index.css"`, `importAlias "@"`; `config`: style, base `"base"`, aliases and resolved absolute paths |
| `preset resolve` | `code b2fA`, style nova, baseColor/theme/chartColor neutral, iconLibrary lucide, font geist, radius default, menuAccent subtle, plus `https://ui.shadcn.com/create?preset=b2fA`: a preset is a short code you can share |
| `view button` | prints the registry item as JSON including the **full file content** (`registry/base-nova/ui/button.tsx`) and `dependencies: ["cn"]` |
| `docs button --json` | **links only**: `https://ui.shadcn.com/docs/components/base/button` and an examples URL, not documentation text |
| `search -q button` / `search -t block` | **exit 1**: `No registries are configured in components.json. Provide a registry or namespace to search, e.g. shadcn search @shadcn.` (`registries` is empty by default, so pass `@shadcn`) |
| `migrate --list` | `cn`, `icons`, `base-color`, `radix`, `rtl` |
| `add nonexistentcomp-zzz -y` | exit 1: `The item at https://ui.shadcn.com/r/styles/base-nova/nonexistentcomp-zzz.json was not found. It may not exist at the registry.` |

## `add`: dry runs, skips, overwrites (what an agent must know)

1. `add button --dry-run` (10 s): `Files (1) =1 skip`, `= src\components\ui\button.tsx skip (identical)`, `Dependencies (1) + cn`,
   then `Run with --diff ... --view ...`.
2. `add button dialog -y`: created `dialog.tsx`, **skipped `button.tsx`** with `Skipped 1 file: (files might be identical, use
   --overwrite to overwrite)`. That message appears for identical files; it is the normal idempotent case.
3. After appending `// LOCAL EDIT` to `button.tsx`: **`add button -y` does not overwrite and still asks**:
   `The file button.tsx already exists. Would you like to overwrite? (y/N)`. `-y` skips the confirmation for the add, **not** this
   per-file prompt. With stdin closed (an agent run) it cannot answer and leaves the file alone.
4. `add button --diff` printed a unified diff of what an overwrite would do (`-// LOCAL EDIT`, with `(overwrite)` next to the
   path) and wrote nothing. Always diff first when you have local edits.
5. `add button -y -o` printed `Updated 1 file` and **discarded the local edit**. Commit before overwriting.

## Checklist

- Pass `--preset` from the list the CLI prints, not from the help text; record the preset **code** (`preset resolve`) for reproducibility.
- Decide `--base radix|base|aria` at `init`; later components follow `components.json`'s base.
- Expect two extra npm dependencies (`shadcn`, `cn`) and a CSS import from `shadcn/tailwind.css`: they are not "copy-in only" any more.
- In automation use `add <names> -y -o` only on files you have not edited; otherwise `--diff` first.
- Configure registries (`shadcn registry add @shadcn`, or `registries` in `components.json`) before using `search`.
