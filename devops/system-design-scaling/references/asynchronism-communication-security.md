# Asynchronism, Communication & Security

Distilled from donnemartin/system-design-primer (CC BY 4.0), master branch, mined 2026-09-13.

## Asynchronism

Async workflows cut request times for expensive operations that would otherwise block inline; they also let you do time-consuming work *in advance* (e.g., periodic aggregation).

### Message queues vs task queues
**Message queue**: receives, holds, delivers messages. Pattern: app publishes a job → tells user "job started" → worker pulls the job, processes it, signals completion. User never blocks; optionally the client does small inline work so progress *looks* complete (e.g., your tweet appears on your timeline instantly while fan-out to followers happens in the background).
- **Redis**: simple broker, but messages can be lost.
- **RabbitMQ**: popular; requires adapting to AMQP and managing your own nodes.
- **Amazon SQS**: hosted; higher latency; at-least-once delivery (possible duplicates — design idempotent consumers).

**Task queue**: receives tasks + related data, runs them, delivers results; supports scheduling; for computationally intensive background jobs. **Celery**: scheduling support, primarily Python.

### Back pressure
If queues grow past memory → cache misses, disk reads, everything slows down. Limit queue size deliberately: once full, clients get "server busy" / HTTP 503 and retry later — ideally with exponential backoff. This preserves throughput + response times for jobs already queued rather than degrading the whole system.

Disadvantage of asynchronism in general: cheap calculations and realtime workflows are better synchronous — queues add delay and complexity without benefit there.
Related law worth knowing by name: **Little's Law** (L = λW) relates queue length, arrival rate, and time-in-system.

## Communication protocols

### HTTP verbs cheat-sheet
| Verb | Description | Idempotent* | Safe | Cacheable |
|---|---|---|---|---|
| GET | reads a resource | yes | yes | yes |
| POST | creates a resource / triggers processing | no | no | only if response has freshness info |
| PUT | create or replace a resource | yes | no | no |
| PATCH | partial update | no | no | only if response has freshness info |
| DELETE | delete a resource | yes | no | no |

\* idempotent = can be called many times without different outcomes. HTTP is self-contained (requests/responses flow through routers doing load balancing, caching, encryption, compression).

### TCP vs UDP — selection rules
**TCP**: connection-oriented over IP; handshake to establish/terminate; guaranteed in-order delivery via sequence numbers + checksums + ACK/retransmission; multiple timeouts drop the connection; implements flow control and congestion control. Guarantees cost latency → less efficient than UDP. High-throughput web servers keep many TCP connections open (memory-hungry) — use **connection pooling** where applicable (e.g., app ↔ memcached).
Use TCP when: all data must arrive intact; you want automatic best-effort throughput utilization. Typical: web, DB traffic, SMTP, FTP, SSH.

**UDP**: connectionless datagrams; may arrive out of order or not at all; no congestion control → more efficient overall; can broadcast to a subnet (DHCP needs this — client has no IP yet).
Use UDP when: lowest latency matters; late data is worse than lost data; you want your own error correction. Typical: VoIP, video chat, streaming, realtime multiplayer games.

### RPC vs REST

**RPC**: client causes a procedure to run in another address space, coded as if local. Anatomy (request): client program → **client stub** marshals procedure id + args into a message → OS sends it → server communication module passes packets to **server stub** → unmarshals, invokes the matching procedure; response reverses the path. Frameworks: Protobuf, Thrift, Avro.
- RPC exposes *behaviors*; often chosen for internal calls where you can hand-craft native calls for performance/UX. Choose a native SDK when: target platform known, want control over access + error handling, performance is primary concern.
- Disadvantages: clients tightly coupled to service implementation; new API definition per operation; harder to debug; may not leverage existing tech (e.g., caching proxies like Squid) out of the box.

**REST**: architectural style — client/server model where clients act on server-managed *resources*; all communication stateless and cacheable. Four qualities:
1. Identify resources via URI (same URI regardless of operation).
2. Change with representations (verbs, headers, body).
3. Self-descriptive responses (use standard status codes; don't reinvent).
4. HATEOAS — service fully navigable in a browser.

REST exposes *data*; minimizes client/server coupling → public HTTP APIs; statelessness makes horizontal scaling and partitioning easy.
Disadvantages: awkward when resources aren't naturally hierarchical (e.g., "all records updated in the past hour matching events X" = path + query params + body soup); few verbs don't always fit ("archive expired documents"); nested hierarchies need multiple round trips (bad on mobile networks); evolving responses bloat payloads for old clients that receive fields they never use.

**HATEOAS in practice** (from the primer's flashcard deck — fuller than most summaries): HATEOAS = *Hypermedia As The Engine Of Application State* — hypertext links should be how a client navigates the API, so responses advertise their own next actions:
```http
GET /account/12345 HTTP/1.1
HTTP/1.1 200 OK
<?xml version="1.0"?>
<account>
  <account_number>12345</account_number>
  <balance currency="usd">100.00</balance>
  <link rel="deposit"   href="/account/12345/deposit"/>
  <link rel="withdraw"  href="/account/12345/withdraw"/>
  <link rel="transfer"  href="/account/12345/transfer"/>
</account>
```
The client discovers available operations from the representation itself instead of hardcoding URLs — this is what makes a REST service "fully accessible in a browser". In practice most public APIs skip full HATEOAS (link bloat, awkward with JSON); treat it as the theoretical ceiling of REST's self-descriptiveness.

### Side-by-side (same operations)
| Operation | RPC | REST |
|---|---|---|
| Signup | POST /signup | POST /persons |
| Resign | POST /resign {"personid":"1234"} | DELETE /persons/1234 |
| Read person | GET /readPerson?personid=1234 | GET /persons/1234 |
| Person's items | GET /readUsersItemsList?personid=1234 | GET /persons/1234/items |
| Add item to person | POST /addItemToUsersItemsList {...} | POST /persons/1234/items {itemid...} |
| Update item | POST /modifyItem {"itemid":"456",...} | PUT /items/456 {...} |
| Delete item | POST /removeItem {"itemid":"456"} | DELETE /items/456 |

Rule of thumb from the primer: **REST for public APIs, RPC (or SDKs) for internal performance-sensitive calls.**

## Security basics

Unless you have deep security experience or are interviewing into a security role, know only the fundamentals:
- Encrypt in transit and at rest.
- Sanitize all user inputs to prevent XSS and SQL injection; use **parameterized queries**.
- Apply the principle of **least privilege** (also visible in the AWS case study: open only necessary ports — 80/443 public, SSH from whitelisted IPs only; private subnets for everything but the web tier).

Further reading pointers kept by the primer: API Security Checklist, OWASP Top Ten.
