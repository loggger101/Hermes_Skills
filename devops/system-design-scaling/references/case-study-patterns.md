# Case-Study Patterns (8 Worked Designs → Reusable Recipes)

Distilled from donnemartin/system-design-primer `solutions/` (CC BY 4.0), master branch, mined 2026-09-13. Each entry: the reusable pattern + its key numbers + the non-obvious tricks. All share the same template — scope → high-level design → core components → scale iteratively ("do NOT jump to the final design; benchmark → profile → fix bottleneck with trade-off discussion → repeat").

Shared back-of-envelope conversion guide (used by every case study):
- 2,500,000 seconds per month
- 1 req/s = 2.5M req/month · 40 req/s = 100M req/month · 400 req/s = 1B req/month

---

## 1. Pastebin / Bit.ly (URL shortener) — `pastebin`
**Constraints**: 10M users; 10M writes + 100M reads per month (10:1); ~1 KB/paste → **12.7 GB/month**, ~450 GB over 3 years, 360M shortlinks in 3 years; ≈ 4 write/s, 40 read/s average.

**The pattern — hash-based unique ID generation**:
- `url = base_encode(md5(ip_address + timestamp))[:7]`
- MD5: 128-bit, uniformly distributed (or hash random data). Base62 (`[a-zA-Z0-9]`) is URL-safe and deterministic; Base64 rejected because of `+`/`/`. O(k) encode where k = digits.
- **Capacity math**: first 7 chars → 62^7 ≈ 3.5×10^12 possible values ≫ 360M needed over 3 years. (Script: `scripts/shortlink_base62.py`.)
- Store in SQL as a big hash table: PK on `shortlink char(7)` enforces uniqueness via index; extra index on `created_at`. Paste *contents* go to an **object store** (S3) or document store — don't manage file servers. Uniqueness check = look up duplicate, regenerate if collision.
- Reads: shortlink → SQL lookup → object-store fetch.
- Analytics without realtime requirement: **MapReduce over web-server logs** (mapper emits `(year_month, url), 1`; reducer sums).
- Expiry: periodic scan for `expiration < now`, delete/mark.

## 2. Twitter timeline + search — `twitter`
**Constraints**: 100M active users; 500M tweets/day (~6K/s); fan-out avg 10 → **60K tweet-deliveries/s**; 250B reads/month (100K req/s); 10B searches/month. ~10 KB/tweet with media → 150 TB/month, 5.4 PB/3 years.

**The pattern — write-time fan-out for feeds**:
- User's *own* tweets → SQL (user timeline). Home timeline (followers' activity) is the hard part: fanning out to all followers overloads a traditional RDBMS at 60K/s → use **NoSQL/memory cache with fast writes** (Redis list per user, entries = tweet_id + user_id + meta bytes).
- Write path: client → web server → write API stores in SQL → **Fan Out Service**: query User Graph (followers from memory cache) → insert into each follower's home-timeline cache (**O(n): 1000 followers = 1000 lookups+inserts**) → index into Search Index Service → media to object store → notifications via async queue.
- Read path: timeline service reads cached tweet/user IDs — **O(1)** for the list, then O(n) multigets against Tweet Info + User Info services (Redis `MGET`).

**The celebrity problem (the key trick)**: users with millions of followers take minutes to fan out → race conditions on @replies. Fixes:
- Re-order tweets at *serve* time; and/or **invert for celebrities**: don't fan them out — at read time, search their recent tweets, merge into the home timeline, re-sort by timestamp.

**Cache sizing tricks**: keep only several hundred tweets per home timeline in cache; keep only *active* users' timelines (inactive 30+ days → rebuild from SQL via user graph); store ~1 month of tweet info and only active users in info services; search cluster keeps recent data in memory for latency.

