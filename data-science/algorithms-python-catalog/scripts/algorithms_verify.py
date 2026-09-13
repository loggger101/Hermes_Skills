"""Re-runnable verification harness for data-science/algorithms-python-catalog.

Every claim in SKILL.md and references/*.md is asserted here live. Stdlib-only;
the numpy cross-check (Brent vs roots) runs only if numpy is importable, else it
falls back to an analytic root check. Run:  py algorithms_verify.py
Verified at mining time: 2026-09-13, Python 3.13, Windows 11 — all checks pass.

Source under test: TheAlgorithms/Python @ 23c4208 (MIT). Snippets here are the
verified reference implementations recorded in references/algorithms-from-scratch.md;
the harness re-proves their behavior rather than importing from a clone, so it
stays self-contained and re-runnable anywhere.
"""

from __future__ import annotations

import bisect
import math
import random
import re
import sys
import zlib

PASS = 0


def check(name: str, cond: bool) -> None:
    global PASS
    if not cond:
        print(f"FAIL {name}")
        raise SystemExit(1)
    PASS += 1
    print(f"ok   {name}")


# ---------------------------------------------------------------- string matching

def get_failure_array(pattern):
    failure, i, j = [0], 0, 1
    while j < len(pattern):
        if pattern[i] == pattern[j]:
            i += 1
        elif i > 0:
            i = failure[i - 1]
            continue
        j += 1
        failure.append(i)
    return failure


def knuth_morris_pratt(text, pattern):
    if not pattern:
        return 0
    failure = get_failure_array(pattern)
    i, j = 0, 0
    while i < len(text):
        if pattern[j] == text[i]:
            if j == len(pattern) - 1:
                return i - j
            j += 1
        elif j > 0:
            j = failure[j - 1]
            continue
        i += 1
    return -1


def z_function(s):
    n, l, r = len(s), 0, 0
    z = [0] * n
    for i in range(1, n):
        if i <= r:
            z[i] = min(r - i + 1, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] - 1 > r:
            l, r = i, i + z[i] - 1
    return z


def count_overlapping(pattern, text):
    z = z_function(pattern + "\x00" + text)
    plen = len(pattern)
    return sum(1 for v in z[plen:] if v >= plen)


class _ACNode:
    __slots__ = ("next", "fail", "out")

    def __init__(self):
        self.next = {}
        self.fail = None
        self.out = []


def aho_corasick_build(keywords):
    root = _ACNode()
    for kw in keywords:
        node = root
        for ch in kw:
            node = node.next.setdefault(ch, _ACNode())
        node.out.append(kw)
    from collections import deque

    q = deque()
    for node in root.next.values():
        node.fail = root          # depth-1 nodes fail to root — CRITICAL; skipping this line
                                  # makes every depth-2 fail link skip a level (verified bug:
                                  # keywords ['ab','b'] on 'bbbbbabbaa...' missed half the matches)
        q.append(node)
    while q:
        r = q.popleft()
        for ch, c in r.next.items():
            f = r.fail
            while f is not root and ch not in f.next:
                f = f.fail
            c.fail = f.next.get(ch, root)
            if c.fail is c:       # self-loop guard (single-char keyword at depth 1)
                c.fail = root
            c.out = c.out + c.fail.out   # inherit outputs of fail ancestors ("er" inside "ver")
            q.append(c)
    return root


def aho_corasick_search(keywords, text):
    root = aho_corasick_build(keywords)
    result = {}
    state = root
    for i, ch in enumerate(text):
        while state is not root and ch not in state.next:
            state = state.fail or root
        if ch in state.next:
            state = state.next[ch]
        else:
            state = root
        for kw in state.out:
            result.setdefault(kw, []).append(i - len(kw) + 1)
    return result


def rabin_karp(pattern, text):
    """Textbook Rabin-Karp: big-endian rolling hash (h = c + h*B mod p), seed 0 — see PITFALL below."""
    m, n, base, mod = len(pattern), len(text), 256, 1000003
    if m > n:
        return False

    def H(s):
        h = 0                                  # seed MUST be 0 for init/roll to stay consistent
        for ch in s:
            h = (ord(ch) + h * base) % mod
        return h

    p_hash = H(pattern)
    t_hash = H(text[:m])
    h_pow = pow(base, m - 1, mod)              # weight of the oldest char; constant across windows
    for i in range(n - m + 1):
        if t_hash == p_hash and text[i : i + m] == pattern:   # hash match => VERIFY the substring
            return True
        if i == n - m:
            break
        t_hash = ((t_hash - ord(text[i]) * h_pow) * base + ord(text[i + m])) % mod  # roll window
    return False


