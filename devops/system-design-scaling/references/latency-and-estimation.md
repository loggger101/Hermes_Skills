# Latency Numbers & Back-of-the-Envelope Estimation

Distilled from donnemartin/system-design-primer (CC BY 4.0), master branch, mined 2026-09-13. The primer's appendix tables verbatim + the conversion guide its case studies use. `scripts/availability_math.py` and `scripts/topk_mapreduce_sim.py` make parts of this runnable.

## Powers of two table
```
Power           Exact Value         Approx Value        Bytes
---------------------------------------------------------------
7                             128
8                             256
10                           1024   1 thousand           1 KB
16                         65,536                       64 KB
20                      1,048,576   1 million            1 MB
30                  1,073,741,824   1 billion            1 GB
32                  4,294,967,296                        4 GB
40              1,099,511,627,776   1 trillion           1 TB
```

## Latency numbers every programmer should know
```
Latency Comparison Numbers
--------------------------
L1 cache reference                           0.5 ns
Branch mispredict                            5   ns
L2 cache reference                           7   ns                      14x L1 cache
Mutex lock/unlock                           25   ns
Main memory reference                      100   ns                      20x L2, 200x L1
Compress 1K bytes with Zippy            10,000   ns       10 us
Send 1 KB over 1 Gbps network           10,000   ns       10 us
Read 4 KB randomly from SSD*          150,000   ns      150 us        ~1 GB/sec SSD
Read 1 MB sequentially from memory    250,000   ns      250 us
Round trip within same datacenter     500,000   ns      500 us
Read 1 MB sequentially from SSD*    1,000,000   ns       1 ms        ~1 GB/sec SSD, 4x memory
HDD seek                            10,000,000   ns     10 ms        20x datacenter roundtrip
Read 1 MB sequentially from 1 Gbps  10,000,000   ns     10 ms        40x memory, 10x SSD
Read 1 MB sequentially from HDD     30,000,000   ns     30 ms       120x memory, 30x SSD
Send packet CA->Netherlands->CA    150,000,000   ns    150 ms

Notes: 1 us = 1,000 ns; 1 ms = 1,000 us = 1,000,000 ns
```

Handy derived metrics (from the same numbers):
- Sequential read speeds: HDD ≈ **30 MB/s** · 1 Gbps Ethernet ≈ **100 MB/s** · SSD ≈ **1 GB/s** · main memory ≈ **4 GB/s**.
- ~6–7 world-wide round trips per second; ~2,000 datacenter round trips per second.

Why these matter in design conversations: they justify *why* you cache (RAM is 4× faster than SSD and 120× faster than HDD for sequential reads), why indexes should fit in memory ("keep the index hot"), why a datacenter-local service beats cross-continent calls by ~300×, and why fan-out to millions of followers can't be synchronous.

## Request-rate conversion guide (used across all 8 case studies)
```
2,500,000 seconds per month
1   request/s = 2.5 million requests/month
40    requests/s = 100 million requests/month
400   requests/s = 1 billion requests/month
```

Worked examples straight from the case studies:
- Pastebin: 10M writes + 100M reads per month → **4 write/s, 40 read/s** average. Paste size ~1.27 KB (content 1 KB + shortlink 7 B + expiry 4 B + created_at 5 B + path 255 B) → 12.7 GB/month new content; ×36 months ≈ 450 GB, 360M links over 3 years.
- Twitter: 500M tweets/day at ~10 KB each (incl. media avg) → **150 TB/month**, 5.4 PB/3yrs; fan-out ×10 → 60K deliveries/s; 250B reads/month → 100K read req/s via the 400-req/s-per-billion rule.
- Sales rank: 40 GB new content/month handled comfortably by an object store (S3).

## Availability ("nines") downtime tables
| Uptime | Year | Month | Week | Day |
|---|---|---|---|---|
| 99.9% | 8h 45m 57s | 43m 49.7s | 10m 4.8s | 1m 26.4s |
| 99.99% | 52m 35.7s | 4m 23s | 1m 5s ⚠️ | 8.6s |

⚠️ The primer's published "1m 5s" is a source defect — its own arithmetic gives **1m 0.5s** (60.48 s). See `scripts/availability_math.py`, which verifies every other cell and flags this one on each run.

Composition rules (verified by `scripts/availability_math.py`):
- In **sequence**: A_total = A₁ × A₂ — two 99.9% components → ~99.8%.
- In **parallel** (redundant paths): A_total = 1 − (1−A₁)(1−A₂) — two 99.9% → ≈99.9999%.

## Study-guide framing (interview prep)
You do NOT need everything in the primer for an interview; scope by timeline:
- **Short**: breadth on topics + a few company engineering-blog posts + some practice questions.
- **Medium**: breadth + some depth, many practice questions.
- **Long**: breadth + more depth, most practice questions.

The 4-step process (scope → high-level design → core components → scale iteratively) and the "benchmark/profile/fix/repeat" loop are what interviewers actually grade — not memorizing every trade-off table.