## 3. Web crawler + search — `web_crawler`
**The pattern — prioritized crawl queue with signature dedup**:
- Seed `links_to_crawl` ranked by site popularity (or seed from link-hubs like Yahoo/DMOZ). Redis **sorted sets** hold the ranking; a NoSQL KV store holds `crawled_links` = url + page signature.
- Loop: pop top-priority link → check for *similar* crawled signature → if similar, **reduce its priority and continue (cycle prevention)**; else crawl it: enqueue reverse-index job + document (title/snippet) job, compute signature, move from to-crawl to crawled.
- **Duplicate URLs**: small lists `sort | unique`; 1B links → MapReduce keeping only frequency-1 entries. **Duplicate content**: compare page signatures via Jaccard index / cosine similarity.
- **Freshness**: `timestamp` per page; default re-crawl weekly, shorter for popular/fast-changing sites; data-mine the mean update interval per page to set schedules; support robots.txt.

**Search side**: query parsing pipeline (strip markup → tokenize → typo fix → normalize case → boolean ops) → reverse index service ranks matches → document service returns titles/snippets. Popular queries served from memory cache (skews: some queries very popular, most run once).
Crawler optimizations: keep own periodically-refreshed DNS lookups (DNS can be a bottleneck); **connection pooling** for many open connections; bandwidth is the real constraint of crawling.

## 4. Social graph shortest path — `social_graph`
Millions of vertices / billions of edges → no single machine holds it all.
- Shard users across **Person Servers**; a **Lookup Service** maps person_id → server (hash map). BFS runs in the User Graph Service, resolving each neighbor via lookup + remote fetch.

**BFS tricks worth stealing**:
- Store complete/partial BFS traversals from popular sources in cache; batch-compute offline into NoSQL for later lookups.
- **Batch friend lookups per Person Server** to cut machine hops (group IDs by destination server); shard servers geographically — friends cluster locally.
- **Bidirectional BFS**: run one search from source and one from destination simultaneously, merge paths when frontiers meet → dramatically fewer expansions on average.
- Start expansion from the side with more connections (high-degree nodes shrink degrees of separation faster).
- Bound by time/hops; ask user to continue if needed. If allowed: a graph DB (Neo4j) or GraphQL removes all this machinery.

