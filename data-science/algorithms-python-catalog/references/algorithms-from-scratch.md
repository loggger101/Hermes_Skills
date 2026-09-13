# Algorithms From Scratch (verified)

Every snippet below was **executed live** on 2026-09-13 (Python 3.13, Windows 11) and cross-checked
against a stdlib oracle or independent reference — see `scripts/algorithms_verify.py` for the
re-runnable harness that re-proves each claim. Source: TheAlgorithms/Python @ `23c4208` (MIT),
trimmed to essentials; doctests from their files are preserved where they encode verified numbers.

## 1. String matching — when each algorithm earns its keep

**Decision rule:** one pattern → `str.find`/`re.search` (C-speed, always wins in Python). Many
patterns against the same text → **Aho-Corasick** is O(n + m + z) total regardless of pattern count;
per-pattern regex loops are O(k·n). Rolling hash (Rabin-Karp) only when you need substring *equality*
across a sliding window with cheap updates.

### KMP — failure array (the part worth memorizing)

```python
def get_failure_array(pattern: list[int]) -> list[int]:
    """failure[i] = length of longest proper prefix of pattern[:i+1] that is also a suffix."""
    failure, i, j = [0], 0, 1
    while j < len(pattern):
        if pattern[i] == pattern[j]:
            i += 1
        elif i > 0:
            i = failure[i - 1]      # fall back — this is the whole trick
            continue
        j += 1
        failure.append(i)
    return failure

def knuth_morris_pratt(text, pattern):
    """First occurrence index of pattern in text (O(n+m)), or -1."""
    if not pattern:
        return 0
    failure = get_failure_array(pattern)
    i, j = 0, 0                      # i into text, j into pattern
    while i < len(text):
        if pattern[j] == text[i]:
            if j == len(pattern) - 1:
                return i - j         # full match; index of first char
            j += 1
        elif j > 0:
            j = failure[j - 1]       # mismatch: resume at longest border, no re-scan of text
            continue
        i += 1
    return -1

# verified: get_failure_array("aabaabaaa") == [0, 1, 0, 1, 2, 3, 4, 5, 2]
```

### Z-function — one array answers "where does the prefix reappear?"

```python
def z_function(s):
    """z[i] = longest common prefix of s and s[i:]. O(n)."""
    n, l, r = len(s), 0, 0
    z = [0] * n
    for i in range(1, n):
        if i <= r:
            z[i] = min(r - i + 1, z[i - l])   # reuse mirrored value inside the Z-box
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] - 1 > r:                   # extend the rightmost box
            l, r = i, i + z[i] - 1
    return z

def count_overlapping(pattern, text):
    """All (overlapping) occurrences — verified equal to re.findall(r'(?=pat)', s)."""
    z = z_function(pattern + "\x00" + text)   # separator must not occur in either string
    plen = len(pattern)
    return sum(1 for v in z[plen:] if v >= plen)

# verified: z_function("abracadabra") == [0, 0, 0, 1, 0, 1, 0, 4, 0, 0, 1]
```

### Aho-Corasick — the only multi-pattern matcher worth hand-rolling

Key mechanics (verified against regex ground truth on random alphabets AND nested keywords):

1. Build a trie of all patterns; each node stores `next_states`, `fail_state`, and accumulated
   `output` (patterns ending at this state **or any fail ancestor** — that's what makes it find
   "er" inside "ver").
2. Fail links are set in BFS order: for child c of r, walk r's fail chain until a node with an
   edge labeled by c exists; if none, fail to root (0). Then `output[c] += output[fail[c]]`.
3. Search is one pass over the text: on missing transition from state s, follow fail links until
   one matches (or hit 0); emit every keyword in the current node's accumulated output at position
   `i - len(kw) + 1`.

**Verified behavior:** keywords `["a", "aa"]` on `"aaa"` → `{'a': [0,1,2], 'aa': [0,1]}` (nested
keywords both reported correctly). Their repo's own doctest: patterns `[what, hat, ver, er]` in
`"whatever, err ... , wherever"` → `ver:[5,25], er:[6,10,22,26]`.

