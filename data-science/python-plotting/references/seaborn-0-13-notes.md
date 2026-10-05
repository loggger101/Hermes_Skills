---
description: "seaborn 0.13.2 on pandas 3.0 / matplotlib 3.11 / Python 3.14: 24 common calls run; deprecations that vanish in 0.14 (palette without hue, ci, distplot, shade), calls that fail, and new warnings"
source_repo: mwaskom/seaborn (BSD-3-Clause)
tested_version: "seaborn 0.13.2 (latest release, 2024-01-25) + matplotlib 3.11.2 + pandas 3.0.6 + numpy 2.5.3 on Python 3.14.6, Windows, Agg backend, warnings forced to 'always'; main branch inspected via the GitHub API (last commit 2026-07-06, unreleased)"
verified_date: "2026-10-05"
---

# seaborn 0.13.2 against the 2026 stack

The `SKILL.md` quick reference (`sns.barplot(x=, y=, data=)`, `heatmap(df.corr())`) predates several removals. Release
state: the latest tag is **v0.13.2 (2024-01-25)**; `main` kept moving until at least 2026-07-06 (docs, histplot weights fix,
relplot legend fix) with `numpy>=2.0`, `pandas>=2.2`, `matplotlib>=3.9`, `Python>=3.10` in its `pyproject.toml`, none of it released.
`pip install seaborn` gives 0.13.2. Install from git only if you need a main-branch fix.

## 24 calls, one run each (pandas 3 string dtype in the frame)

| Call | Result |
|---|---|
| `barplot(df, x='cat', y='num', palette='Set2')` | works, **FutureWarning**: passing `palette` without assigning `hue` is deprecated and will be removed in v0.14.0. Fix: also `hue='cat', legend=False` (works, silent) |
| `lineplot(..., ci=95)` | works, FutureWarning: `ci` deprecated; use `errorbar=('ci', 95)` (works, silent) |
| `distplot(df['num'])` | works, UserWarning: deprecated, removed in 0.14.0; use `displot` / `histplot` |
| `kdeplot(df['num'], shade=True)` | works, FutureWarning: `shade` deprecated for `fill`, an error in 0.14.0 |
| `heatmap(df.corr(), annot=True)` with string columns | **ValueError: could not convert string to float: 'c'** (raised by `DataFrame.corr()`); fix `df.corr(numeric_only=True)` |
| `FacetGrid(df, col='cat', size=2)` | **TypeError: unexpected keyword argument 'size'**; the keyword is `height` |
| `boxplot(x='cat', y='num', data=df)` | works, but **MatplotlibDeprecationWarning**: `vert: bool` deprecated in Matplotlib 3.11, removed in 3.13 (raised from inside seaborn) |
| `seaborn.objects`: `so.Plot(...).add(so.Dot()).plot()` and `.add(so.Bar(), so.Agg())` | work, but emit **Pandas4Warning**: the `copy` keyword is deprecated (Copy-on-Write is on in pandas 3) |
| `histplot(bins=30, kde=True)`, `kdeplot(fill=True)`, `regplot`, `pairplot(hue=)`, `countplot`, `catplot(kind='bar', hue=)`, `displot(kind='kde', multiple='fill')`, `violinplot(split=True)`, `FacetGrid(height=2).map(...)`, `sns.set()`, `set_theme(style='whitegrid')`, `savefig(bbox_inches='tight')` | all work with no warning |

Take-aways:

- **Pandas 3's default `str` dtype is fine** for `countplot`, `pairplot(hue=)`, `barplot` and the objects interface.
- Expect the four 0.14 removals above to break code that is silent today. Write the replacement forms now.
- seaborn 0.13.2 on a future matplotlib 3.13 will hit the removed `vert` argument inside `boxplot`; pin
  `matplotlib<3.13` or move to a seaborn release/main that has changed it. I did not test either (PyPI's newest matplotlib was
  3.11.2 when checked) and did not confirm that main already fixes it.
- Run notebooks with `-W error::FutureWarning` (or `python -W error::FutureWarning`) once before upgrading, to find the
  four patterns.

## Updated quick reference

```python
import seaborn as sns
sns.set_theme(style="whitegrid")
sns.histplot(df, x="col", bins=30, kde=True)
sns.boxplot(df, x="cat", y="num")                              # data first; keyword data= still works
sns.barplot(df, x="cat", y="num", hue="cat", palette="Set2", legend=False)
sns.lineplot(df, x="when", y="num", errorbar=("ci", 95))
sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="coolwarm")
g = sns.FacetGrid(df, col="cat", height=2); g.map(plt.hist, "num")
sns.displot(df, x="num", hue="cat", kind="kde", multiple="fill")
```

Not run: interactive backends, `jointplot`, `clustermap`, `relplot` legends, categorical `dodge`/`native_scale`, the docs
build, or any pandas 2.x / numpy 1.x combination.
