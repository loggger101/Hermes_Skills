---
name: system-design-scaling
description: "Scalable system design: CAP, caches, shards, tradeoffs."
version: v1.0.0
author: Hermes Agent
license: MIT (distilled from donnemartin/system-design-primer, CC BY 4.0)
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [system-design, scalability, architecture, CAP-theorem, caching, sharding, interview-prep]
    related_skills: [rest-api-client, sql-for-data, python-craft]

---

# System Design & Scalability

Distilled from the [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer) (369k+ stars): a trade-off-first knowledge base for designing large-scale systems — usable both to prep system design interviews and to make real architecture decisions. **Everything is a trade-off**: every pattern here carries its disadvantages, not just its benefits.

## What This Skill Does

Provides the full decision framework: the 4-step process for any design question (scope → high-level design → core components → scale iteratively), back-of-envelope estimation tools (latency numbers, powers of two, request-rate conversions, availability math with runnable verification scripts), and distilled trade-off tables for every layer — DNS/CDN/load balancer/reverse proxy/application/database/cache/asynchronism/communication/security. Includes 8 worked case studies reduced to reusable patterns (URL shortener, social feed fan-out, web crawler, sharded graph BFS, query cache, budget aggregation, top-k ranking via MapReduce key-sort trick, and the iterative AWS scaling ladder).

## When to Use

- "Design a system for X" / any architecture or scalability question
- Prepping a system design interview (study guide + 4-step process inside)
- Choosing SQL vs NoSQL, cache strategy, replication mode, sharding key
- Estimating storage/bandwidth/latency by hand ("back of the envelope")
- Deciding TCP vs UDP, RPC vs REST, message queue vs task queue

## The 4-step process (lead the conversation)

1. **Outline use cases, constraints, assumptions** — who uses it, how many users, inputs/outputs, data volume, requests/sec, read:write ratio. Run back-of-envelope math (see `references/latency-and-estimation.md`).
2. **High-level design** — sketch main components and connections; justify each choice.
3. **Design core components** — for each: storage schema, API shape, the hard part (e.g., hash generation + collisions, fan-out, dedup).
4. **Scale iteratively** — never jump to the final design. State you will 1) benchmark/load-test, 2) profile bottlenecks, 3) address them evaluating alternatives and trade-offs, 4) repeat. The `scaling_aws` case study (`references/case-study-patterns.md`) is the model: each stage adds exactly one technique triggered by a measured bottleneck (object store → DB split → LB + horizontal scaling → cache + read replicas → autoscaling).

## Reference map

| Question | Doc |
|---|---|
| Performance vs scalability, latency vs throughput, CAP/CP/AP, consistency patterns, availability math | `references/scaling-tradeoffs-and-topics.md` |
| DNS records & routing policies, push/pull CDNs, L4/L7 load balancing, reverse proxy vs LB, microservices/service discovery | same doc (networking half) |
| ACID vs BASE, replication modes, federation, sharding + consistent hashing, denormalization, SQL tuning checklist, NoSQL families, cache update strategies | `references/databases-and-caching.md` |
| Message queues vs task queues, back pressure, TCP vs UDP selection rules, RPC anatomy, REST properties, RPC-vs-REST comparison table, security basics | `references/asynchronism-communication-security.md` |
| The 8 case studies as reusable patterns with their key numbers and the non-obvious tricks (base62 capacity math, celebrity fan-out inversion, crawl signature dedup, bidirectional BFS, MapReduce top-k sort) | `references/case-study-patterns.md` |
| Powers of two, latency numbers every programmer should know, request-rate conversions, nines downtime tables | `references/latency-and-estimation.md` |

## Runnable scripts (stdlib-only, self-testing — run with `py`)

```bash
py devops/system-design-scaling/scripts/lru_cache_o1.py            # O(1) LRU matching the primer's design doc + tests
py devops/system-design-scaling/scripts/shortlink_base62.py        # MD5→Base62 shortener: capacity math, collision demo
py devops/system-design-scaling/scripts/topk_mapreduce_sim.py      # two-stage MapReduce top-k-per-group (key-sort trick) on the primer's sample data
py devops/system-design-scaling/scripts/availability_math.py       # nines→downtime tables + sequence/parallel composition, verified vs published values
```

## Key decision rules (memorize these first)

- **Read-heavy** → cache in front of DB + read replicas; denormalize to kill expensive joins.
- **Write-heavy fan-out** (feeds) → write-time fan-out O(followers); invert for celebrities: don't fan out, merge at serve time and re-order.
- **Hot keys skew load** → memory cache absorbs spikes; sharded cache cluster with consistent hashing beats per-node or replicated caches.
- **Expensive operation inline** → queue + workers (async), but keep cheap/realtime paths synchronous; apply back pressure (HTTP 503 + exponential backoff) when queues grow past memory.
- **CAP**: networks partition, so choose CP (atomic reads/writes, may time out) vs AP (serve stale, propagate later). NoSQL = BASE: basically available, soft state, eventually consistent.
- **Scaling a DB**: replication first (reads), then federation (by function), then sharding (by key); denormalize when joins hurt; always benchmark before and after.