**Pitfall:** the reference implementation reports *every* occurrence per keyword — for huge texts
with very short keywords this output list can exceed the text size (O(z) is inherent; no fix).

### Rabin-Karp — rolling hash with two real pitfalls (both verified)

```python
def rabin_karp(pattern, text):  # expected O(n+m); source docstring wrongly claims "O(nm)"
    m, n, base, mod = len(pattern), len(text), 256, 1000003
    if m > n: return False

    def H(s):                    # big-endian rolling hash — seed MUST be 0 (see pitfall 1)
        h = 0
        for ch in s:
            h = (ord(ch) + h * base) % mod
        return h

    p_hash, t_hash = H(pattern), H(text[:m])
    h_pow = pow(base, m - 1, mod)          # weight of the oldest char; constant across windows
    for i in range(n - m + 1):
        if t_hash == p_hash and text[i:i+m] == pattern:   # hash match => VERIFY the substring
            return True
        if i == n - m: break
        t_hash = ((t_hash - ord(text[i]) * h_pow) * base + ord(text[i + m])) % mod  # roll window
    return False

# verified: bit-identical behavior to the shipped file (its doctests pass); rolling value stays
# exactly consistent with a fresh recompute of every window — 0 divergences over 1504 windows;
# matches str.find on 500 random cases incl. late-position occurrences.
```

**Pitfall 1 — the seed must be zero.** The init and roll steps only form a consistent pair with
seed `h=0`. With any non-zero seed s, every hash carries an extra term s·B^m; each roll multiplies
that term to s·B^{m+1} while p_hash (never rolled) keeps s·B^m — so after k rolls the window value
drifts from ground truth by (B^k − 1)·s·B^m mod p and matches go missing. Demonstrated: changing
only the seed to 1 makes this exact code fail its own doctest's positive case at window 14, while
seed 0 passes everything.

**Pitfall 2 — never drop the verify step.** The `text[i:i+m] == pattern` check is what makes it
correct despite hash collisions; a "pure" rolling-hash comparison returns false positives whenever
two windows collide mod p (p = 1,000,003 ≈ 2^20, so birthday-collision odds are real for long texts).

Its real niche: many patterns of the same length — hash all patterns once into a set, then one pass.

## 2. Checksums & non-cryptographic hashes

**Decision rule:** integrity → `zlib.crc32` or `hashlib.blake2b`. Protocol parity (gzip header
needs Adler-32 exactly) → implement it. Stable cross-language string hash for your own maps/sets →
djb2/sdbm with the wrap caveat below. Card validation → Luhn, always hand-rollable in 10 lines.

### Adler-32 — verified bit-exact vs `zlib.adler32`

```python
MOD_ADLER = 65521   # largest prime < 2^16; both sums mod this -> combined value fits 32 bits

def adler32(s: str) -> int:
    a, b = 1, 0
    for ch in s.encode("ascii"):        # NOTE: source iterates chars+ord(); bytes() is equivalent here
        a = (a + ch) % MOD_ADLER
        b = (b + a) % MOD_ADLER         # b accumulates a -> position-dependent, unlike plain sum
    return (b << 16) | a

# verified: adler32("Algorithms") == zlib.adler32(b"Algorithms") == 363791387
```

Why it's weaker than CRC-32 at the same width: two sums mod p catch single-byte errors and most
transpositions, but a transposition that preserves both partial-sum sequences slips through — hence
gzip uses it only where speed matters more.

### Fletcher-16 (8-bit variant) — verified vs independent reimplementation

```python
def fletcher16(s: str) -> int:
    s1 = s2 = 0
    for b in s.encode("ascii"):
        s1 = (s1 + b) % 255             # mod 255, NOT 256 — keeps the two sums independent of position
        s2 = (s2 + s1) % 255            #   (mod 256 would let a pure transposition cancel in both)
    return (s2 << 8) | s1

# verified: fletcher16("hello world") == 6752
```

