# TheAlgorithms/Python: what changed since the 2026-09-13 snapshot, and which new modules hold up (run live)

Source: [TheAlgorithms/Python](https://github.com/TheAlgorithms/Python) (MIT). The catalog skill was mined at commit `23c4208`
(2026-09-13). This review compared that commit with `master` at **`35ccb2c`** (2026-10-05 06:12 -1000) using
`gh api repos/TheAlgorithms/Python/compare/23c4208...master`, then shallow-cloned HEAD and ran 48 oracle checks and the
doctests of 13 of the new modules (Python 3.14.6, Windows). Complements `catalog-map.md` (the 50-category map) and
`keon-algorithms-notes.md` (the same oracle method on another repo).

## Size of the change

**288 commits** in 3 weeks; the compare view lists 300 changed files (GitHub's cap, so there are more) of which **131 are new
files** in the first 300. Tooling touched: `.github/workflows` (`build.yml`, `ty.yml`, `sphinx.yml`, `hacktoberfest_prep.yml`),
`.pre-commit-config.yaml`, `.python-version`, `CONTRIBUTING.md`, `DIRECTORY.md`. `computer_vision/cnn_classification.py` was removed.
The skill's own harness (`scripts/algorithms_verify.py`) still passes, **18 of 18 checks**: the claims it records did not rot.

New modules by area (names from the compare):

- **ciphers**: `base58.py`, `columnar_transposition.py`, `des_ecb.py`, `rc4.py`, `skytale_cipher.py`, `xtea.py`; **blockchain** (new
  folder content): `merkle_tree.py`, `proof_of_stake.py`, `proof_of_work.py`, `simple_blockchain.py`, `simple_proof_of_work.py`.
- **conversions**: `base64_to_binary`, `binary_to_base64`, `binary_to_excess3`, `binary_to_gray(_code)`, `endianness`, `hex_to_rgb`,
  negative-base conversions. **hashes**: `crc32.py`, `jenkins_one_at_a_time.py`.
- **maths**: `next_prime_number`, `ncr_combinations`, `shoelace_area`, `is_ipv6_address_valid`, `bearing`, `padovan_sequence`,
  `binomial_expansion`, special numbers (`abundant`, `deficient`, `evil`, `jacobsthal`, `spy`, `trimorphic`), `numerical_analysis/gauss_seidel_method`, `nth_root`.
- **data structures**: dynamic array, gas station, merge intervals, set-matrix-zeroes, persistent segment tree, monotonic queue,
  min/max-tracking stack; **graphs**: Edmonds blossom, centrality, peripherality; **machine learning**: DBSCAN, Gaussian mixture, MAB,
  mean shift, ridge regression, RMSprop, Q-learning, naive Bayes text, mini-batch gradient descent; **financial**: value at risk,
  expected shortfall, Macaulay duration, annuity future values; **physics**, **electronics**, **quantum/shor_algorithm.py**, project Euler 60/111/124/137/138/142.
- 128 doctest examples across the 13 modules below ran with **0 failures**.

## Oracle results on the new cryptography, hashing and conversion code

| Module | Check | Result |
|---|---|---|
| `ciphers/rc4.py` | RFC test vector (key `Key`, `Plaintext` -> `bbf316e8d940af0ad3`), 100 random key/data pairs against a reference RC4, decrypt roundtrip | **all pass** |
| `hashes/crc32.py` | 200 random byte strings vs `zlib.crc32`; empty input | **identical** (empty = 0) |
| `hashes/jenkins_one_at_a_time.py` | published `a` -> `0xca2e9442`, pangram -> `0x519e91f5`, 100 random strings vs a reference (non-ASCII included) | **all pass** |
| `maths/next_prime_number.py` | -3..199 plus three large values vs trial division; `is_prime` 0..500 | **all pass** |
| `maths/ncr_combinations.py` | all (n, k) up to 14 vs `math.comb` | pass, but returns a **float** (`combinations(5, 0)` -> `1.0`); `combinations(-1, 2)` -> `1.0`; `5.5` allowed |
| `blockchain/merkle_tree.py` | 3-leaf root vs a hex-string pairing reference (last node duplicated when odd) | match; empty list raises `ValueError`; one leaf returns that leaf's sha256 |
| sequences | padovan 1,1,1,2,2,3,4,5,7,9; jacobsthal 0,1,1,3,5,11,21,43; `is_evil_number` vs popcount parity 0..199 | pass |
| `maths/bearing.py` | London -> New York | 288.3300 deg, expected 288.33; **takes `(lat, lon)` tuples**, swapping the order gives 183.07 |
| `maths/binomial_expansion.py` | (a+b)**n over 48 combinations | pass |
| `ciphers/columnar_transposition.py`, `skytale_cipher.py` | 50 random roundtrips each | pass |
| `conversions/binary_to_gray.py` | `n ^ (n >> 1)` for 0..63 | pass |

## Where the name or default is not what it sounds like

- **`ciphers/xtea.py` is not standard XTEA with its default arguments.** `num_rounds` counts full loop cycles, each doing two
  Feistel half-steps, so the default 64 is **64 cycles (128 rounds)**; the standard cipher is 32 cycles (64 rounds). Results:
  `num_rounds=32` on key `00..0f`, plaintext `4142434445464748` -> `497df3d072612cb5`, the published value, and zero key and zero
  block -> `dee9d4d8f7131ed9`; the default gives `fc924d124ad0ed50` (which is the module's own doctest, so the docstring "recommended 64
  rounds" misleads). Pass `num_rounds=32` to interoperate. Byte order is big-endian (`!II`); encrypt/decrypt roundtrip is fine.
- **`ciphers/base58.py` implements Base64**: its functions are `base64_encode`/`base64_decode` and `b"Hello World!"` encodes to
  `b'SGVsbG8gV29ybGQh'` (equal to `base64.b64encode`), not Bitcoin Base58 (`2NEpo7TZRRrLZSi2U`).
- **`conversions/binary_to_base64.py` and `base64_to_binary.py` convert a number between radixes**, not bytes (RFC 4648): the
  binary string is zero-padded on the left to a 6-bit boundary and **a length that is already a multiple of 6 gets an extra leading `A`**
  (`bin_to_base64('000001')` -> `AB`, `'111111'` -> `A/`). `=` padding is rejected (`Invalid base64 string. Invalid char = at pos 7`),
  and 74 of 100 stdlib-encoded strings failed for that reason. Eight numeric values (1, 2, 63, 64, 65, 4095, 4096, 123456) round-tripped
  with the right integer value. Never use them to encode data.
- `geometry/shoelace.py` `area_of_polygon` returns a **signed** area: a clockwise rectangle gave `-12.0` (the docstring requires
  counter-clockwise vertices); `maths/shoelace_area.py` returned `12.0` for both orders.
- `maths/is_ipv6_address_valid.py` implements a documented **subset** of RFC 4291: it rejects `::ffff:192.168.1.1` (embedded IPv4) and
  `fe80::1%eth0` (zone id), both accepted by `ipaddress.IPv6Address`; 13 other probes (compressed, double `::`, over-long group,
  non-hex, nine groups, trailing colon, leading space, prefix length) agreed with the stdlib.
- `hex_to_rgb('#12345')` raises `ValueError: Invalid hex color code`; `#fff` is expanded to `rgb(255, 255, 255)`; a missing `#` is accepted.

## Use

Prefer stdlib for crc32 (`zlib`), base64 (`base64`), `math.comb`, `ipaddress`; use the repo's rc4/xtea/DES only to read an algorithm
(and pass `num_rounds=32` for XTEA). The catalog's rule still stands: copy a function only together with its oracle test.
Not run: the machine-learning, quantum, graph, physics and project Euler additions, `des_ecb.py` (not run at all), and any file beyond the first 300 of the diff.
