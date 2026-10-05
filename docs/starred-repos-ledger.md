# Starred-repo review ledger

Working list for the review of the owner's GitHub stars (`gh api user/starred`, 166 repos on 2026-10-05).
Each repo is reviewed **one at a time**: read it (README, layout, source where it matters), decide what
it teaches that no existing skill already holds, fold that into a skill or reference, then flip its
row here and commit. Nothing batches across repos, so a session cut-off loses at most one repo.

## How to resume

1. Read this file; take the first row whose Status is `pending` (the table is in work order).
2. Review that repo (`gh repo view`, `gh api repos/OWNER/NAME/contents`, clone to the scratchpad if source matters).
3. Search the repo for what already covers it: `grep -ril NAME .` and `SKILLS-INDEX.md`.
4. Edit or add the skill / reference. A new `references/*.md` needs `python tools/gen-references-index.py` and the reference-doc count in `DESCRIPTION.md` bumped; a NEW SKILL also needs a line in its category `DESCRIPTION.md`, then run `gen-skills-index.py`, `gen-code-index.py`, `regen-dependency-map.py`, `gen-claude-plugin.py`, and bump the hand-kept counts in `README.md` (skills total, xrefs, category row, plugin-exposed) and `DESCRIPTION.md` — `verify-all.py` names each wrong number. If the router-coverage gate flags the new skill (in scope by tag, e.g. `code-review`), add it to a lane in `software-development/skill-flow-router/SKILL.md`. Then run `python tools/verify-all.py` (all gates must pass).
5. Set the row to `done` with a one-line outcome and the commit's round tag; commit; next row.

Statuses: `pending` · `done` (skill/reference changed) · `covered` (already well held, nothing to add) · `skip` (no skill-relevant content, with reason).

`Hits` = number of files in this repo that mention the repo's name before the review started (0 = never mentioned; short generic names inflate it).