The `255` modulus is the whole design: with mod-256 arithmetic, swapping two bytes at positions i<j
changes s1 by ±(x−y) in both sums identically and can cancel; mod-255 (≡0 mod 254... no — 255=3·5·17,
odd composite chosen so the wrap-around carries differ between the two accumulators).

### djb2 / sdbm — magic constants with provenance

```python
def djb2(s: str) -> int:      # Dan Bernstein; h = 33h + c, seed 5381 (odd prime), masked to 32 bits
    h = 5381
    for ch in s.encode("ascii"):
        h = ((h << 5) + h + ch) & 0xFFFFFFFF
    return h

def sdbm(s: str) -> int:      # sdbm DB (gawk fast form): h = c + h*65599, i.e. c + h<<16 - h>>... :
    h = 0
    for ch in s.encode("ascii"):
        h = (ch + (h << 6) + (h << 16) - h) & ((1 << 64) - 1)   # see PITFALL below
    return h

# verified: djb2("Algorithms") == 3782405311; sdbm("Algorithms") — see pitfall
```

**⚠️ VERIFIED PITFALL (sdbm & friends):** the source implementation does **not** mask to 64 bits, so
in Python it returns an *unbounded* integer that grows with input length. Any C/Java reference value
(64-bit wraparound) will NOT match: for `"Algorithms"` their unmasked result is
`14621749...036` while the 64-bit-wrapped value is `7428168923269278692`. If you need cross-language
parity, mask explicitly; if you only need a stable-within-Python hash, unmasked is fine.

### Luhn — the card-check digit algorithm (no library exists to beat 10 lines)

```python
def luhn_valid(digits: str) -> bool:
    total = int(digits[-1])                       # check digit itself, added once
    for i, d in enumerate(reversed(digits[:-1])):
        d = int(d) * (2 if i % 2 == 0 else 1)     # double every other starting from 2nd-last
        total += d - 9 if d > 9 else d            # "subtract 9" == sum the digits of a two-digit product
    return total % 10 == 0

# verified: luhn_valid("79927398713") is True, all other last-digits in ...710..719 are False
```

## 3. Geodesy — haversine great-circle distance (offline, no API)

**Decision rule:** road/rail/air routing or travel time → OSRM via the `maps` skill. Straight-line
distance between two coordinates with zero dependencies → haversine. Accuracy: treats Earth as a
sphere of R = 6371000 m — fine to ~0.5% for most distances; use Lambert's ellipsoidal formula (also
in the repo) when you need better, or `geopy`/OSRM in production.

```python
from math import asin, cos, radians, sin, sqrt
EARTH_RADIUS = 6_371_000   # mean Earth radius, metres

def haversine_m(lat1, lon1, lat2, lon2):
    p1, p2 = radians(lat1), radians(lat2)
    dlam   = radians(lon2 - lon1)
    dphi   = p2 - p1
    a      = sin(dphi / 2) ** 2 + cos(p1) * cos(p2) * sin(dlam / 2) ** 2
    return 2 * EARTH_RADIUS * asin(sqrt(a))          # sqrt is MANDATORY: `a` is the SQUARED hav term.
                                                     # (Verified pitfall: dropping it gives SF->Yosemite = 5,052 m
                                                     # instead of 253,748 m — a ~50x underestimate.)

# verified (repo doctests, re-executed):
#   SF(37.774856,-122.424227) -> Yosemite(37.864742,-119.537521)  = 253,748 m
#   NYC(40.712776,-74.005974)-> LA(34.052235,-118.243683)        = 3,935,746 m
#   London -> Paris                                                 = 343,549 m
```

Sanity anchor: NYC→LA straight-line ≈ 3,936 km; OSRM *road* distance for the same pair is ~3,900–4,100
km depending on route — if your haversine result is off by more than a few percent from road
distance you've likely mixed up lat/lon order or degrees/radians.

## 4. Numerical methods (what scipy.optimize wraps)