# PITFALL (verified by construction): init and roll form a consistent pair ONLY with seed 0.
# With any non-zero seed s, the hash carries an extra B^m*s term; each roll multiplies it to
# B^{m+1}*s while a fresh re-init would give B^m*s — so after k rolls the rolling value drifts
# from ground truth by (B^m-1)*(B^k-1)*s mod p, producing false negatives. Demonstrated:
# seeding this exact code with 1 makes its own doctest positive case fail at window 14.


rng = random.Random(20260913)

# KMP vs str.find on 500 random binary strings (first-occurrence semantics match find())
for _ in range(500):
    n = rng.randint(1, 300)
    text = "".join(rng.choice("ab") for _ in range(n))
    pat = "".join(rng.choice("ab") for _ in range(rng.randint(1, min(8, n))))
    assert knuth_morris_pratt(text, pat) == text.find(pat), (text[:40], pat)
check("KMP first-occurrence == str.find on 500 random cases", True)

# KMP failure-array doctest value from source file
assert get_failure_array("aabaabaaa") == [0, 1, 0, 1, 2, 3, 4, 5, 2]
check("KMP failure array 'aabaabaaa' -> [0,1,0,1,2,3,4,5,2]", True)

# Z-function: doctest values + overlapping count vs regex ground truth (500 random cases)
assert z_function("abracadabra") == [0, 0, 0, 1, 0, 1, 0, 4, 0, 0, 1]
for _ in range(500):
    n = rng.randint(2, 120)
    text = "".join(rng.choice("abc") for _ in range(n))
    pat = "".join(rng.choice("abc") for _ in range(rng.randint(1, min(4, n))))
    assert count_overlapping(pat, text) == len(re.findall("(?=" + re.escape(pat) + ")", text)), (text, pat)
check("Z-function doctest value + overlap counts vs regex on 500 random cases", True)

# Aho-Corasick: per-pattern overlapping occurrence positions vs regex ground truth.
# Includes nested keywords ('a' inside 'aa') and duplicate-free keyword sets only —
# NOTE: passing the SAME keyword twice to any AC implementation double-counts it;
# dedupe first (the TheAlgorithms reference behaves identically).
for _ in range(300):
    kws = list({"".join(rng.choice("ab") for _ in range(rng.randint(1, 5))) for _ in range(8)})
    text = "".join(rng.choice("ab") for _ in range(rng.randint(10, 120)))
    got = aho_corasick_search(kws, text)
    for kw in kws:
        truth = [m.start() for m in re.finditer("(?=" + re.escape(kw) + ")", text)]
        assert sorted(got.get(kw, [])) == truth, (text, kw, got.get(kw), truth)
# the repo's own doctest case, verbatim
assert aho_corasick_search(["what", "hat", "ver", "er"], "whatever, err ... , wherever") == {
    "what": [0], "hat": [1], "ver": [5, 25], "er": [6, 10, 22, 26]
}
# nested-keyword case verified against regex truth
assert aho_corasick_search(["a", "aa"], "aaa") == {"a": [0, 1, 2], "aa": [0, 1]}
check("Aho-Corasick positions vs regex ground truth (300 random + repo doctest + nested)", True)

# Rabin-Karp: positive and negative cases incl. hash-collision safety via the verify step
assert rabin_karp("abc1abc12", "alskfjaldsabc1abc1abc12k23adsfabcabc") is True
assert rabin_karp("abc1abc12", "alskfjaldsk23adsfabcabc") is False
for _ in range(200):
    n = rng.randint(5, 150)
    text = "".join(rng.choice("ab") for _ in range(n))
    pat = "".join(rng.choice("ab") for _ in range(rng.randint(1, min(6, n))))
    assert rabin_karp(pat, text) == (text.find(pat) != -1), (text[:40], pat)
check("Rabin-Karp find/no-find vs str.find on 200 random cases", True)

# ---------------------------------------------------------------- checksums & hashes


def adler32(s: str) -> int:
    a, b = 1, 0
    for ch in s.encode("ascii"):
        a = (a + ch) % 65521
        b = (b + a) % 65521
    return (b << 16) | a


def fletcher16(s: str) -> int:
    s1 = s2 = 0
    for b in s.encode("ascii"):
        s1 = (s1 + b) % 255
        s2 = (s2 + s1) % 255
    return (s2 << 8) | s1


def djb2(s: str) -> int:
    h = 5381
    for ch in s.encode("ascii"):
        h = ((h << 5) + h + ch) & 0xFFFFFFFF
    return h


def sdbm_unmasked(s: str) -> int:   # as shipped by TheAlgorithms (no wrap mask)
    h = 0
    for ch in s.encode("ascii"):
        h = ch + (h << 6) + (h << 16) - h
    return h


def sdbm_64(s: str) -> int:         # C-style 64-bit wrap — the cross-language value
    h = 0
    for ch in s.encode("ascii"):
        h = (ch + (h << 6) + (h << 16) - h) & ((1 << 64) - 1)
    return h


