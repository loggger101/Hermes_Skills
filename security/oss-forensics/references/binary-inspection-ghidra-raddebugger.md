---
description: "binary-inspection tooling read from primary source rather than remembered tutorials: Ghidra's headless analyzer (what it can do without a GUI, where analyzeHeadless actually lives in the master tree versus the release layout most guides assume, and its current JDK 25 / Gradle 9.1 build requirement) plus Epic's RAD Debugger stack — RDI debug-info format, radbin for dumping debug info standalone, and the RAD Linker including two documented Windows footguns (32-bit PDB table overflow on huge builds; large-pages mode fragmenting host memory until reboot)"
source_repo: NationalSecurityAgency/ghidra at master + EpicGames/raddebugger at master, 2026-11-04
tested_version: "**read from source** via the GitHub contents/code-search APIs and raw READMEs. Nothing was built or executed here (neither tool is installed on this box); path existence for `analyzeHeadless` was confirmed by code search rather than inferred"
verified_date: "2026-11-04"
---

# Ghidra headless, and Epic's RAD debugger / RDI / linker stack

## Ghidra — the parts that matter for automated inspection

The **Headless Analyzer** is a command-line, non-GUI Ghidra: it creates and populates projects, analyses imported or existing binaries, and runs non-GUI scripts (program-dependent or independent). Minimum invocation needs just project path + name; with more arguments it can import a file *or a directory recursively*, process executables already in a project, run any number of `-preScript` / `-postScript` GhidraScripts per executable, turn analysis on/off per executable, and write a log — **with separated logging available for scripts**, which is what makes bulk triage auditable (one script's output doesn't interleave with the whole import batch). That combination is the forensically useful shape: import a directory of samples, run your own post-script over each binary, get per-file evidence out without opening a GUI once.

**Path trap, verified.** Tutorials say "run `support/analyzeHeadless`". In the **source tree at master there is no top-level `support/`** — querying it returns 404 — because those scripts live at:

```
Ghidra/RuntimeScripts/support/analyzeHeadless
Ghidra/RuntimeScripts/support/analyzeHeadless.bat
Ghidra/RuntimeScripts/support/analyzeHeadlessREADME.md   <- the real usage doc, in-tree
```

The `support/…` layout people quote is what a **built or downloaded release** presents. So: clone master and you won't find it; download the release zip (or build) and you will. The implementation class is `ghidra.app.util.headless.AnalyzeHeadless`. And when you need flag semantics, read that in-tree README instead of recalling them — it documents parameter passing to scripts (`askXxx()` methods get consumed headlessly), analysis-timeout checks, passing values between scripts, and controlling program disposition from scripts.

**Build requirement is currently JDK 25 + Gradle 9.1.0+**, per the master README (wrapper acceptable when online): `gradle -I gradle/support/fetchDependencies.gradle` then `gradle buildGhidra`. Worth stating explicitly because Ghidra tutorials circulate for years with "JDK 17" or "JDK 21" and a stale version number is the usual reason a from-source build fails at the first task. Check the README of the tag you actually checked out rather than trusting any remembered number, including this one. Scripting languages are Java **or Python** (PyGhidra).

## Epic's RAD stack — debugger, RDI format, and a linker with two Windows footguns

Three separate technologies in one repo; only the first is what people mean by "raddebugger".

**RAD Debugger**: native, user-mode, multi-process GUI debugger, explicitly **ALPHA**, and today supporting **only local-machine x64 Windows debugging with PDBs**; Linux debugging and DWARF are stated intentions. Its own README also warns it does *not* document usage — the usage doc ships with releases / appears in `build/`. So don't design a cross-platform or CI RE workflow around it yet, and don't look for usage docs at the repo root.

**RDI (RAD Debug Info)**: their own debug-information format that the debugger parses *instead of* PDB/DWARF, with PDB converted in on demand (DWARF-in still in progress). Unusually for this space the format is specified **in code** — `src/lib_rdi/rdi.h`, `rdi.c` plus `rdi_parse.h/.c` for parsing helpers. The standalone takeaway: the **`radbin` utility** (also reachable via the debugger's `--bin`) converts native debug info to RDI *and produces textual dumps of an RDI file's contents* — a cheap way to inspect what debug information a binary actually carries, independent of any debugger session.

**RAD Linker** — the piece most likely to be useful here, and the one with sharp edges:

- New x64 PE/COFF linker optimised for **gigantic executables**; command-line syntax is **fully MSVC-compatible** (implemented switch list via `/help`), so it's a drop-in experiment rather than a migration.
- Their reported result on huge test cases (multiple gigabytes of debug info): about **50 % faster links**, with large-page mode adding roughly another 25 %.
- It emits standard PDBs, but can optionally write native RDI — and the reason given is a real failure mode worth knowing before you hit it: very large projects produce **"broken PDBs that overflow internal 32-bit tables"**. If a huge build's debugger experience degrades or PDB tooling misbehaves, this is a named cause with an alternative output format.
- `/rad_workers` limits link threads; **default is one thread per core**, so running several linkers in parallel silently oversubscribes the machine — cap it explicitly for parallel CI matrices.
- `/rad_large_pages`: on a normal Windows workstation this **"will fragment memory quickly, forcing a reboot"**; upstream recommends it *only* in Docker or VM images reset after each link. Actionable rule for this host: never enable large pages outside a disposable image.
- **No link-time optimisation yet** (roadmap), so it cannot replace MSVC's LTCG path for release builds — the stated use case is the compile-debug cycle of huge projects, not shipping optimised binaries.

## Two architecture patterns worth stealing from its source layout

Every layer carries a short uppercase prefix namespace (`demon`→`DEMON_`, `rdi`→`RDI_`, `regs`→`REGS_`, `render`→`R_`, `ui`→`UI_`, `text`→`TXT_`), so any symbol names its owning layer without a module system — cheap, greppable discipline for hand-written C.

Build-time codegen is explicit and observable in the build log: *"parsing metadesk… 16 metadesk files parsed → gathering tables… 97 tables found → generating layer code"*. Layer boilerplate comes from metadata rather than repetition. Note also `render`'s stated boundary — it deliberately does **not** implement a high-level drawing API ("strictly for minimally abstracting on an as-needed basis"), with higher-level drawing kept in a separate `draw` layer: abstraction layers that declare what they refuse to provide, like the RAD docs' per-layer non-responsibilities discussed in `skill-intake-and-release/references/two-external-skill-packs-reviewed.md`.
