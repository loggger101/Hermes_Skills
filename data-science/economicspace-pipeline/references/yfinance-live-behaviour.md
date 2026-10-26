---
description: "yfinance 1.7.0 as spacecost.quotes.fetch_closes calls it (Ticker.history 5d), behind `spacevalue quotes record`, `spacecost quotes record` and the opt-in live builds; no economicspace stage calls it. Failures are logged not raised, the last bar can be an in-progress session (why recording drops today's bar), TIO=F data conflicts with spacevalue's CNY note"
source_repo: ranaroussi/yfinance (Apache-2.0) as called from spacecost.quotes.fetch_closes (spacecost v0.14.0, spacecost/quotes.py); first run 2026-10-05 against economicspace's own fetch_yfinance, the same loop before it moved
tested_version: "yfinance 1.7.0 + pandas 3.0.6 on Python 3.14.6 (Windows, uv venv); live requests to Yahoo Finance on Mon 2026-10-05 around 08:20-08:30 EDT. Yahoo's API is unofficial, so every number here is a snapshot"
verified_date: "2026-10-05"
---

# yfinance, as the quote recorders call it

**No economicspace stage calls yfinance** (since master v1.59.0). Stage 2 installs a pinned spacevalue price
release and Stage 3 prices fuel from a recorded spacecost snapshot; see `data-sources-environment-entrypoints.md`.
yfinance runs in two places outside economicspace, both through one function, `spacecost.quotes.fetch_closes`:

| caller | what it asks for | on a failed ticker |
|---|---|---|
| `spacevalue quotes record` (`record_snapshot("metals", ...)`) | `HG=F` copper USD/lb, `GC=F` gold, `SI=F` silver, `PL=F` platinum, `PA=F` palladium, USD/troy oz (`spacevalue.catalog.metal_tickers()`) | **nothing is written**: one ticker failed, or quoted in an unexpected unit, refuses the whole snapshot |
| `spacecost quotes record` | the fuel proxies `HO=F`, `NG=F`, `CL=F` (`spacecost.prices.FUEL_TICKERS`) | the same refusal |
| opt-in live builds: spacevalue `use_yfinance=True` / `spacevalue build --live` (extra `spacevalue[live]`), spacecost `use_yfinance` | the same tickers | prints `FAIL <ticker>: ...` and falls back to the reference row; the build reports success |

`fetch_closes` calls `yf.Ticker(t).history(period="5d", auto_adjust=False)` per ticker, takes the last non-NaN `Close`,
and returns the quotes plus a list of failures rather than raising. The recorders pass `completed_only=True`; the live
builds do not. A recorded snapshot stores the raw close in the exchange's unit, never $/kg. The run below was made on
2026-10-05 against economicspace's `fetch_yfinance`, which was the same loop before it moved to spacecost; only the
five metal tickers were run.

## What the call returns (run)

| Check | Result |
|---|---|
| Install | `pip install yfinance` gives 1.7.0 on Python 3.14.6 with pandas 3.0.6, no build step |
| Five tickers, `history(period="5d", auto_adjust=False)` | 4 rows each (a weekend inside the window), 8 columns `Open High Low Close Adj Close Volume Dividends Stock Splits`, index tz `America/New_York`, dtype `datetime64[s, America/New_York]`. First call ~3 s, then ~0.2 s |
| Last closes | HG 6.624, GC 4184.0, SI 61.975, PL 1745.3, PA 1183.5 (all dated 2026-10-05) |
| `history()` default | `auto_adjust=True`: the `Adj Close` column is dropped (7 columns). `fetch_closes` passes `auto_adjust=False` explicitly, so keep it |
| `yf.download([...])` | MultiIndex columns `(field, ticker)`; even a single ticker comes back as a MultiIndex in 1.7.0 |

## Failures do not raise (run)

| Input | Result |
|---|---|
| Unknown ticker `ZZZZNOPE=F` | **no exception**, empty DataFrame with 6 columns; the only trace is a log line `HTTP Error 404 ... Quote not found` and `No data found, symbol may be delisted` on the `yfinance` logger |
| Invalid period `'5dd'` | no exception, empty DataFrame, log line listing the valid periods (`1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max`) |

So the `except Exception` branch in `fetch_closes` is not what catches a bad or blocked ticker; the empty-closes branch
(`<ticker>: no close data` in the failure list) is. Yahoo's own error text never reaches the output unless the
`yfinance` logger is configured. For a recorder that is harmless: `record_snapshot` checks the result against the
consumer's ticker list (`missing()`) and refuses to write anything, so a throttled or changed API means no new snapshot,
never a partial one. For a live build it means a per-ticker `FAIL` line and a reference-row price; read those lines
before quoting a level from a live build.

## The last "close" can be a session in progress (run)

At 08:28 EDT the GC=F history ended with a bar dated 2026-10-05 (Close 4183.7, **Volume 57 510**) while the three previous
full sessions had 130 846-156 277. The 1-minute feed for the day had 499 bars ending 08:18. Yahoo's daily bar for a futures
contract includes the current session, so `closes.iloc[-1]` is the **latest trade, not a settlement**. spacecost acted on
this: `completed_only=True`, which both `quotes record` commands use, drops any bar dated today or later, so a snapshot
holds the last finished session (and spacecost's snapshot checks refuse a close dated after its `recorded_date`). The live builds still take today's bar. Also observed: the 2026-10-01 and 2026-10-02 bars show the identical
volume 130 846, which looks like a stale value on Yahoo's side; do not use volume from this source.

## TIO=F (iron ore) conflicts with the note in spacevalue

spacevalue's reference table (`spacevalue/catalog.py`, the iron-ore row) sets `yfinance_ticker` to `None` with the comment
"iron ore (TIO=F) is CNY/MT, skip" (the row and comment moved there from economicspace with the split). Yahoo's data for
`TIO=F` on 2026-10-05: short name "Iron Ore 62% Fe, CFR China (TSI)", `currency = USD`, `quoteType = ALTSYMBOL`,
`exchange = CMX`, daily `Close` of 91.35 to 97.14 over the previous month with **Volume 0**, but
`get_info()["regularMarketPrice"]` = **161.91**. The history column (91-97) looks like a USD-per-tonne quote near USD 100;
the market level was not checked independently, so treat the CNY label as unconfirmed. What is certain is that Yahoo
labels it USD and that its history and quote fields disagree. Skipping the ticker is still right (zero volume,
contradictory fields), but the stated reason should be "unreliable symbol", not "CNY". Iron ore is priced from its
reference row either way, so this touches no committed float.

## Rules of thumb

- Treat yfinance as a recording tool, not a build input: record once (`spacevalue quotes record`,
  `spacecost quotes record`), commit the snapshot, build from it. A snapshot is never edited; a newer quote is a new file.
- Pin the yfinance version where you record, and expect breakage when Yahoo changes its site; a refused recording
  is the safe failure.
- Route Yahoo's logger output into the log if you need to know why a ticker failed:
  `logging.getLogger("yfinance").addHandler(...)`.
- Not run: the fuel tickers (`HO=F`, `NG=F`, `CL=F`), `Ticker.info` for the metals, `yf.download` with `interval`
  options, retry/rate-limit behaviour under load, the `curl_cffi` impersonation layer, options chains and fundamentals.