for t in ["Algorithms", "go adler em all", "", "hello world\nThe quick brown fox"]:
    assert adler32(t) == zlib.adler32(t.encode("ascii")), t
check("Adler-32 bit-exact vs zlib.adler32 (4 cases incl. empty string)", True)

assert fletcher16("hello world") == 6752 and fletcher16("onethousandfourhundredthirtyfour") == 28347
check("Fletcher-16 doctest values", True)

assert djb2("Algorithms") == 3782405311 and djb2("scramble bits") == 1609059040
check("djb2 doctest values (seed 5381, *33+c)", True)

# the documented pitfall: unmasked Python int != C-style 64-bit wrap for the same input
assert sdbm_unmasked("Algorithms") == 1462174910723540325254304520539387479031000036
assert sdbm_64("Algorithms") == 7428168923269278692
assert sdbm_unmasked("Algorithms") != sdbm_64("Algorithms")   # the pitfall, made explicit
check("sdbm: unmasked (repo) vs 64-bit-wrapped values differ — pitfall documented", True)


def luhn_valid(digits: str) -> bool:
    total = int(digits[-1])
    for i, d in enumerate(reversed(digits[:-1])):
        d = int(d) * (2 if i % 2 == 0 else 1)
        total += d - 9 if d > 9 else d
    return total % 10 == 0


assert luhn_valid("79927398713") is True
assert all(luhn_valid(f"7992739871{d}") is False for d in "012456789")
check("Luhn: 79927398713 valid, every other last digit invalid", True)

# ---------------------------------------------------------------- geodesy


def haversine_m(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlam = math.radians(lon2 - lon1)
    dphi = p2 - p1
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlam / 2) ** 2
    return 2 * 6_371_000 * math.asin(math.sqrt(a))   # sqrt is MANDATORY — a is the squared hav term;
                                                     # dropping it underestimates by ~sqrt(1/a) (verified:
                                                     # SF->Yosemite came out 5,052 m instead of 253,748 m)


assert round(haversine_m(37.774856, -122.424227, 37.864742, -119.537521)) == 253_748
assert round(haversine_m(40.712776, -74.005974, 34.052235, -118.243683)) == 3_935_746
assert round(haversine_m(51.507351, -0.127758, 48.856614, 2.352222)) == 343_549
# quarter-equator sanity: pi/2 * R ~ 10,007,543 m (within 0.1%)
assert abs(haversine_m(0, 0, 0, 90) - 10_007_543) / 10_007_543 < 1e-3
check("haversine: SF->Yosemite 253,748 m; NYC->LA 3,935,746 m; London->Paris 343,549 m", True)

# ---------------------------------------------------------------- numerical methods


def brent_method(f, left, right, tol=1e-8, max_iter=100):
    fl, fr = f(left), f(right)
    if fl * fr >= 0:
        raise ValueError("func(left) and func(right) must have opposite signs")
    if abs(fl) < abs(fr):
        left, right, fl, fr = right, left, fr, fl
    c, fc, d = left, fl, right - left
    for it in range(max_iter):
        if fr == 0:
            return right
        # NOTE: guard FIRST — on iteration 1, c==left so fc==fl exactly and the IQU
        # denominators (fl-fc) are zero; evaluating them before the check crashes.
        if fc not in (fl, fr):   # inverse quadratic interpolation
            s = (left * fr * fc / ((fl - fr) * (fl - fc)) + right * fl * fc / ((fr - fl) * (fr - fc))
                 + c * fl * fr / ((fc - fl) * (fc - fr)))
        else:                    # secant fallback
            s = right - fr * (right - left) / (fr - fl)
        bisection_conditions = [
            not ((3 * left + right) / 4 < s < right),
            it > 1 and abs(s - right) >= abs(right - c) / 2,
            it <= 1 and abs(s - right) >= abs(c - d) / 2,
            (it > 1 and abs(right - c) < tol) or (it <= 1 and abs(c - d) < tol),
        ]
        s = (left + right) / 2 if any(bisection_conditions) else s
        fs = f(s)
        d, c, fc = c, right, fr
        if fl * fs < 0:
            right, fr = s, fs
        else:
            left, fl = s, fs
        if abs(fl) < abs(fr):
            left, right, fl, fr = right, left, fr, fl
        if abs(right - left) < tol:
            return right
    return right


def newton_raphson(f, x0=0.0, max_iter=100, step=1e-6, max_error=1e-6):
    def df(x):
        return (f(x + step / 2) - f(x - step / 2)) / step

    a = x0
    for _ in range(max_iter):
        if abs(f(a)) < max_error:
            return a
        d = df(a)
        if d == 0:
            raise ZeroDivisionError("zero derivative")
        a -= f(a) / d
    raise ArithmeticError("iteration limit reached")


