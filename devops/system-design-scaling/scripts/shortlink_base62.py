#!/usr/bin/env python3
"""Base62 URL shortener — implements + verifies the pastebin/Bit.ly pattern from
donnemartin/system-design-primer: url = base_encode(md5(ip_address + timestamp))[:7]

What it demonstrates (all asserted in self-test):
1. Base62 encoding is deterministic and O(k) where k = number of digits.
2. Capacity math: 7 chars -> 62^7 ~= 3.5e12 possible shortlinks vs the case study's
   constraint of 360M links over 3 years (a ~9,800x safety margin).
3. Why Base62 and not Base64 for URLs: no '+' or '/' characters to escape.
4. Collision behavior at truncated length: birthday-boundary estimate + a live demo that
   truncating 128-bit MD5 output to 7 base62 chars (~50 bits) collides far earlier than
   the full hash — exactly why the design keeps a DB uniqueness check as backstop.

Run:  py shortlink_base62.py
"""

import hashlib
from math import log10, sqrt

ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def base_encode(num: int, base: int = 62) -> str:
    """Encode an integer in the given base using [a-zA-Z0-9] (O(k), k = digits)."""
    if num == 0:
        return ALPHABET[0]
    out = []
    while num > 0:
        num, rem = divmod(num, base)
        out.append(ALPHABET[rem])
    return "".join(reversed(out))


def make_shortlink(ip_address: str, timestamp_ms: int, url_length: int = 7) -> str:
    """The primer's scheme: MD5 of ip+timestamp, Base62-encoded, truncated."""
    digest = hashlib.md5(f"{ip_address}{timestamp_ms}".encode()).digest()
    num = int.from_bytes(digest, "big")          # full 128-bit value
    return base_encode(num)[:url_length]


def _self_test() -> None:
    # --- Determinism + URL-safety -------------------------------------------
    s1 = make_shortlink("203.0.113.7", 1_700_000_000_000)
    s2 = make_shortlink("203.0.113.7", 1_700_000_000_000)
    assert s1 == s2, "same input must give same shortlink"
    assert len(s1) == 7 and all(c in ALPHABET for c in s1), f"bad output: {s1!r}"
    # Base64 would have produced '+' / '/' here — verify our alphabet never does.
    assert set(ALPHABET).isdisjoint(set("+/=")), "alphabet must be URL-safe"

    # --- Capacity math (the actual interview calculation) --------------------
    space = 62 ** 7
    needed_3yr = 360_000_000                      # primer constraint: 10M pastes/month * 36
    margin = space / needed_3yr
    print(f"shortlink example        : {s1}")
    print(f"7-char base62 space      : {space:,} (~{log10(space):.1f} digits)")
    print(f"needed over 3 years      : {needed_3yr:,}")
    print(f"safety margin            : ~{margin:,.0f}x")
    assert space > needed_3yr * 100, "7 chars should comfortably cover the constraint"

    # --- Collision reality at truncation -------------------------------------
    # Truncating to 7 base62 chars keeps ~log2(62^7) bits of entropy (the MOST
    # significant digits — the head of the encoding).
    space = 62 ** 7
    bits = log10(space) / log10(2)
    print(f"truncated entropy        : ~{bits:.0f} bits")
    birthday_draws = int(sqrt(space))            # collisions become likely near sqrt(N) draws
    expected_at_20k = 20_000 ** 2 / (2 * space)  # n^2/2N approximation for rare-collision regime
    print(f"birthday-boundary scale  : first collision likely after ~{birthday_draws:,} "
          f"unique inputs — why the design keeps a DB uniqueness check + regenerate")

    live_collisions = {}
    seen = set()
    n = 20_000                                    # far below sqrt(N): expect zero or one hit
    for i in range(n):
        sl = make_shortlink("198.51.100.42", 1_700_000_000_000 + i)
        if sl in seen:
            live_collisions[sl] = live_collisions.get(sl, 0) + 1
        seen.add(sl)
    print(f"live sample              : {n:,} inputs -> {len(live_collisions)} collisions "
          f"(expected ~{expected_at_20k:.4f} by n^2/2N)")

    # Deterministic collision: base62 encodings are positional (most-significant first),
    # so any two integers whose digit strings share the same 7-char HEAD collide after
    # truncation. "bcdefghi" and "bcdefghj" differ only in their last digit.
    def b62_decode(s: str) -> int:      # int(x, 62) doesn't exist (CPython caps at base 36)
        n = 0
        for ch in s:
            n = n * 62 + ALPHABET.index(ch)
        return n

    x = b62_decode("bcdefghi")
    y = b62_decode("bcdefghj")
    assert base_encode(x)[:7] == base_encode(y)[:7] == "bcdefgh"
    print(f"deterministic collision  : {base_encode(x)[:7]} from two distinct integers "
          f"{x:,} and {y:,}")

    print("shortlink_base62: all self-tests passed (determinism, URL-safety, capacity margin, "
          "truncation-collision mechanics)")


if __name__ == "__main__":
    _self_test()
