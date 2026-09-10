---
description: "Verified GitHub web-UI + URL tricks from tiimgreen/github-cheat-sheet (MIT) — diff params, compare URLs, gists-as-repos, templates"
source_repos: tiimgreen/github-cheat-sheet (MIT), re-verified live 2026-09-10 against github.com; stale items flagged inline
tested_version: every URL pattern curl-checked on this machine 2026-09-10 (HTTP status noted); git protocol for gists exercised with real clone/ls-remote
verified_date: "2026-09-10"
---

# GitHub Web UI + URL Tricks (distilled from github-cheat-sheet)

The cheat sheet's Git CLI recipes live in `git-workflow-recipes.md`; this file is the other half —
everything about browsing, comparing, and linking on github.com itself. Every item below was
re-checked against a live repo (`tiimgreen/github-cheat-sheet`, default branch `master`) or current
github/docs on 2026-09-10; items that died since the cheat sheet's last update (Oct 2023) are in
**Stale / dead** at the bottom.

## Diff and file URL parameters

| Param | Effect | Verified |
|---|---|---|
| `?w=1` on any diff/compare URL | hide whitespace-only changes — see only real code deltas | 200 OK live |
| `?ts=N` on a blob/diff URL | render tabs as N spaces (default 8); does NOT work on gists or raw views | 200 OK live |

```text
https://github.com/{user}/{repo}/compare/A...B?w=1        # code-only diff of the range
https://github.com/{user}/{repo}/blob/master/f.py?ts=4    # Go-style tab width on any file
```

## Compare URLs (the most useful pattern in this file)

```text
https://github.com/{user}/{repo}/compare/{range}          # {range} = A...B, three dots = "changes since divergence"
https://github.com/{user}/{repo}/compare/master@{1.day.ago}...master   # TIME TRAVEL: what changed in the last day (braces must be URL-encoded as %7B %7D)
https://github.com/{user}/{repo}/compare/master@{2014-10-04}...master  # date form YYYY-MM-DD
```

Append `.diff` or `.patch` to any compare/PR URL for plain-text output (302 → raw body; follow the redirect). Verified: `pull/386.diff`, `compare/master...master.diff`.

**Cross-fork compare:** `{foreign-user}:{branch}...{own-branch}` — e.g.
`https://github.com/{user}/{repo}/compare/{fork}:master...master`. Verified live with a real fork; note GitHub canonicalizes it to the FORK's repo view (`/shinyoung0905-byte/github-cheat-sheet/compare/master...tiimgreen:github-cheat-sheet:master`) — same content, different URL.

**Commit history by author:** append `?author={user}` to a commits page (e.g. `/commits/master?author=dhh`). 200 OK live.

## Line anchors and permalinks

- `#L53` highlights one line; `#L53-L60` a range — works on any blob URL, also how you deep-link "look at exactly this" in reviews.
- Press **y** while viewing a file to freeze the branch name into a commit SHA (`/blob/<sha>/path`) — the permanent link that survives force-pushes and rebases.

## Gists are real git repositories

```bash
git clone https://gist.github.com/{user}/{id}     # verified live: ls-remote returns refs (master)
# then edit, commit, push normally to update the gist in place
```

- All files must sit at the repo root — **no directories** in a gist.
- Append `.pibb` to any gist URL for an HTML-only embeddable version of it (verified 200 OK).
- Gists are fine for single-file snippets; anything with structure belongs in a real repo.

## User and repo endpoints that don't need the API

```text
https://github.com/{user}.keys    # plain-text list of all public SSH keys — verified 200 (octocat.keys)
https://github.com/{user}.png     # avatar; 302-redirects to the CDN image, fine in <img> tags
https://github.com/{repo}?template=1   # "use as template" URL for any repo enabled as a template — verified 200 on a live isTemplate repo
```

Repo templates (Settings → General → Template repository) let anyone clone your directory structure/files without the history — the boilerplate/tutorial pattern. The web button says **Use this template**; the `?template=1` URL does the same and is shareable.

## Keyboard shortcuts still current (per github/docs, 2026-09-10)

Press **?** on any GitHub page for the full context-sensitive list; these are the ones that earn muscle memory:

