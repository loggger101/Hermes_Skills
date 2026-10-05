---
description: "statsmodels 0.15.0 on pandas 3.0 / Python 3.14: no-constant R-squared 0.27 vs 0.66, silent add_constant skip, misleading predict error for unseen levels, term order, degenerate proportion CIs, ARIMA without freq"
source_repo: statsmodels/statsmodels (BSD-3-Clause)
tested_version: "statsmodels 0.15.0 + pandas 3.0.6 + numpy 2.5.3 + scipy 1.18.1 + patsy 1.0.3 on Python 3.14.6 (Windows, uv venv); about 30 calls in two scripts, warnings forced on, seeded data (n=200, true model y = 2 + 1.5x + group effect + noise)"
verified_date: "2026-10-05"
---

# statsmodels 0.15.0 (pandas 3 era): measured traps

Installs and runs on Python 3.14 with pandas 3 (string dtype columns work in formulas). The traps below are behaviours of the
library; each was produced by one call on seeded data.

## Regression setup

| Call | Result |
|---|---|
| `smf.ols('y ~ x + C(g)', df)` with `g` a pandas 3 `str` column | works: `['Intercept', 'C(g)[T.b]', 'C(g)[T.c]', 'x']`, R-squared 0.904. `'y ~ x + g'` (no `C()`) gives the same dummies |
| `sm.OLS(y, X)` without `add_constant` (X has only `x`) | no intercept, silently: slope 1.465 and **R-squared 0.27 (uncentred)**, versus **0.663** with `sm.add_constant(X)` on the same data. Never compare the two R-squared values |
| `sm.add_constant(frame_with_a_constant_column)` | **adds nothing** (default `has_constant='skip'`): columns stayed `['c', 'x']`. `has_constant='add'` gave `['const', 'c', 'x']` (perfectly collinear) |
| NaN in `x`, formula API | rows dropped silently: `nobs` 190 of 200. `sm.OLS(..., missing='none')` (the default for arrays) raises `MissingDataError: exog contains inf or nans`; `missing='drop'` gives nobs 190 |
| Parameter order | with formulas it is `Intercept`, then **categorical dummies**, then numeric terms: `y ~ x + C(g)` and `y ~ C(g) + x` both give `[Intercept, C(g)[T.b], C(g)[T.c], x]`; `y ~ x + I(x**2) + C(g)` ends `[..., x, I(x ** 2)]`. Index results by name (`m.params['x']`), never by position: `m.get_robustcov_results('HC3').bse[1]` returned the standard error of the `b` dummy (0.0925), not of `x` (0.0486 from `fit(cov_type='HC3')`) |

## Prediction

| Call | Result |
|---|---|
| `m.predict(DataFrame({'x':[0.0], 'g':['b']}))` | `[2.952]` |
| Same with an **unseen level** `'d'` | `PatsyError: predict requires that you use a DataFrame when predicting from a model that was created using the formula api`. **That headline is misleading**: a DataFrame was passed. The real cause is two levels down in the chain: `observation with value 'd' does not match any of the expected levels (expected: ['a', 'b', 'c'])`, then `KeyError: 'd'`. Read `e.__cause__` |
| Declare the level up front: `pd.Categorical(g, categories=['a','b','c','d'])` | predicts, but fits with `SingularMatrixWarning: The design matrix is rank-deficient` (the `d` dummy is all zero) and the `d` row is predicted as the baseline-like value (-0.009 here) without any error. A never-seen level has no estimate |

## Inference helpers

| Call | Result |
|---|---|
| `fit(cov_type='HC3')` vs default for `x` | standard error 0.0486 robust vs 0.0421 classical (homoskedastic data, so close) |
| `multipletests(p, method='holm')` on `[.001,.01,.02,.04,.3,.6]` | corrected `[0.006, 0.05, 0.08, 0.12, 0.6, 0.6]`; `fdr_bh` gives `[0.006, 0.03, 0.04, 0.06, 0.36, 0.6]`; the return tuple is `(reject, p_corrected, alpha_sidak, alpha_bonf)`, so corrected p-values are `[1]`, not `[0]` |
| `proportions_ztest(45, 100, value=0.5)` | `z = -1.005, p = 0.3149` |
| `proportion_confint(45, 100)` default (`normal`) vs `wilson` | (0.3525, 0.5475) vs (0.3561, 0.5476) |
| `proportion_confint(0, 20)` | normal gives **(0.0, 0.0)**, a degenerate interval; `method='wilson'` gives (0.0, 0.161). Use Wilson (or `beta`) for small counts and zero events |
| `TTestIndPower().solve_power(effect_size=0.5, power=0.8, alpha=0.05)` | 63.8 per group (round up to 64) |
| `summary()` text | 27 lines, widest 91 characters: wraps in narrow terminals |

## Time series

- `ARIMA(ts, order=(1,1,0))` on a daily `DatetimeIndex` with a frequency: fits (AR coefficient 0.257).
- The same series with two days removed (no inferable frequency): fits (0.208) but warns `ValueWarning: A date index has been
  provided, but it has no associated frequency information and so will be ignored when e.g. forecasting.` The gaps are
  treated as consecutive steps. Reindex to a regular frequency (and fill or model the gaps) before fitting.

## Habits that avoid these

1. Use formulas for categorical models, or `sm.add_constant` on a copy and check `m.params.index`.
2. Report `m.nobs` next to every fit, so silent row drops show.
3. For prediction, fix categories at fit time with a consistent `pd.Categorical`, and handle unseen levels explicitly.
4. Select coefficients by name; keep `m.summary().as_text()` out of fixed-width layouts.
5. Prefer Wilson intervals and a multiple-testing correction whose output tuple you index deliberately.

Not run: GLM and discrete-choice families, mixed models, `statsmodels.stats.anova`, diagnostics (`het_breuschpagan`, `acorr_ljungbox`),
SARIMAX, plotting, and pandas 2.x / numpy 1.x combinations.