| # | Repo | Lang | Pushed | Hits | Status | Outcome |
|---|------|------|--------|------|--------|---------|
| 1 | [agiwhitelist/auteur](https://github.com/agiwhitelist/auteur) | JavaScript | 2026-08-06 | 0 | done | round-67: new `creative/awwwards-gsap-motion/references/acceptance-gates.md` (linter rules, DPR2/headed/prod perf honesty, serve-over-HTTP, fallback payload); `transition: all` removed from design-taste-frontend |
| 2 | [alibaba/open-code-review](https://github.com/alibaba/open-code-review) | Go | 2026-10-01 | 0 | done | round-68: new `github/github-code-review/references/large-changeset-review-protocol.md` (git-built file list, bundling/rule groups, coverage accounting, position verification) |
| 3 | [AndrewAnnex/SpiceyPy](https://github.com/AndrewAnnex/SpiceyPy) | Python | 2026-09-27 | 0 | done | round-69: new `data-science/astro-toolkit-selection/references/spiceypy-notes.md` (live-verified: empty-pool errors, 80-char pool truncation, SPICE AU vs IAU, asteroid ids) |
| 4 | [ant-design/ant-design](https://github.com/ant-design/ant-design) | TypeScript | 2026-10-05 | 0 | done | round-70: new `creative/design-md/references/antd-v6-design-md-exemplar.md` (real DESIGN.md exemplar, v6 ConfigProvider theming levers, AGENTS.md rule patterns); pointers from design-md and frontend-design |
| 5 | [cathrynlavery/repo-atlas](https://github.com/cathrynlavery/repo-atlas) | Python | 2026-08-05 | 0 | done | round-71: NEW skill `software-development/repo-atlas` (in-repo atlas docs + `--write`/`--check` drift gate); generator run live on Windows, upstream utf-8 crash patched, non-fixed-point first write and changelog-staleness documented |
| 6 | [cloudflare/wrangler-action](https://github.com/cloudflare/wrangler-action) | TypeScript | 2026-09-28 | 0 | done | round-72: new `web-development/publish-site/references/cloudflare-ci-wrangler-action.md` (wrangler-action v4 inputs/outputs from action.yml, Pages + Workers + preview-per-PR workflows, pitfalls); source-read only |
| 7 | [cool-RR/PySnooper](https://github.com/cool-RR/PySnooper) | Python | 2026-06-08 | 0 | done | round-73: `software-development/python-debugpy` Recipe 6 (PySnooper tracing for agents); live-verified normalize leaves Elapsed time, watch_explode ignores max_variable_length, PYSNOOPER_DISABLED read at import |
| 8 | [CS-SI/Orekit](https://github.com/CS-SI/Orekit) | Java | 2026-10-04 | 0 | done | round-74: new `data-science/astro-toolkit-selection/references/orekit-python-notes.md` (orekit-jpype + jdk4py pip-only setup live-verified on Windows py3.14; Kepler run; UTC/ITRF need orekit-data) |
| 9 | [csscomb/csscomb.js](https://github.com/csscomb/csscomb.js) | JavaScript | 2023-01-03 | 0 | done | round-75: `web-development/static-site-patterns` new section "CSS: property ordering and lint (use stylelint, not csscomb)"; live-verified csscomb 4.3.0 throws on CSS nesting and its CLI no-ops silently, stylelint 17 + recess-order works |
| 10 | [Cyan4973/xxHash](https://github.com/Cyan4973/xxHash) | C | 2026-09-20 | 0 | done | round-81: new `data-science/bit-identity-float-pipelines/references/hashing-floats-xxhash.md` (xxh3 vs sha256 bandwidth measured, known-answer vectors, six canonical-bytes traps reproduced: -0.0, NaN payload, endianness, dtype, order, shape) |
| 11 | [Delgan/loguru](https://github.com/Delgan/loguru) | Python | 2026-10-03 | 0 | done | round-77: new `software-development/python-craft/references/logging-loguru.md` (loguru 0.7.3 run live: brace-format KeyError with args, diagnose=True leaks local values, ANSI in captured stderr, rotation/retention, stdlib interception) |
| 12 | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | JavaScript | 2026-10-05 | 0 | done | round-78: NEW skill `software-development/ponytail` (7-rung minimal-code ladder + diff-review/repo-audit/debt-ledger modes, six tagged findings); debt grep run live; routed in skill-flow-router; vendor benchmark labelled as vendor-only |
| 13 | [dtamayo/reboundx](https://github.com/dtamayo/reboundx) | Jupyter Notebook | 2026-08-21 | 0 | done | round-76: new `data-science/astro-toolkit-selection/references/rebound-n-body-notes.md` (REBOUNDx sdist-only/needs compiler verified; REBOUND 5.2.1 run live, G-unit gotcha; Yarkovsky params). REBOUND repo row (hannorein/rebound) can reuse this note |
| 14 | [enaqx/awesome-react](https://github.com/enaqx/awesome-react) | - | 2026-09-04 | 0 | done | round-79: NEW skill `web-development/react-ecosystem` (defaults-by-need table + freshness traps) + `references/awesome-react-map.md` (every pick with npm latest/modified, checked 2026-10-05; flags refine placeholder, loadable-components deprecated, react-uploady 404). Later React-cluster rows (react, next.js, zustand, shadcn, motion, remotion, react-native, react-navigation, ionic) should extend this skill |
| 15 | [esa/pykep](https://github.com/esa/pykep) | C++ | 2026-10-03 | 0 | done | round-80: new `data-science/astro-toolkit-selection/references/pykep-v3-notes.md` (PyPI JSON-verified: pykep 3.0.1 manylinux-only wheels, exact heyoka pin; API map from docs; not run). Also fixes react-uploady package name |
| 16 | [evanw/esbuild](https://github.com/evanw/esbuild) | Go | 2026-08-09 | 0 | done | round-82: `web-development/static-site-patterns` new section "Optional build step: esbuild" (0.28.2 run live: tree-shaking, CSS emitted beside JS not injected, target lowering of ?? and CSS nesting, no type-checking) |
| 17 | [evenfurther/pathfinding](https://github.com/evenfurther/pathfinding) | Rust | 2026-09-30 | 0 | done | round-83: new `data-science/algorithms-python-catalog/references/graph-algorithms-library-map.md` (crate module list -> scipy.sparse.csgraph/networkx; zero-weight-edge CSR trap, assignment direction, integer-capacity flow all run live) |
| 18 | [faif/python-patterns](https://github.com/faif/python-patterns) | Python | 2026-10-02 | 0 | done | round-84: new `software-development/python-craft/references/gof-patterns-in-python.md` (pattern -> idiom table; 19 runnable idioms all asserted; len(proxy) and functools.cache-keeps-self claims verified) |
| 19 | [FavioVazquez/ds-cheatsheets](https://github.com/FavioVazquez/ds-cheatsheets) | - | 2024-07-18 | 0 | skip | Link list to ~70 human-oriented PDF cheat sheets (pandas, R, Keras, SQL...), no procedural content to port; the topics are held by python-data-science, sql-for-data, duckdb-querying, streamlit-dashboards, mlops skills. No file changes. |
| 20 | [fitzgen/bumpalo](https://github.com/fitzgen/bumpalo) | Rust | 2026-09-16 | 0 | done | round-86: NEW skill `software-development/rust-crate-picks` (decision table; entries so far bumpalo, pathfinding) + `references/bumpalo-arena-notes.md` (no-Drop rule, reset, features, Send not Sync; source-read, no Rust toolchain here). Later Rust rows (uom, hifitime, EGObox, gpui-kit) should add rows to this skill |
| 21 | [GSA/data.gov](https://github.com/GSA/data.gov) | Python | 2026-10-01 | 0 | done | round-87: new `data-science/space-data-pipelines/references/data-gov-catalog-api.md` + SKILL section: live-probed that catalog.data.gov dropped CKAN /api/3/action (404), documents /search cursor pagination, org_slug trap (nasa not nasa-gov), missing distributions |
| 22 | [gto76/python-cheatsheet](https://github.com/gto76/python-cheatsheet) | Python | 2026-07-29 | 0 | done | round-88: new `software-development/python-craft/references/stdlib-traps-windows.md` (probe run on 3.14.6/Windows: open() cp1252 mojibake without error, csv \r\r\n, os.rename FileExistsError, rmtree PermissionError, strftime %-d, json NaN; also non-traps: sum is exact on 3.14, long paths, time granularity) |
| 23 | [hannorein/rebound](https://github.com/hannorein/rebound) | C | 2026-09-29 | 0 | done | round-89: `rebound-n-body-notes.md` extended with REBOUND 5.2.1 live results: WHFast dt table vs IAS15 on e=0.9 orbit (garbage at dt>=0.01), bit-identical restart from save_to_file/Simulationarchive, default yr2pi units, Horizons add() side effects |
| 24 | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | TypeScript | 2026-10-05 | 0 | done | round-90: NEW skill `creative/hyperframes-video` (HTML+GSAP -> deterministic MP4). Run live on Windows: planted-defect lint (media_missing_id, audio_src_not_found, gsap_animates_clip_element), 2s render 6.9s, two renders byte-identical + 48 identical frame hashes, telemetry on by default, CDN GSAP in scaffold |
| 25 | [HIPS/autograd](https://github.com/HIPS/autograd) | Python | 2026-10-01 | 0 | done | round-91: new `data-science/python-data-science/references/autograd-notes.md` (autograd 1.9.1 / numpy 2.5 run live: working calls, int-input, non-scalar, in-place, sqrt-at-0 errors, double-where guard, check_grads) |
| 26 | [hoffstadt/DearPyGui](https://github.com/hoffstadt/DearPyGui) | C++ | 2026-05-13 | 0 | done | round-92: new `frontend-design/nicegui-app-builder/references/python-gui-toolkits.md` (toolkit chooser + Dear PyGui 2.3.1 headless probe: segfault rc 139 on any call outside create/destroy_context, duplicate tag SystemError then orphaned alias). Kivy and PySimpleGUI rows should extend this file |
| 27 | [igorbarinov/awesome-data-engineering](https://github.com/igorbarinov/awesome-data-engineering) | - | 2026-09-07 | 0 | done | round-93: new `data-science/build-systems-data/references/data-engineering-tool-map.md` (PyPI JSON freshness for 25 tools; dry-run proved pip on Python 3.14 silently resolves great-expectations 0.18.22 and luigi 3.6.0; bruin/evidence PyPI name collisions) |
| 28 | [iliekturtles/uom](https://github.com/iliekturtles/uom) | Rust | 2026-04-23 | 0 | done | round-94: `rust-crate-picks` gains uom row + `references/uom-units-notes.md` (README/crates.io; Python analogue pint 0.26.1 run live: dimension errors, degC offset trap, AU=149597870.7, year=365.25 d); python-craft Windows pitfalls gains the pip silent-old-version trap |
| 29 | [isl-org/Open3D](https://github.com/isl-org/Open3D) | C++ | 2026-09-30 | 0 | pending | |
| 30 | [Karmanplus/prospector](https://github.com/Karmanplus/prospector) | Python | 2026-09-15 | 0 | pending | |
| 31 | [kivy/kivy](https://github.com/kivy/kivy) | Python | 2026-10-03 | 0 | pending | |
| 32 | [Kristories/awesome-guidelines](https://github.com/Kristories/awesome-guidelines) | JavaScript | 2026-09-28 | 0 | pending | |
| 33 | [LeCoupa/awesome-cheatsheets](https://github.com/LeCoupa/awesome-cheatsheets) | JavaScript | 2026-04-12 | 0 | pending | |
| 34 | [leonardomso/33-js-concepts](https://github.com/leonardomso/33-js-concepts) | JavaScript | 2026-09-10 | 0 | pending | |
| 35 | [loggger101/asteroid-belt-gradient](https://github.com/loggger101/asteroid-belt-gradient) | Python | 2026-09-28 | 0 | pending | |
| 36 | [longbridge/gpui-kit](https://github.com/longbridge/gpui-kit) | Rust | 2026-10-05 | 0 | pending | |
| 37 | [lukas-blecher/LaTeX-OCR](https://github.com/lukas-blecher/LaTeX-OCR) | Python | 2025-01-18 | 0 | pending | |
| 38 | [markusschanta/awesome-jupyter](https://github.com/markusschanta/awesome-jupyter) | - | 2026-10-05 | 0 | pending | |
| 39 | [mgramin/awesome-db-tools](https://github.com/mgramin/awesome-db-tools) | - | 2026-10-03 | 0 | pending | |
| 40 | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | Python | 2026-10-03 | 0 | pending | |
| 41 | [norvig/pytudes](https://github.com/norvig/pytudes) | Jupyter Notebook | 2026-10-02 | 0 | pending | |
| 42 | [nyx-space/hifitime](https://github.com/nyx-space/hifitime) | Rust | 2026-09-09 | 0 | pending | |
| 43 | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | JavaScript | 2026-10-05 | 0 | pending | |
| 44 | [piskvorky/gensim](https://github.com/piskvorky/gensim) | Python | 2025-11-01 | 0 | pending | |
| 45 | [plotly/plotly.py](https://github.com/plotly/plotly.py) | Python | 2026-10-05 | 0 | pending | |
| 46 | [poteto/hiring-without-whiteboards](https://github.com/poteto/hiring-without-whiteboards) | JavaScript | 2026-09-24 | 0 | pending | |
| 47 | [public-api-lists/public-api-lists](https://github.com/public-api-lists/public-api-lists) | - | 2026-09-14 | 0 | pending | |
| 48 | [PyCQA/pycodestyle](https://github.com/PyCQA/pycodestyle) | Python | 2026-09-29 | 0 | pending | |
| 49 | [pyenv/pyenv](https://github.com/pyenv/pyenv) | Shell | 2026-10-03 | 0 | pending | |
| 50 | [PySimpleGUI/PySimpleGUI](https://github.com/PySimpleGUI/PySimpleGUI) | Python | 2026-08-30 | 0 | pending | |
| 51 | [react-navigation/react-navigation](https://github.com/react-navigation/react-navigation) | TypeScript | 2026-10-02 | 0 | pending | |
| 52 | [relf/EGObox](https://github.com/relf/EGObox) | Jupyter Notebook | 2026-10-04 | 0 | pending | |
| 53 | [remotion-dev/remotion](https://github.com/remotion-dev/remotion) | TypeScript | 2026-10-04 | 0 | pending | |
| 54 | [roboflow/supervision](https://github.com/roboflow/supervision) | Python | 2026-10-05 | 0 | pending | |
| 55 | [ryanoasis/nerd-fonts](https://github.com/ryanoasis/nerd-fonts) | CSS | 2026-09-30 | 0 | pending | |
| 56 | [SeleniumHQ/selenium](https://github.com/SeleniumHQ/selenium) | Java | 2026-10-04 | 0 | pending | |
| 57 | [shadden/celmech](https://github.com/shadden/celmech) | Python | 2026-07-15 | 0 | pending | |
| 58 | [Tencent/WeKnora](https://github.com/Tencent/WeKnora) | Go | 2026-10-01 | 0 | pending | |
| 59 | [unclecode/crawl4ai](https://github.com/unclecode/crawl4ai) | Python | 2026-10-05 | 0 | pending | |
| 60 | [visgl/deck.gl](https://github.com/visgl/deck.gl) | TypeScript | 2026-10-05 | 0 | pending | |
| 61 | [xtekky/gpt4free](https://github.com/xtekky/gpt4free) | Python | 2026-10-05 | 0 | pending | |
| 62 | [yusufkaraaslan/Skill_Seekers](https://github.com/yusufkaraaslan/Skill_Seekers) | Python | 2026-09-30 | 0 | pending | |
| 63 | [567-labs/instructor](https://github.com/567-labs/instructor) | Python | 2026-10-01 | 1 | pending | |
| 64 | [dask/dask](https://github.com/dask/dask) | Python | 2026-09-29 | 1 | pending | |
| 65 | [dexteryy/spellbook-of-modern-webdev](https://github.com/dexteryy/spellbook-of-modern-webdev) | - | 2023-12-18 | 1 | pending | |
| 66 | [react/react-native](https://github.com/react/react-native) | C++ | 2026-10-05 | 1 | pending | |
| 67 | [sympy/sympy](https://github.com/sympy/sympy) | Python | 2026-10-05 | 1 | pending | |
| 68 | [terkelg/awesome-creative-coding](https://github.com/terkelg/awesome-creative-coding) | HTML | 2026-07-21 | 1 | pending | |
| 69 | [tt-a1i/archify](https://github.com/tt-a1i/archify) | JavaScript | 2026-10-05 | 1 | pending | |
| 70 | [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | JavaScript | 2026-09-14 | 2 | pending | |
| 71 | [ionic-team/ionic-framework](https://github.com/ionic-team/ionic-framework) | TypeScript | 2026-10-05 | 2 | pending | |
| 72 | [ripienaar/free-for-dev](https://github.com/ripienaar/free-for-dev) | HTML | 2026-10-04 | 2 | pending | |
| 73 | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) | Python | 2026-08-30 | 3 | pending | |
| 74 | [exaloop/codon](https://github.com/exaloop/codon) | Python | 2026-10-05 | 3 | pending | |
| 75 | [vectorize-io/hindsight](https://github.com/vectorize-io/hindsight) | Python | 2026-10-02 | 3 | pending | |
| 76 | [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | Python | 2026-10-03 | 4 | pending | |
| 77 | [pmndrs/zustand](https://github.com/pmndrs/zustand) | TypeScript | 2026-09-29 | 4 | pending | |
| 78 | [public-apis/public-apis](https://github.com/public-apis/public-apis) | Python | 2026-10-05 | 4 | pending | |
| 79 | [rlaope/oh-my-hermes](https://github.com/rlaope/oh-my-hermes) | Python | 2026-10-05 | 4 | pending | |
| 80 | [typpo/spacekit](https://github.com/typpo/spacekit) | JavaScript | 2026-04-10 | 4 | pending | |
| 81 | [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | - | 2026-10-02 | 4 | pending | |
| 82 | [loggger101/AsteroidCatalog](https://github.com/loggger101/AsteroidCatalog) | Python | 2026-09-29 | 5 | pending | |
| 83 | [loggger101/General_Research](https://github.com/loggger101/General_Research) | HTML | 2026-10-05 | 5 | pending | |
| 84 | [ranaroussi/yfinance](https://github.com/ranaroussi/yfinance) | Python | 2026-10-04 | 5 | pending | |
| 85 | [gradle/gradle](https://github.com/gradle/gradle) | Groovy | 2026-10-05 | 6 | pending | |
| 86 | [mwaskom/seaborn](https://github.com/mwaskom/seaborn) | Python | 2026-07-06 | 6 | pending | |
| 87 | [dvf/blockchain](https://github.com/dvf/blockchain) | C# | 2024-07-21 | 7 | pending | |
| 88 | [gztchan/awesome-design](https://github.com/gztchan/awesome-design) | - | 2024-07-04 | 7 | pending | |
| 89 | [loggger101/spacecost](https://github.com/loggger101/spacecost) | Python | 2026-10-04 | 7 | pending | |
| 90 | [NousResearch/hermes-agent-self-evolution](https://github.com/NousResearch/hermes-agent-self-evolution) | Python | 2026-06-17 | 7 | pending | |
| 91 | [PrefectHQ/prefect](https://github.com/PrefectHQ/prefect) | Python | 2026-10-05 | 8 | pending | |
| 92 | [simple-icons/simple-icons](https://github.com/simple-icons/simple-icons) | JavaScript | 2026-10-04 | 8 | pending | |
| 93 | [bilawalsidhu/gods-eye-view](https://github.com/bilawalsidhu/gods-eye-view) | JavaScript | 2026-10-05 | 9 | pending | |
| 94 | [tqdm/tqdm](https://github.com/tqdm/tqdm) | Python | 2026-09-20 | 9 | pending | |
| 95 | [nasa/aegis](https://github.com/nasa/aegis) | TypeScript | 2026-10-03 | 10 | pending | |
| 96 | [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop) | Python | 2026-09-02 | 10 | pending | |
| 97 | [statsmodels/statsmodels](https://github.com/statsmodels/statsmodels) | Python | 2026-10-04 | 10 | pending | |
| 98 | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) | JavaScript | 2026-10-03 | 11 | pending | |
| 99 | [DataExpert-io/data-engineer-handbook](https://github.com/DataExpert-io/data-engineer-handbook) | Jupyter Notebook | 2026-08-03 | 11 | pending | |
| 100 | [oxnr/awesome-bigdata](https://github.com/oxnr/awesome-bigdata) | - | 2026-07-31 | 11 | pending | |
| 101 | [astropy/astropy](https://github.com/astropy/astropy) | Python | 2026-10-02 | 13 | pending | |
| 102 | [htmlhint/HTMLHint](https://github.com/htmlhint/HTMLHint) | JavaScript | 2026-10-04 | 13 | pending | |
| 103 | [cupy/cupy](https://github.com/cupy/cupy) | Python | 2026-10-04 | 14 | pending | |
| 104 | [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer) | Python | 2026-09-15 | 14 | pending | |
| 105 | [lissy93/dashy](https://github.com/lissy93/dashy) | Vue | 2026-10-03 | 14 | pending | |
| 106 | [reconurge/flowsint](https://github.com/reconurge/flowsint) | TypeScript | 2026-10-03 | 14 | pending | |
| 107 | [pydantic/pydantic](https://github.com/pydantic/pydantic) | Python | 2026-10-02 | 15 | pending | |
| 108 | [skyfielders/python-skyfield](https://github.com/skyfielders/python-skyfield) | Python | 2026-09-29 | 15 | pending | |
| 109 | [nasa/cumulus](https://github.com/nasa/cumulus) | JavaScript | 2026-10-03 | 16 | pending | |
| 110 | [analysis-tools-dev/static-analysis](https://github.com/analysis-tools-dev/static-analysis) | Rust | 2026-10-02 | 17 | pending | |
| 111 | [julie-dujardin/space-map](https://github.com/julie-dujardin/space-map) | Python | 2026-10-05 | 17 | pending | |
| 112 | [sentrux/sentrux](https://github.com/sentrux/sentrux) | Rust | 2026-03-19 | 17 | pending | |
| 113 | [pygame/pygame](https://github.com/pygame/pygame) | C | 2025-11-01 | 18 | pending | |
| 114 | [CelestiaProject/Celestia](https://github.com/CelestiaProject/Celestia) | C++ | 2026-10-04 | 19 | pending | |
| 115 | [tensorflow/tensorflow](https://github.com/tensorflow/tensorflow) | C++ | 2026-10-05 | 19 | pending | |
| 116 | [thedaviddias/Front-End-Checklist](https://github.com/thedaviddias/Front-End-Checklist) | MDX | 2026-10-05 | 19 | pending | |
| 117 | [tiimgreen/github-cheat-sheet](https://github.com/tiimgreen/github-cheat-sheet) | - | 2024-04-15 | 19 | pending | |
| 118 | [esa/pygmo2](https://github.com/esa/pygmo2) | C++ | 2026-04-17 | 20 | pending | |
| 119 | [unslothai/unsloth](https://github.com/unslothai/unsloth) | Python | 2026-10-05 | 20 | pending | |
| 120 | [Z3Prover/z3](https://github.com/Z3Prover/z3) | C++ | 2026-10-05 | 21 | pending | |
| 121 | [Cyan4973/zstd](https://github.com/Cyan4973/zstd) | C | 2026-09-06 | 22 | pending | |
| 122 | [vercel/next.js](https://github.com/vercel/next.js) | JavaScript | 2026-10-05 | 23 | pending | |
| 123 | [Small-Bodies-Node/pds4_tools](https://github.com/Small-Bodies-Node/pds4_tools) | Python | 2026-02-14 | 24 | pending | |
| 124 | [blader/humanizer](https://github.com/blader/humanizer) | Python | 2026-09-28 | 25 | pending | |
| 125 | [cuspaceflight/CamPyRoS](https://github.com/cuspaceflight/CamPyRoS) | Jupyter Notebook | 2025-07-27 | 27 | pending | |
| 126 | [zauberzeug/nicegui](https://github.com/zauberzeug/nicegui) | Python | 2026-10-05 | 29 | pending | |
| 127 | [repowise-dev/repowise](https://github.com/repowise-dev/repowise) | Python | 2026-10-04 | 31 | pending | |
| 128 | [astropy/astroquery](https://github.com/astropy/astroquery) | Python | 2026-10-02 | 32 | pending | |
| 129 | [OpenSCvx/OpenSCvx](https://github.com/OpenSCvx/OpenSCvx) | Python | 2026-10-04 | 32 | pending | |
| 130 | [mesa/mesa](https://github.com/mesa/mesa) | Python | 2026-09-30 | 35 | pending | |
| 131 | [nyx-space/nyx](https://github.com/nyx-space/nyx) | Rust | 2026-10-02 | 36 | pending | |
| 132 | [Pyomo/pyomo](https://github.com/Pyomo/pyomo) | Python | 2026-09-30 | 38 | pending | |
| 133 | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | JavaScript | 2026-10-03 | 39 | pending | |
| 134 | [tech-leads-club/agent-skills](https://github.com/tech-leads-club/agent-skills) | TypeScript | 2026-09-20 | 39 | pending | |
| 135 | [juliensimon/space-datasets](https://github.com/juliensimon/space-datasets) | Python | 2026-10-04 | 40 | pending | |
| 136 | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | JavaScript | 2026-09-26 | 42 | pending | |
| 137 | [pola-rs/polars](https://github.com/pola-rs/polars) | Rust | 2026-10-04 | 42 | pending | |
| 138 | [streamlit/streamlit](https://github.com/streamlit/streamlit) | Python | 2026-10-05 | 43 | pending | |
| 139 | [pymc-devs/pymc](https://github.com/pymc-devs/pymc) | Python | 2026-10-02 | 46 | pending | |
| 140 | [duncaneddy/brahe](https://github.com/duncaneddy/brahe) | Rust | 2026-10-04 | 49 | pending | |
| 141 | [matplotlib/matplotlib](https://github.com/matplotlib/matplotlib) | Python | 2026-10-04 | 52 | pending | |
| 142 | [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | HTML | 2026-10-05 | 54 | pending | |
| 143 | [obra/superpowers](https://github.com/obra/superpowers) | Shell | 2026-09-27 | 56 | pending | |
| 144 | [tester-army/e2e](https://github.com/tester-army/e2e) | TypeScript | 2026-10-04 | 62 | pending | |
| 145 | [astral-sh/ruff](https://github.com/astral-sh/ruff) | Rust | 2026-10-04 | 65 | pending | |
| 146 | [scipy/scipy](https://github.com/scipy/scipy) | Python | 2026-10-04 | 67 | pending | |
| 147 | [affaan-m/ECC](https://github.com/affaan-m/ECC) | JavaScript | 2026-10-05 | 76 | pending | |
| 148 | [keon/algorithms](https://github.com/keon/algorithms) | Python | 2026-09-25 | 87 | pending | |
| 149 | [pytorch/pytorch](https://github.com/pytorch/pytorch) | Python | 2026-10-05 | 88 | pending | |
| 150 | [loggger101/economicspace](https://github.com/loggger101/economicspace) | Python | 2026-10-01 | 103 | pending | |
| 151 | [pandas-dev/pandas](https://github.com/pandas-dev/pandas) | Python | 2026-10-05 | 111 | pending | |
| 152 | [matthewholman/assist](https://github.com/matthewholman/assist) | Jupyter Notebook | 2026-06-21 | 141 | pending | |
| 153 | [d3/d3](https://github.com/d3/d3) | Shell | 2026-05-28 | 192 | pending | |
| 154 | [numpy/numpy](https://github.com/numpy/numpy) | Python | 2026-10-04 | 193 | pending | |
| 155 | [ajay-dhangar/algo](https://github.com/ajay-dhangar/algo) | TypeScript | 2026-10-04 | 196 | pending | |
| 156 | [TheAlgorithms/Java](https://github.com/TheAlgorithms/Java) | Java | 2026-10-04 | 214 | pending | |
| 157 | [pytest-dev/pytest](https://github.com/pytest-dev/pytest) | Python | 2026-10-05 | 264 | pending | |
| 158 | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | Python | 2026-10-05 | 266 | pending | |
| 159 | [oven-sh/bun](https://github.com/oven-sh/bun) | Rust | 2026-10-05 | 298 | pending | |
| 160 | [react/react](https://github.com/react/react) | JavaScript | 2026-10-02 | 319 | pending | |
| 161 | [astral-sh/uv](https://github.com/astral-sh/uv) | Rust | 2026-10-05 | 328 | pending | |
| 162 | [motiondivision/motion](https://github.com/motiondivision/motion) | TypeScript | 2026-10-05 | 484 | pending | |
| 163 | [standard/standard](https://github.com/standard/standard) | JavaScript | 2025-07-11 | 1025 | pending | |
| 164 | [mattpocock/skills](https://github.com/mattpocock/skills) | Shell | 2026-10-04 | 1305 | pending | |
| 165 | [TheAlgorithms/Python](https://github.com/TheAlgorithms/Python) | Python | 2026-10-05 | 1813 | pending | |
| 166 | [shadcn-ui/ui](https://github.com/shadcn-ui/ui) | TypeScript | 2026-10-05 | 3103 | pending | |
