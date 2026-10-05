---
description: "yfinance 1.7.0 as economicspace uses it (Ticker.history 5d on HG/GC/SI/PL/PA=F): failures are logged not raised, last bar can be an in-progress session, TIO=F data conflicts with the pipeline's CNY note"
source_repo: ranaroussi/yfinance (Apache-2.0) as called from economicspace master.py fetch_yfinance (lines 2539-2603 read)
tested_version: "yfinance 1.7.0 + pandas 3.0.6 on Python 3.14.6 (Windows, uv venv); live requests to Yahoo Finance on Mon 2026-10-05 around 08:20-08:30 EDT. Yahoo's API is unofficial, so every number here is a snapshot"
verified_date: "2026-10-05"
---

# yfinance, as the pipeline calls it

`economicspace` Stage 2 (`master.py::fetch_yfinance`, mirrored in `modules/mineral_value.py`) takes each reference row with a
`yfinance_ticker` (`HG=F` copper USD/lb, `GC=F` gold, `SI=F` silver, `PL=F` platinum, `PA=F` palladium, all USD/troy oz except
copper), calls `yf.Ticker(t).history(period="5d", auto_adjust=False)`, takes the last non-NaN `Close`, and converts to USD/kg.
This note records what that call returns today. See `data-sources-environment-entrypoints.md` for why soft price failures
matter.

## What the call returns (run)

| Check | Result |
|---|---|
| Install | `pip install yfinance` gives 1.7.0 on Python 3.14.6 with pandas 3.0.6, no build step |
| Five tickers, `history(period="5d", auto_adjust=False)` | 4 rows each (a weekend inside the window), 8 columns `Open High Low Close Adj Close Volume Dividends Stock Splits`, index tz `America/New_York`, dtype `datetime64[s, America/New_York]`. First call ~3 s, then ~0.2 s |
| Last closes | HG 6.624, GC 4184.0, SI 61.975, PL 1745.3, PA 1183.5 (all dated 2026-10-05) |
| `history()` default | `auto_adjust=True`: the `Adj Close` column is dropped (7 columns). The pipeline passes `auto_adjust=False` explicitly, so keep it |
| `yf.download([...])` | MultiIndex columns `(field, ticker)`; even a single ticker comes back as a MultiIndex in 1.7.0 |

## Failures do not raise (run)

| Input | Result |
|---|---|
| Unknown ticker `ZZZZNOPE=F` | **no exception**, empty DataFrame with 6 columns; the only trace is a log line `HTTP Error 404 ... Quote not found` and `No data found, symbol may be delisted` on the `yfinance` logger |
| Invalid period `'5dd'` | no exception, empty DataFrame, log line listing the valid periods (`1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max`) |

So the `except Exception` branch in `fetch_yfinance` is not what catches a bad or blocked ticker; the `closes.empty` branch
(`WARN ... no close data`) is. That is consistent with the "fails softly" design, but note the error text never reaches the
run output unless the `yfinance` logger is configured. If Yahoo throttles or changes its API, the pipeline prints `WARN`
per ticker and falls back to reference prices; check those lines before quoting a level.

## The last "close" can be a session in progress (run)

At 08:28 EDT the GC=F history ended with a bar dated 2026-10-05 (Close 4183.7, **Volume 57 510**) while the three previous
full sessions had 130 846-156 277. The 1-minute feed for the day had 499 bars ending 08:18. Yahoo's daily bar for a futures
contract includes the current session, so `closes.iloc[-1]` is the **latest trade, not a settlement**. For a number that is
stored with a date (`live_price_date`), prefer the previous complete bar when the last bar's date is today, or record
that it is intraday. Also observed: the 2026-10-01 and 2026-10-02 bars show the identical volume 130 846, which looks like a
stale value on Yahoo's side; do not use volume from this source.

## TIO=F (iron ore) conflicts with the note in the pipeline

`master.py` sets `yfinance_ticker` to `None` for iron ore with the comment "iron ore (TIO=F) is CNY/MT, skip". Yahoo's
data for `TIO=F` today: short name "Iron Ore 62% Fe, CFR China (TSI)", `currency = USD`, `quoteType = ALTSYMBOL`,
`exchange = CMX`, daily `Close` of 91.35 to 97.14 over the last month with **Volume 0**, but `get_info()["regularMarketPrice"]`
= **161.91**. The history column (91-97) looks like a USD-per-tonne quote near USD 100; I did not check the market level independently, so
treat the CNY label as unconfirmed. What is certain is that Yahoo labels it USD and that its history and quote fields disagree.
Skipping the ticker is still right (zero volume, contradictory fields), but the stated reason should be "unreliable symbol",
not "CNY". This does not touch any committed float.

## Rules of thumb

- Treat yfinance as a convenience feed: pin the version and expect breakage when Yahoo changes
  its site.
- Prefer a previous complete bar for anything stored as a dated price; keep the fallback reference path.
- Route Yahoo's logger output into the run log if silent fallbacks matter:
  `logging.getLogger("yfinance").addHandler(...)`.
- Not run: `Ticker.info` for the metals, `yf.download` with `interval` options, retry/rate-limit behaviour under load, the
  `curl_cffi` impersonation layer, options chains and fundamentals.
