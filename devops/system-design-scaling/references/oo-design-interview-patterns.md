# Object-Oriented Design Interview Patterns (6 Worked Exercises)

Distilled from donnemartin/system-design-primer's **OO Design** Anki deck + `solutions/object_oriented_design/` (CC BY 4.0), master branch, mined 2026-09-13 (round 17b). This is the OO half of system design interviews: given a domain ("design a parking lot"), produce a clean class model with inheritance, state machines, and separation of concerns — *not* scaling.

The recurring meta-pattern across all six:
1. **Open with clarifying questions** (scope the domain before coding).
2. Model entities as classes; use `Enum` for closed sets (suits, ranks, sizes, states); use an abstract base class (`ABCMeta`) to define the contract subclasses must fill in.
3. Keep *state* and *behavior* on the right object — a `Call` knows its own state machine, a `ParkingSpot` decides whether it can fit a vehicle, not the other way around.

> The primer ships these as **stubbed** notebook code (method bodies are `# ...`). Below each skeleton is cleaned up to be runnable-shaped; where I kept a stub I say so. Two exercises have real implementations in this skill already: hash map (`solutions/.../hash_map.py`) and LRU cache (`scripts/lru_cache_o1.py` — the primer's own LRU notebook is stubbed, my script implements it for real).

---

## 1. Deck of cards → extend to Blackjack
**Clarifying questions**: generic deck first (poker/blackjack)? assume 52 cards + 4 suits? valid inputs?
**Key structure**: `Suit(Enum)` · abstract `Card` with an *abstract property* `value` · `BlackJackCard(Card)` overrides `value` so Ace→1 and face cards (J/Q/K)→10 · `Hand.score()` sums card values · `BlackJackHand(Hand)` handles the multi-Ace ambiguity.

**The non-obvious trick — multiple possible scores**: an Ace can be 1 or 11, so a hand like A+K+A has several legal totals (12, 22… and with one Ace as 11 → 22/12). `BlackJackHand.possible_scores()` enumerates them; `score()` then picks the *best* total:
```python
def score(self):
    min_over = sys.MAXSIZE      # smallest total that busts (>21)
    max_under = -sys.MAXSIZE    # largest total <= 21
    for s in self.possible_scores():
        if self.BLACKJACK < s < min_over:   min_over = s
        elif max_under < s <= self.BLACKJACK: max_under = s
    return max_under if max_under != -sys.MAXSIZE else min_over
```
i.e., prefer the highest non-busting total; only report a bust if *every* arrangement busts. `Deck` deals via an incrementing `deal_index`, marks dealt cards unavailable, and returns `None` on exhaustion (cleaner than raising).

## 2. Call center — hierarchical dispatch + state machine
**Clarifying questions**: what employee levels? do calls always start at the lowest level? if nobody free → queue? VIP jump-the-queue? (No.)
**Key structure**: `Rank(Enum)` OPERATOR<SUPERVISOR<DIRECTOR · abstract `Employee` with `take_call/complete_call/escalate_call` + a shared `_escalate_call()` that frees itself and notifies the center · concrete `Operator/Supervisor/Director` where each `escalate_call()` bumps `call.level` to the next rank (Director raises — it must handle everything) · `CallState(Enum)` READY→IN_PROGRESS→COMPLETE · `CallCenter.dispatch_call(call)` tries operators, then supervisors, then directors in order and **queues** if all are busy.

**The pattern**: dispatch is a *cascade* through levels (`if employee is None: try next level`), escalation re-enters the same cascade at a higher rank via a notification callback (`notify_call_escalated`), and completion frees an employee which can then pull from `queued_calls`. This is a clean state-machine + observer sketch — reusable for any tiered routing (support desks, ticket triage).

## 3. Hash map (chaining)
**Clarifying questions**: integer keys only? collision resolution by chaining? ignore load factor? fits in memory?
Already fully implemented at `solutions/object_oriented_design/hash_table/hash_map.py` — `Item(key,value)` + a list-of-buckets table, `_hash_function = key % size`, linear-scan each bucket on set/get/remove with `KeyError` on miss. No new pattern beyond "chaining hash table"; included here for completeness of the six.

## 4. LRU cache
**Clarifying questions**: what are we caching (web-query results)? valid inputs? fits memory?
The primer's notebook is **stubbed** (`LinkedList.move_to_front/append_to_front/remove_from_tail` are `# ...`). The real O(1) implementation — hash table + doubly-linked list with sentinel head/tail, move-to-front on get, evict-tail at capacity — lives in this skill: **`scripts/lru_cache_o1.py`** (self-tested). Use that.

## 5. Online chat
**Clarifying questions**: text only? which user workflows (add/remove/update, friend request lifecycle, group vs private chats)? no scaling initially?
**Key structure**: `UserService` holds `users_by_id` and owns the *user-management* verbs (add_user, add/approve/reject_friend_request) · `User` carries its own relation maps: `friends_by_id`, `friend_ids_to_private_chats`, `group_chats_by_id`, plus separate inbound/outbound request maps (`received_…/sent_…`) keyed by friend id → `AddRequest` · abstract `Chat(chat_id, users[], messages[])` with concrete `PrivateChat(first_user, second_user)` and `GroupChat(add_user/remove_user)` · `Message(message_id, message, timestamp)` · `AddRequest(from, to, request_status, timestamp)` where `request_status ∈ RequestStatus(Enum)` UNREAD/READ/ACCEPTED/REJECTED.

**The pattern**: split *identity/friendship* (UserService + User) from *conversation* (Chat subclasses). A private chat is just a 2-user Chat; group chat adds membership mutation. The friend-request lifecycle is its own little state machine on `RequestStatus`. This mirrors how real IM backends separate the social graph from message storage.

## 6. Parking lot — multi-level, size-constrained
**Clarifying questions**: which vehicle types (Motorcycle/Car/Bus)? do they take different spot counts? does a bus need *consecutive* spots? multiple levels?
**Key structure**: `VehicleSize(Enum)` MOTORCYCLE<COMPACT<LARGE · abstract `Vehicle(vehicle_size, license_plate, spot_size)` with `spots_taken[]`, `clear_spots()`, and **abstract `can_fit_in_spot(spot)`** (the polymorphic hook) · `Motorcycle` fits any spot (`return True`) · `Car` fits COMPACT or LARGE · `Bus` has `spot_size=5` and only fits a run of 5 consecutive LARGE spots · `ParkingLot(num_levels).park_vehicle(v)` walks levels top-down until one accepts · `Level(floor, total_spots)` with `SPOTS_PER_ROW=10`, tracks `available_spots`, `_find_available_spot(vehicle)` then `_park_starting_at_spot(spot, vehicle)` (occupies `spot.spot_number .. +vehicle.spot_size`) · `ParkingSpot(level,row,spot_number,spot_size,…).can_fit_vehicle(v)` = free AND `v.can_fit_in_spot(self)`.

**The pattern**: the *fit decision is inverted* — the spot asks the vehicle (`vehicle.can_fit_in_spot(spot)`) rather than hardcoding a size matrix. Multi-spot vehicles (bus=5 consecutive) make `_park_starting_at_spot` the interesting method: it must find a contiguous run, not just any free spot. This "ask the entity whether it fits" inversion is the reusable OO lesson here.

---

## Source defects found in the primer's OO code (verified 2026-09-13)
These are real bugs/typos in the published notebook skeletons — do **not** copy them verbatim:
- `call_center.py`: `Supervisor.__init__` and `Director.__init__` call `super(Operator, self)` (copy-paste error — should be their own class); Director's no-op uses `raise NotImplemented(...)` where it must be `NotImplementedError`.
- `deck_of_cards.py`: `Hand.score()` iterates `for card in card:` (bare name) instead of `self.cards`; `Deck.remaining_cards`/`deal_card` reference bare `deal_index` instead of `self.deal_index`.
- `parking_lot.py`: `Vehicle.__init__` has a dead statement `self.spot_size` (missing assignment); `ParkingLot.park_vehicle` iterates bare `levels` instead of `self.levels`; `PrivateChat.__init__` calls `super().__init__()` with no args though the base requires `chat_id`.
- The LRU + hash-map notebooks are intentionally stubbed (`# ...`) — see the real implementations referenced above.

## Cross-cutting OO lessons to reuse in any design interview
- **Enum for closed vocabularies** (suits, ranks, vehicle sizes, call/request states) — makes state machines explicit and switch-exhaustive.
- **Abstract base + one polymorphic hook** is the workhorse: `Card.value`, `Employee.escalate_call`, `Vehicle.can_fit_in_spot` each force subclasses to supply exactly their domain-specific behavior while sharing scaffolding.
- **Invert responsibility toward the more specific object**: spot→vehicle fit, employee→call state transitions, hand→its own best score. Keeps base classes stable (open/closed).
- **Separate lifecycle from membership**: friend-request state machine vs friendship map; call state machine vs dispatch cascade.