## 5. Query cache for search — `query_cache`
LRU over query → results, in front of the reverse-index + document services.
- **O(1) LRU design** = hash table (`query → node`) + doubly-linked list (head = most recent, tail = evict). Get: move-to-front; Set: update+move or append, evicting tail at capacity. (Runnable: `scripts/lru_cache_o1.py` — the primer's own notebook code is stubbed out; this implements it for real.)
- Invalidation triggers: page content changed / added/removed / rank changed → simplest correct approach = **TTL** on entries (cache-aside).

**Scaling a cache cluster to many machines — three options**:
1. Each machine its own cache — simple, low hit rate.
2. Every machine holds a full copy — simple, wasteful memory.
3. **Shard the cache across machines** (`machine = hash(query)`, ideally consistent hashing) — more complex, best option.

## 6. Mint.com (budgeting) — `mint`
10M users; ~5B transactions total; async extraction pipeline is the core pattern:
- Link account → **queue job** (extraction takes a while) → Transaction Extraction Service pulls jobs, fetches from financial institution, stores raw logs in object store → Category Service categorizes each transaction → Budget Service aggregates monthly spending by category (+ notifications when nearing/exceeding budget) → update `transactions` and pre-aggregated `monthly_spending` tables.
- **Categorization trick**: seed a seller→category dictionary with popular sellers (50K sellers × <255 B ≈ 12 MB — fits in RAM); for unknown sellers, use crowdsourced user overrides; keep the top override per seller in a heap for O(1)-ish lookup.
- **Budget recommendation without storing everything**: generic income-tier template (housing .4 / food .2 / gas .1 / shopping .2 …) computed on demand — only store *user overrides*, not 100M budget rows.
- Aggregation: SQL over `transactions` works, but running **MapReduce over the raw log files** offloads the DB entirely (mapper: `(user_id, year_month, category), amount`; reducer sums + fires budget notifications).

## 7. Amazon sales rank — `sales_rank` (the MapReduce top-k trick)
40 GB new content/month; 40K read/s vs 400 write/s → precompute the answer offline and serve from a small aggregate table.
- Raw tab-delimited logs on S3: `timestamp product_id category_id qty total_price seller_id buyer_id`.
- **Two-stage MapReduce** (the non-obvious part): stage 1 maps `(category, product) → sum(qty)`; stage 2 re-keys to **`(category, quantity), product`** and does an identity reduce — the framework's shuffle/sort step then performs a *distributed sort by (category, rank)* for free. Top-k per category = first k rows of each group.
- Result lands in `sales_rank(category_id, total_sold, product_id)` with indexes on id/category/product; reads are trivial table lookups served from memory cache at 40K req/s.

## 8. Scaling to millions of users on AWS — `scaling_aws` (the iterative ladder)
The model for "how do I actually grow a system" — each rung is triggered by *measured* bottlenecks, never speculative:
1. **Single box** (web + MySQL + storage): vertical scaling only; monitor CPU/mem/IO/network (CloudWatch/top/nagios/statsd); Elastic IP so failover = repoint DNS; open only 80/443 public + SSH from whitelist. Cheap, no redundancy, gets expensive fast.
2. **Users+**: DB and static content outgrow the box → move static assets to S3 (server-side encryption), MySQL to RDS (multi-AZ, encryption at rest); VPC with public subnet for web tier only, private subnets behind it; encrypt in transit + at rest. Cost: complexity + app changes + security work per new component.
3. **Users++**: single web server bottlenecks at peak → LB (ELB or HAProxy active-active across AZs) + multiple stateless web servers across AZs + MySQL master-slave failover across AZs; terminate SSL on the LB; separate web tier from app tier (read APIs vs write APIs scale independently); CDN for static+some dynamic.
4. **Users+++**: read-heavy 100:1 → memory cache (ElastiCache) for hot DB content (**try tuning MySQL's own cache first**) and session data (→ stateless web servers enable autoscaling); add read replicas with LBs in front; route reads/writes separately at the app layer.
5. **Users++++**: traffic spikes on business hours → managed autoscaling groups per server type across AZs, min/max instances, scale triggers from CloudWatch (time-of-day for predictable loads, or CPU/latency/network/custom metrics); automate DevOps (Chef/Puppet/Ansible); layered monitoring: host-level, aggregate LB stats, log analysis (CloudTrail/Splunk), external site checks (Pingdom/New Relic), incident paging (PagerDuty), error reporting (Sentry). Autoscaling caveat: lag between demand change and capacity response.
6. **Users+++++**: DB too big → keep a bounded time window in MySQL, warehouse the rest (Redshift handles 1 TB/month easily); scale memory cache for hot reads at 40K req/s; if single write master can't take 400 w/s peaks → federation/sharding/denormalization/tuning + move suitable data to NoSQL (DynamoDB); split app servers further — non-realtime work goes async: e.g., photo upload returns immediately, SQS job on a worker/Lambda creates the thumbnail, updates DB, stores it in S3.

---

## Cross-cutting patterns worth memorizing
- **Precompute offline, serve online**: analytics/rankings/aggregations via MapReduce over logs → small SQL table + cache (pastebin analytics, sales_rank, mint budgets).
- **Object store for blobs, KV/NoSQL for fast writes, SQL for relational truth** — every case study splits storage this way.
- **Async queue at the write edge** whenever an operation is slow (extraction, fan-out notifications, thumbnails); keep cheap paths synchronous.
- **Stateless app servers + centralized sessions/cache** are what make horizontal scaling and autoscaling possible.
- **Memory latency anchor**: 1 MB sequential from RAM ≈ 250 µs; SSD ≈ 4× that; HDD ≈ 80× (full table in `latency-and-estimation.md`).
