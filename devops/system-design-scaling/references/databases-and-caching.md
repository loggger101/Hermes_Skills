# Databases, NoSQL & Caching — Trade-Off Tables

Distilled from donnemartin/system-design-primer (CC BY 4.0), master branch, mined 2026-09-13.

## RDBMS scaling toolkit (in typical order of application)

**ACID**: Atomicity (all-or-nothing transaction), Consistency (valid state → valid state), Isolation (concurrent = serial results), Durability (committed stays committed).

### 1. Master-slave replication
Master serves reads + writes, replicating writes to slaves that serve **reads only**; slaves can chain into trees. If the master dies: read-only mode until a slave is promoted or a new master provisioned.
Disadvantages: extra promotion logic; plus all shared replication disadvantages below.

### 2. Master-master replication
Both masters serve reads + writes and coordinate on writes; either dying leaves full R/W capability.
Disadvantages (beyond the shared list): needs an LB or app-logic write routing; most systems are loosely consistent (violates ACID) **or** pay higher write latency for synchronization; conflict resolution gets worse with more writers and more latency.

### Shared replication disadvantages
- Data-loss window if master fails before new writes replicate out.
- Replicas replay the write stream — heavy write loads bog replicas down, starving their read capacity.
- More read slaves → more to replicate → greater lag.
- Some engines let the master spawn parallel writer threads while a replica replays sequentially (single-threaded).
- More hardware + complexity.

### 3. Federation (functional partitioning)
Split databases **by function** — e.g., `forums` / `users` / `products` instead of one monolith. Less R/W traffic per DB → less replication lag; smaller DBs fit in memory better → more cache hits via locality; no single central master serializing writes → parallel writes, higher throughput.
Disadvantages: useless if your schema demands huge tables/functions; app logic must route reads/writes to the right DB; cross-DB joins need server links (complex); more hardware + complexity.

### 4. Sharding
Distribute data across databases so each manages only a subset (e.g., shard users by last-name initial or geo). Same benefits as federation (less traffic/replication, better cache locality, smaller indexes → faster queries) plus: one shard down ≠ whole system down (add replication to avoid loss); parallel writes.
Disadvantages: app logic must handle shards (complex SQL possible); **lopsided distribution** — power users on one shard skew load; rebalancing is complex (a sharding function based on **consistent hashing** minimizes data movement when nodes join/leave); cross-shard joins are hard; more hardware + complexity.

### 5. Denormalization
Trade write performance for read performance: store redundant copies in multiple tables to avoid expensive joins. PostgreSQL/Oracle materialized views automate the redundancy bookkeeping. After federation/sharding, denormalization can eliminate cross-datacenter joins entirely. Rationale: reads often outnumber writes **100:1 or 1000:1**, and a complex join spends most of its time on disk I/O (see latency table).
Disadvantages: duplicated data; constraints needed to keep copies in sync add design complexity; under heavy write load it can perform *worse* than normalized.

### 6. SQL tuning checklist
First **benchmark** (simulate high load, e.g., `ab`) and **profile** (e.g., MySQL slow query log) — then:
- **Tighten the schema**: fixed-length fields as `CHAR` (fast random access; VARCHAR must find each string's end); large text in `TEXT` (stored by pointer on disk, allows boolean searches); `INT` up to 2^32 (~4B); `DECIMAL` for currency (no float representation errors); avoid big BLOBs — store a location pointer instead; `VARCHAR(255)` is the largest length an 8-bit counter can hold (why it's everywhere); `NOT NULL` where applicable improves search performance.
- **Good indices**: index columns used in SELECT/GROUP BY/ORDER BY/JOIN; indexes are usually self-balancing B-trees → logarithmic searches but more space and slower writes (index must update too); for bulk loads, disable indices, load, rebuild.
- **Avoid expensive joins** — denormalize where performance demands it.
- **Partition tables**: move hot spots into separate tables to keep them in memory.
- **Tune the query cache**: on some systems/versions (notably MySQL 5.7) the built-in query cache can *hurt* performance.

## NoSQL families