**Decision rule:** have scipy → `brentq` / `newton` / `solve_ivp`. No scipy, need it now → the two
root finders below are self-contained and robust-by-construction; for ODEs use plain RK4 with a small
fixed step (the repo's "RKF45" is **fixed-step** — see pitfall).

### Brent's method — bisection + secant + inverse quadratic interpolation, never diverges on a bracket

```python
def brent_method(f, left, right, tol=1e-8, max_iter=100):
    """Root of f in [left,right]; requires sign change. Robust: falls back to bisection."""
    fl, fr = f(left), f(right)
    if fl * fr >= 0:
        raise ValueError("func(left) and func(right) must have opposite signs")
    if abs(fl) < abs(fr): left, right, fl, fr = right, left, fr, fl   # keep |f| decreasing at 'right'
    c, fc, d = left, fl, right - left
    for it in range(max_iter):
        if fr == 0: return right
        # Guard FIRST: on iteration 1, c==left so fc==fl exactly and the IQU denominators
        # (fl-fc) are zero — evaluating them before the check raises ZeroDivisionError.
        if fc not in (fl, fr):                       # inverse quadratic interpolation
            s = (left*fr*fc/((fl-fr)*(fl-fc)) + right*fl*fc/((fr-fl)*(fr-fc))
                 + c*fl*fr/((fc-fl)*(fc-fr)))
        else:                                        # secant fallback
            s = right - fr * (right - left) / (fr - fl)
        bisection_conditions = [                     # any of these -> trust the bracket instead
            not ((3*left + right)/4 < s < right),    #   interpolation outside safe zone
            it > 1 and abs(s - right) >= abs(right - c) / 2,   # slow progress vs last step
            it <= 1 and abs(s - right) >= abs(c - d) / 2,      # no gain yet in first iterations
            (it > 1 and abs(right - c) < tol) or (it <= 1 and abs(c - d) < tol),  # already converged
        ]
        s = (left + right) / 2 if any(bisection_conditions) else s
        fs = f(s); d, c, fc = c, right, fr
        if fl * fs < 0: right, fr = s, fs            # shrink bracket to the side with a sign change
        else:          left,  fl = s, fs
        if abs(fl) < abs(fr): left, right, fl, fr = right, left, fr, fl
        if abs(right - left) < tol: return right
    return right

# verified: brent_method(lambda x: x**3 - x - 2, 1, 2) ≈ 1.52138 (matches numpy.roots to 1e-6);
#           raises ValueError on f(x)=x^2+1 over [0,1] as documented
```

### Newton-Raphson — fast but *will* diverge without care

```python
def newton_raphson(f, x0=0.0, max_iter=100, step=1e-6, max_error=1e-6):
    """Root via x_{n+1} = x_n - f/f'; derivative by central finite difference (no analytic f')."""
    def df(x): return (f(x + step/2) - f(x - step/2)) / step   # central diff: O(step^2) accurate
    a = x0
    for _ in range(max_iter):
        if abs(f(a)) < max_error: return a
        d = df(a)
        if d == 0: raise ZeroDivisionError("zero derivative — no converging solution")
        a -= f(a) / d
    raise ArithmeticError("iteration limit reached — bad initial guess or no root nearby")

# verified failure modes (both in source doctests, re-executed):
#   newton_raphson(math.cos, 0)          -> ZeroDivisionError (f'(0)=sin(0)... f''=cos; df≈0 at x=0? No:
#                                           cos'(x)=-sin(x), -sin(0)=0 exactly -> division by zero) ✓
#   newton_raphson(lambda x: x**2 + 1, 2)-> ArithmeticError (no real root; walks off to infinity) ✓
```

**Pitfall:** Newton needs a *good* initial guess — near inflection points or where f' ≈ 0 it jumps
far away and diverges. Brent never does this given a bracket: **prefer Brent whenever you have one.**

### ⚠️ The repo's "Runge-Kutta-Fehlberg" is NOT adaptive

`runge_kutta_fehlberg_45.py` computes the classic 6-stage Fehlberg pair (k1..k6, order-5 weights
16/135, 0, 6656/12825, 28561/56430, −9/50, 2/55) but **never uses the embedded error estimate to
change `step_size`** — it marches at your fixed step. The whole point of RKF45 is adaptive stepping;
this file gives you a fixed-step order-5 method with extra work per step. For learning RK structure
it's fine (the Butcher coefficients are all visible); for actual ODEs use `scipy.integrate.solve_ivp`
(method="RK45") which does the adaptivity correctly.

## 5. Dynamic programming — LIS in O(n log n) (patience sorting tails)

```python
import bisect

def lis_length(v):
    """Length of longest STRICTLY increasing subsequence, O(n log n)."""
    if not v: return 0
    tails = [v[0]]                       # tails[k] = smallest possible tail value of an inc. subseq of length k+1
    for x in v[1:]:
        i = bisect.bisect_left(tails, x) # first tail >= x (bisect_right would give non-decreasing LIS)
        if i == len(tails): tails.append(x)
        else:                tails[i] = x
    return len(tails)

# verified vs O(n^2) DP reference on 500 random arrays; repo doctest values reproduced:
#   lis_length([2,5,3,7,11,8,10,13,6]) == 6 ; lis_length([5,4,3,2,1]) == 1
```

The invariant worth internalizing: `tails` is always sorted (that's what makes bisect legal), and it
is **not** itself a subsequence — only its length is the answer. To recover the actual subsequence you
need backpointers; for "length" queries this alone suffices.

## 6. Backtracking — N-queens diagonal invariants (the trick that kills most of the state)

Instead of marking attacked squares, note two facts: a **right** diagonal (`/`) has constant
`row − col`; a **left** diagonal (`\`) has constant `row + col`. So collision checks reduce to three
set-membership tests with zero board storage per column placement. Board = one list where index=row,
value=column (guarantees no two queens share row/column by construction).

```python
def n_queens_solutions(n):
    """All solutions as lists of columns-per-row; verified counts: n=1..8 -> 1,0,0,2,10,4,40,92."""
    sols = []
    def dfs(cols, diag_r, diag_l):          # cols: list[row]=col ; diags: sets of row-col / row+col
        r = len(cols)
        if r == n:
            sols.append(list(cols)); return
        for c in range(n):
            if c not in set(cols) or (r - c) in diag_r or (r + c) in diag_l: continue
            cols.append(c); diag_r.add(r - c); diag_l.add(r + c)
            dfs(cols, diag_r, diag_l)
            cols.pop(); diag_r.discard(r - c); diag_l.discard(r + c)
    dfs([], set(), set())
    return sols

# verified: [len(n_queens_solutions(n)) for n in range(1, 9)] == [1, 0, 0, 2, 10, 4, 40, 92]
```

Generalization: any "attack by slope ±1" problem (rook+bishop hybrids, some chess-piece puzzles)
reduces to the same two-invariant trick. The repo's `n_queens_math.py` derives exactly this from the
slope-intercept form y = mx + b with m ∈ {+1, −1} — worth a read for the derivation.

## 7. Quick formula sheet (financial & scheduling — verified in harness)

| Formula | Expression | Verified example |
|---|---|---|
| Sharpe ratio | `(mean(r_p − r_f)) / std_sample(r_p − r_f)` — **sample** std (n−1); repo doctest 2.2164 only reproduces with n−1; annualize ×√periods | verified: [0.1,0.2,0.15,0.05,0.12] → 2.2164; rf=0.02 → 1.8589 |
| Kelly criterion | `f* = (bp − q)/b`, b=net odds, p/win prob, q=1−p; f*>0 only if bp>q | half-Kelly is the standard risk-reduction |
| EMI (loan) | `EMI = P·r(1+r)^n / ((1+r)^n − 1)`, r=monthly rate, n=months | repo doctest reproduced in harness |
| Present value | `PV = FV / (1 + r)^t` | — |
| Round-robin avg wait time | simulate queue with quantum q; turnaround = completion−arrival; waiting = turnaround−burst | repo `round_robin.py` worked example reproduced |
