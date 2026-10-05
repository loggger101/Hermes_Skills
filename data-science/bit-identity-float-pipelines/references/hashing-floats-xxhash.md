---
description: "Choosing and using a hash for bit-identity checks: xxh3 vs sha256 measured on this machine, canonical byte layout for float arrays (-0.0, NaN, endianness, order, dtype)"
source_repo: Cyan4973/xxHash (BSD-2-Clause library) + python-xxhash 4.0.1
tested_version: xxhash 4.0.1 (libxxhash 0.8.3) pip --target on Windows py3.14, run live; bandwidth numbers are one 256 MiB run on this box
verified_date: "2026-10-05"
---

# Hashing floats for bit-identity: algorithm and byte layout

A bit-identity gate is only as good as two choices: *which hash* and *which bytes go into it*. The second matters more.

## Which hash

xxHash is a non-cryptographic hash family. The README states outputs are identical on every platform (little- and big-endian)
and, once an algorithm is finalized, stable across xxHash releases. XXH3 (since v0.8.0) is the recommended default for new
work; `XXH3_128bits` when 128 bits are wanted. It is **not** collision-resistant against an adversary.

Live on this machine, one 256 MiB random buffer, Python bindings:

| Hash | Bandwidth |
|---|---|
| `xxh3_64` | 17.3 GB/s |
| `xxh3_128` | 17.3 GB/s |
| `xxh64` | 13.7 GB/s |
| `xxh32` | 6.1 GB/s |
| `hashlib.sha256` | 2.2 GB/s (probably CPU SHA extensions) |
| `hashlib.blake2b` | 1.0 GB/s |
| `hashlib.md5` | 0.95 GB/s |

Rule of thumb: use `xxh3_128` to detect an accidental change in your own pipeline outputs (a regression gate); use `sha256`
when the hash is a security or provenance claim (anything signed, published as an integrity check, or compared against
an untrusted party). The gap on this CPU was about 8x, which matters for hashing many GB of intermediate arrays and not at all for a
few CSVs. Whatever you pick, **record the algorithm name beside the digest** (`xxh3_128:99aa...`) so a future change of
algorithm is not mistaken for a regression.

Known-answer checks (verified): `xxh32('')=02cc5d05`, `xxh64('')=ef46db3751d8e999`, `xxh3_64('')=2d06800538d394c2`,
`xxh3_128('')=99aa06d3014798d86001c324468d497f`, `xxh64('abc')=44bc2cf5ad770999`, `xxh3_64('abc')=78af5f94892f3950`.
A seed changes the digest, and streaming (`update` pieces) equals the one-shot digest. Keep a test that asserts the empty-input vectors,
so a binding or library swap that changes output fails loudly.

```python
import xxhash, numpy as np
h = xxhash.xxh3_128()
for chunk in chunks: h.update(chunk)          # stream large files; constant memory
digest = "xxh3_128:" + h.hexdigest()
```

## Which bytes (the part that silently breaks the gate)

Hash a **canonical byte string**, not "whatever the array holds". Each of these was reproduced:

| Trap | Observed | Canonicalise by |
|---|---|---|
| `-0.0` vs `0.0` | compare equal (`==` True) but the 8 bytes differ | add `0.0` (`x + 0.0` turns -0.0 into 0.0) or normalise explicitly, and decide once whether a sign flip counts as a change |
| NaN payloads | two NaNs (`0x7FF8...0` and `0x7FF8...1`) are both `isnan` but their bytes differ | replace NaNs with one canonical NaN before hashing (`np.where(np.isnan(x), np.nan, x)`) |
| Endianness | `>f8` and `<f8` bytes differ, so digests differ | cast to an explicit little-endian dtype (`<f8`) |
| dtype width | the same values as `<f4` and `<f8` give different bytes | fix the dtype in the hasher, not in the producer |
| Element order | `tobytes("C")` differs from `tobytes("F")` for a 2-D array | always `tobytes("C")` on a C-contiguous copy (`np.ascontiguousarray`) |
| Container metadata | shape and dtype are not in the bytes | hash `repr` of `(shape, dtype.str)` first, then the data, so a reshape is a change |

This is the same lesson as the comparator bugs in `SKILL.md`: report the hash **and** a column diff, and when they disagree
the comparator is what broke. A hash that ignores `-0.0` or NaN payload differences is a deliberate choice; write it down next to the digest.

## Cross-host

xxHash being platform-independent only covers the hashing step. The floats being hashed are still not portable across CPUs, BLAS builds
or compilers (see the cross-host section in `SKILL.md`), so a changed digest on another machine is a re-baseline, not proof of a regression.