| Key | Where | Action |
|---|---|---|
| `t` | repo code view | file finder (fuzzy jump to a file) |
| `l` | blob view | jump to line number input |
| `w` | repo code view | switch branch/tag without leaving the page |
| `y` | any blob URL | expand to canonical commit-SHA permalink |
| `i` / `a` | PR diff | show/hide comments / annotations on diffs |
| `s` or `/` | site-wide | focus search (↓ = all-of-GitHub) |
| `g n` | site-wide | go to notifications |
| `c`, `u`, `L`, `M` | issue/PR lists | new issue / filter author / labels (Alt+click a label excludes it) / milestones |

Cheat-sheet-era drift: old docs said `l` edited labels on an open issue — current behavior is line-jump in code view and **uppercase** `L` for the label filter. Trust the live `?` dialog over any list, including this one.

## Closing issues from commit messages (semantics that bite)

Keywords: `fix/fixes/fixed`, `close/closes/closed`, `resolve/resolves/resolved` + issue number.

- **Closes only when the commit lands on the DEFAULT branch.** On a feature branch it merely *references* the issue — this is deliberate so open status tracks what's actually shipped (confirmed against current docs; original design note: github.blog/defunkt 2013).
- **Multiple issues need the keyword before EACH number**: `Closes #4, closes #5` works; `Closes #4, #5` only closes #4. The comma-list form that used to work no longer does.
- **Cross-repo closing** works — `fixes user/repo#45` in a commit message closes the issue in another repo, provided you have push permission there.

Issue cross-links inside comments/PRs: same repo = bare `#12`; other repo = `{user}/{repo}#12`. Both auto-link; no markdown syntax needed.

## Issue & PR search qualifiers (verified live against rails/rails via the search API)

```text
is:issue label:activerecord        # filtered by label
is:issue -label:activerecord       # NEGATION — everything NOT labeled that
is:pr is:merged                    # see MERGED pull requests (the open/closed tabs hide them; 26,883 hits on rails/rails)
status:success                     # PRs whose check runs are all green (2,450 on rails/rails)
```

`gh issue list --search "is:pr is:merged status:success"` takes the same qualifier string — this is how you find "PRs that passed CI" without paging UI.

## GitHub-flavored markdown facts worth knowing

- **Task lists**: interactive checkboxes in issues/PRs (`- [ ] item`, space after bracket required; clicking updates the stored markdown); read-only checklists render in ALL other markdown files (README, wiki).
- **Relative links** are recommended for internal doc links — `#header` anchors and `docs/readme` file paths survive repo renames, user changes, and forks; absolute URLs rot on every one of those events.
- **CSV/TSV render as tables** in the browser (verified 200 on a live .csv blob) — good reason to keep small datasets as committed CSV rather than screenshots. PDFs also render inline. YAML frontmatter at the top of a doc renders as a horizontal key/value table.
- **Rendered prose diffs**: markdown commits/PRs have a Source | Rendered toggle so you review the document, not the syntax. GitHub also diff-renders images (incl. PSD layers) and geodata as maps — per current docs; useful to know they exist when reviewing asset-heavy PRs.
- **Emoji** work in issues/PRs/comments/repo descriptions via `:name:` (`:shipit:`, `:+1:`, `:-1:` are the classics). Language detection/highlighting is Linguist (github/linguist) — its languages.yml is the source of truth for valid fence tags.
- **Quick quote**: in any comment thread, highlight text and press `r` → it lands in your composer as a blockquote. Pasting a screenshot straight from the clipboard into an issue/PR comment box auto-uploads it (desktop browsers).

## Stale / dead — do NOT follow these cheat-sheet sections

| Item | Status 2026-09-10 |
|---|---|
| **git.io** URL shortener (`curl -F "url=..." http://git.io`) | Creation is DEAD — live page says *"Git.io URL shortening service is no longer accepting new links."* Old shortcuts still resolve. Use plain URLs or `gh`-generated permalinks instead. |
| **hub** (github/hub CLI wrapper) | Repo moved to `mislav/hub`, in maintenance mode since Feb 2024 (no releases). `gh` covers every workflow this brain documents — don't install hub for new work. |
| **Travis CI on PRs** (`travis-ci.org`) | OSS Travis shut down (2021); the section is historical. Current path: GitHub Actions + commit statuses, see `ci-troubleshooting.md`. The underlying Commit Status API it referenced still exists and powers check runs. |