root = brent_method(lambda x: x**3 - x - 2, 1, 2)
try:
    import numpy as np

    ref = [r.real for r in np.roots([1, 0, -1, -2]) if abs(r.imag) < 1e-9][0]
    assert abs(root - ref) < 1e-6, (root, ref)
    check(f"Brent x^3-x-2 on [1,2]: {root:.7f} == numpy.roots real root {ref:.7f}", True)
except ImportError:
    # analytic cross-check: plastic constant ~1.5213797068045676 (Cardano)
    assert abs(root - 1.5213797068045676) < 1e-6, root
    check(f"Brent x^3-x-2 on [1,2]: {root:.7f} == analytic real root (no numpy)", True)

try:
    brent_method(lambda x: x**2 + 1, 0, 1)
    raise AssertionError("expected ValueError")
except ValueError:
    check("Brent raises ValueError on sign-less bracket [x^2+1 over 0..1]", True)

r = newton_raphson(math.sin, 1.0)
assert abs(r - 0.0) < 1e-6
# NOTE: convergence is on |f(a)| (default max_error=1e-6), so x lands within ~|x·max_error| of e;
# use a matching tolerance — the source doctest passes max_error=1e-15 for this exact case.
assert math.isclose(newton_raphson(lambda x: math.log(x) - 1, 2.0), math.e, rel_tol=1e-6)
try:
    newton_raphson(math.cos, 0.0)
    raise AssertionError("expected ZeroDivisionError")
except ZeroDivisionError:
    pass
try:
    newton_raphson(lambda x: x**2 + 1, 2.0)
    raise AssertionError("expected ArithmeticError")
except ArithmeticError:
    pass
check("Newton: sin@1->0, log-1@2->e; diverges (ZeroDivision / ArithmeticError) as documented", True)

# ---------------------------------------------------------------- DP & backtracking


def lis_length(v):
    if not v:
        return 0
    tails = [v[0]]
    for x in v[1:]:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)


def lis_length_dp(v):  # O(n^2) reference oracle
    n = len(v)
    dp = [1] * n
    for i in range(1, n):
        for j in range(i):
            if v[j] < v[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp) if n else 0


for _ in range(300):
    arr = [rng.randint(-50, 50) for _ in range(rng.randint(0, 60))]
    assert lis_length(arr) == lis_length_dp(arr), arr[:20]
assert lis_length([2, 5, 3, 7, 11, 8, 10, 13, 6]) == 6 and lis_length([5, 4, 3, 2, 1]) == 1 and lis_length([]) == 0
check("LIS O(n log n) tails == O(n^2) DP on 300 random arrays + doctest values", True)


def n_queens_count(n):
    sols = []

    def dfs(cols, diag_r, diag_l):
        r = len(cols)
        if r == n:
            sols.append(1)
            return
        used_cols = set(cols)
        for c in range(n):
            if c in used_cols or (r - c) in diag_r or (r + c) in diag_l:
                continue
            cols.append(c)
            diag_r.add(r - c)
            diag_l.add(r + c)
            dfs(cols, diag_r, diag_l)
            cols.pop()
            diag_r.discard(r - c)
            diag_l.discard(r + c)

    dfs([], set(), set())
    return len(sols)


counts = [n_queens_count(n) for n in range(1, 9)]
assert counts == [1, 0, 0, 2, 10, 4, 40, 92], counts
check("N-queens diagonal-invariant DFS: n=1..8 -> [1,0,0,2,10,4,40,92]", True)

# ---------------------------------------------------------------- financial formulas


def emi(principal, rate_per_annum, years_to_repay):
    r = rate_per_annum / 12
    n = years_to_repay * 12
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


assert emi(25000, 0.12, 3) == 830.3577453212793
assert emi(25000, 0.12, 10) == 358.67737100646826
check("EMI doctest values (P=25000 @12%: 3y->830.3577..., 10y->358.6773...)", True)


def sharpe_ratio(returns, risk_free_rate=0.0):
    mean = sum(returns) / len(returns) - risk_free_rate
    # SAMPLE std (n-1 denominator) — matches the repo's verified doctest value 2.2164;
    # population std would give ~2.478 for the same inputs and fail that check.
    var = sum((x - mean - risk_free_rate) ** 2 for x in returns) / (len(returns) - 1)
    std = math.sqrt(var)
    return mean / std if std else float("inf")


assert round(sharpe_ratio([0.1, 0.2, 0.15, 0.05, 0.12]), 4) == 2.2164
assert round(sharpe_ratio([0.1, 0.2, 0.15, 0.05, 0.12], 0.02), 4) == 1.8589
check("Sharpe ratio doctest values (sample-std variant: -> 2.2164; rf=0.02 -> 1.8589)", True)

# ---------------------------------------------------------------- summary
print(f"\nALL {PASS} CHECKS PASSED")
