# Scaling Trade-Offs & Networking Topics

Distilled from donnemartin/system-design-primer (CC BY 4.0), master branch, mined 2026-09-13. Every pattern lists its disadvantages — the primer's core thesis is "everything is a trade-off".

## The three fundamental axes

### Performance vs scalability
A service is **scalable** if performance grows proportionally with resources added (more units of work, or larger units as datasets grow).
- **Performance problem**: system is slow for a single user.
- **Scalability problem**: fast for one user, slow under heavy load.

### Latency vs throughput
- **Latency** = time to perform an action / produce a result.
- **Throughput** = number of such actions per unit time.
- Aim: maximal throughput at acceptable latency (batching trades latency for throughput).

### Availability vs consistency — CAP theorem
A distributed system can support only two of three guarantees:
- **Consistency**: every read gets the most recent write or an error.
- **Availability**: every request receives a response, not necessarily the latest version.
- **Partition tolerance**: keeps operating despite network partitioning.

Networks aren't reliable → you must accept partitions; the real choice is C vs A:
- **CP** — waiting on a partitioned node may time out. Choose when business needs atomic reads/writes (e.g., financial ledgers).
- **AP** — serve whatever version any node has; writes propagate after resolution. Choose for eventual consistency or "keep working through external errors".

### Consistency patterns (with multiple copies of data)
| Pattern | Guarantee | Seen in | Fits |
|---|---|---|---|
| Weak | reads may or may not see a write (best effort) | memcached | realtime: VoIP, video chat, multiplayer games — dropped packets are acceptable |
| Eventual | reads will eventually see it; async replication | DNS, email | highly available systems |
| Strong | reads always see the last write; sync replication | file systems, RDBMSes | transactional systems |

### Availability patterns
Two complementary mechanisms: **fail-over** + **replication**.
- **Active-passive (master-slave)**: heartbeats between active and standby; on heartbeat loss the passive takes over the IP. Downtime = hot vs cold standby startup time. Only active serves traffic.
- **Active-active (master-master)**: both serve, spreading load; DNS or app logic must know both endpoints.

Fail-over disadvantages: more hardware + complexity; data loss window if active dies before new writes replicate.

#### Availability in numbers ("nines")
| Uptime | Downtime/year | /month | /week | /day |
|---|---|---|---|---|
| 99.9% (three) | 8h 45m 57s | 43m 49.7s | 10m 4.8s | 1m 26.4s |
| 99.99% (four) | 52m 35.7s | 4m 23s | 1m 5s | 8.6s |

Composition math (verified by `scripts/availability_math.py`):
- **In sequence**: A_total = A_foo × A_bar → two 99.9% components in series give ~99.8%.
- **In parallel** (redundant): A_total = 1 − (1−A_foo)(1−A_bar) → two 99.9% in parallel ≈ 99.9999%.

> ⚠️ Verified source defect: the primer's four-nines table lists week downtime as "1m 5s", but its own arithmetic gives 7·86400·0.0001 = **60.48 s ≈ 1m 0.5s** (every other cell in both tables checks out). `scripts/availability_math.py` asserts the correct value and flags the deviation on each run.
Implication: every component on the critical path multiplies your downtime; redundancy is what buys extra nines.

## Networking layer, top to bottom

### DNS
Translates domain → IP. Hierarchical with authoritative servers at the top; lower-level servers cache (may go stale — propagation delay); browsers/OS also cache per **TTL**.
Record types:
- **NS** — name server for a domain/subdomain
- **MX** — mail exchange servers
- **A** — name → IP address
- **CNAME** — name → another name (or A record)

Managed services (CloudFlare, Route 53) add routing policies: weighted round robin (steer around maintenance, balance uneven clusters, A/B tests), latency-based, geolocation-based.
Disadvantages: lookup delay (mitigated by caching); management complexity; DDoS on DNS providers knocks out sites for everyone who doesn't know the raw IPs.

### CDN — push vs pull
Global proxy network serving content from near users; usually static files (HTML/CSS/JS, photos, video), some support dynamic. Two benefits: proximity to user + origin servers stop handling those requests.
- **Push**: you upload new/changed content directly and rewrite URLs to the CDN. Minimize traffic, maximize storage. Good for low-traffic or rarely-updated sites (content placed once).
- **Pull**: CDN fetches from your server on first request; TTL controls cache lifetime. Minimizes CDN storage but can create redundant re-pulls of unchanged files after expiry. Good for heavy traffic — only recently-requested content stays hot.

Disadvantages: cost scales with traffic; stale content if updated before TTL expires; requires URL rewriting to the CDN domain.

### Load balancer
Distributes client requests across app servers/DBs and routes responses back. Prevents routing to unhealthy servers, prevents overload, removes single points of failure (when you run several). Hardware or software (HAProxy, NGINX).
Extra capabilities: **SSL termination** (backends skip expensive crypto; no per-server X.509 certs), **session persistence** (cookie-based sticky routing when apps don't track sessions themselves).
Routing metrics: random, least loaded, session/cookies, round robin / weighted round robin, L4, L7.

- **Layer 4**: decides from transport-layer info only — source/dest IPs + ports; forwards packets via NAT. Fast, cheap on CPU.
- **Layer 7**: inspects application layer (headers, message body, cookies); terminates the connection and opens a new one to the chosen backend. Can route by content (video traffic → video servers; billing traffic → hardened servers). More flexible, more expensive — though impact is minimal on modern hardware.

**Horizontal scaling via LBs**: scale out with commodity machines = cheaper + higher availability than vertical scaling up; easier hiring too.
Disadvantages of horizontal: complexity from cloning; **servers must be stateless** (no sessions/profile data locally — store in centralized DB or persistent cache like Redis/Memcached); downstream caches/DBs absorb more simultaneous connections as upstream scales out.
LB disadvantages itself: can become the bottleneck if under-resourced/misconfigured; adds complexity; a single LB is still an SPOF → run multiple (active-passive/active-active).

### Reverse proxy vs load balancer
Reverse proxy = web server that centralizes internal services behind one public interface, forwarding each request to whatever backend can serve it. Benefits: hides backends + IP blacklisting + per-client connection limits; clients only see the proxy's IP so you can reconfigure/scale freely; SSL termination; compression; caching; direct static content serving.
- LB is useful when you have **multiple** servers doing the same job (routing among them).
- Reverse proxy helps even with a **single** server (all the benefits above).
- NGINX/HAProxy do both L7 reverse-proxying and load balancing.

### Application layer & microservices
Separate web layer from application ("platform") layer → scale/configure independently; adding an API = more app servers without touching web servers. Single-responsibility principle: small autonomous services; small teams can plan aggressive growth. Workers here enable asynchronism.
**Microservices**: independently deployable, small, modular services; each runs its own process and communicates via a well-defined lightweight mechanism for one business goal (e.g., Pinterest → user profile / followers / feed / search / photo upload).
**Service discovery**: Consul, Etcd, Zookeeper track registered names/addresses/ports; health checks (often an HTTP endpoint) verify integrity. Consul & Etcd embed key-value stores useful for config/shared data.
Disadvantages: different architecture/ops/process mindset vs monolith; deployment + operations complexity grows with service count.