Data denormalized, joins done in application code; most lack true ACID and favor eventual consistency. Described by **BASE** — the CAP opposite of ACID:
- **Basically available**: system guarantees availability.
- **Soft state**: state may change over time without input.
- **Eventual consistency**: becomes consistent given no new input for a while.

| Family | Abstraction | Notes | Use when |
|---|---|---|---|
| Key-value store | hash table | O(1) R/W, often memory/SSD-backed; lexicographic key order → efficient range retrieval; limited ops push complexity to app layer; the base for document stores and some graph DBs | simple models, rapidly-changing data, in-memory cache layers |
| Document store | KV with documents (XML/JSON/binary) as values | one doc = all info about an object; query by internal structure; organized by collections/tags/metadata/dirs; fields may differ between docs; MongoDB/CouchDB add SQL-like queries; DynamoDB does both KV + docs | flexible schema, occasionally-changing data |
| Wide column store | nested map `ColumnFamily<RowKey, Columns<ColKey, Value, Timestamp>>` | unit = name/value pair grouped in column families (≈ tables); each value carries a timestamp for versioning/conflict resolution; lexicographic key order → selective range retrieval; lineage: Bigtable → HBase (Hadoop ecosystem), Cassandra (Facebook) | very large datasets needing high availability + scalability |
| Graph database | graph — nodes = records, arcs = relationships | optimized for complex FK / many-to-many relationship models (social networks); relatively new, fewer tools/resources; often REST-only access | data model *is* a web of relations |

## SQL or NoSQL?

**Choose SQL**: structured data; strict schema; relational data; need complex joins; transactions; clear scaling patterns; more mature ecosystem; very fast indexed lookups.
**Choose NoSQL**: semi-structured data; dynamic/flexible schema; non-relational data; no complex joins needed; many TB (or PB) of data; very data-intensive workload; very high IOPS throughput.

Sample NoSQL-suitable data: rapid ingest of clickstreams/logs; leaderboards/scoring; temporary data (shopping carts); frequently accessed "hot" tables; metadata/lookup tables.

## Caching

Caching speeds page loads and offloads servers/DBs: the dispatcher checks for a previous result before executing. DBs prefer uniform R/W across partitions — popular items skew that distribution, so a cache in front absorbs uneven load and spikes.

### Where to cache (layers)
Client (OS/browser) → CDN → web server/reverse proxy (Varnish serves static+dynamic directly; can answer without touching app servers) → database's own built-in cache (tune for your access pattern) → application-level in-memory KV between app and storage.

### What to cache — two levels
- **Query level**: hash the query as key, store result. Invalidation pain: hard to delete cached results of complex queries; if one cell changes you must invalidate every cached query that might include it.
- **Object level** (usually better): assemble DB data into a class/structure and cache *that*; remove on underlying-data change; enables async workers assembling from the latest cached object. Good candidates: user sessions, fully rendered pages, activity streams, user graph data.

Avoid file-based caching — makes cloning/auto-scaling harder.

### When to update (four strategies)
| Strategy | Flow | Pros | Cons |
|---|---|---|---|
| **Cache-aside** ("lazy loading") | app: miss → load from DB → set cache → return; memcached's standard mode | only requested data gets cached | each miss = 3 trips (latency); stale until TTL or write-through; node failure → empty node, latency spike |
| **Write-through** | app writes to cache; cache *synchronously* persists to DB | cache never stale; fast subsequent reads of just-written data | slow overall writes; new nodes stay cold until entries are written (pair with cache-aside); much written may never be read (use TTL) |
| **Write-behind / write-back** | app updates cache; async flush to store | best write performance | possible data loss if cache dies before flush; most complex to implement correctly |
| **Refresh-ahead** | cache proactively refreshes recently-accessed entries before expiry | lower latency than read-through *if* prediction is right | wrong predictions cost more than no refresh |

General disadvantages: must maintain consistency with the source of truth (cache invalidation is a hard problem); requires app changes to add Redis/memcached.
Redis extras over plain memcached: persistence option; built-in data structures (sorted sets, lists).
