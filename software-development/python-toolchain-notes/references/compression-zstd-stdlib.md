---
description: "Python 3.14 stdlib compression.zstd (zstd 1.5.7) measured against zlib/bz2/lzma on markdown, CSV and float data; dictionaries for small records, level vs options TypeError, tar.zst, thread count"
source_repo: facebook/zstd (BSD-3-Clause / GPL-2.0 dual; Cyan4973/zstd is the original repo name) via CPython's compression.zstd (PEP 784)
tested_version: "Python 3.14.6 on Windows 11 (14 cores), zstd library 1.5.7, run 2026-10-05; two scripts timing single runs on a laptop, so treat times as relative. Data: this repo's markdown index files (0.14 MB), a 2.9 MB CSV, 4 MB of float64, 2 MB random bytes"
verified_date: "2026-10-05"
---

# `compression.zstd` (Python 3.14) vs zlib, bz2, lzma

Python 3.14 added `compression.zstd` (a standard-library Zstandard binding; `import compression.zstd as zstd`). It reports
**zstd 1.5.7** and level bounds **(-131072, 22)**. Names: `compress`, `decompress`, `ZstdCompressor`, `ZstdDecompressor`,
`ZstdFile`, `open`, `ZstdDict`, `train_dict`, `finalize_dict`, `get_frame_info`, `get_frame_size`, `CompressionParameter`,
`DecompressionParameter`, `Strategy`, `ZstdError`. No third-party `zstandard` package is needed on 3.14; on older Pythons it is.

## Ratio and speed (compressed/original, compress time)

| Data | zlib 6 | zlib 9 | bz2 9 | lzma 6 | zstd 3 | zstd 10 | zstd 19 | zstd -5 |
|---|---|---|---|---|---|---|---|---|
| Markdown, 0.14 MB | 0.328 / 2 ms | 0.326 / 3 | 0.279 / 9 | 0.282 / 27 | 0.329 / 2 | 0.303 / 4 | 0.292 / 34 | 0.507 / 2 |
| CSV records, 2.9 MB | 0.292 / 31 ms | 0.279 / 73 | 0.210 / 160 | 0.236 / 1098 | 0.311 / 11 | 0.267 / 80 | 0.253 / 1136 | 0.571 / 8 |
| Random float64, 4 MB | 0.959 / 105 | 0.964 / 117 | 0.977 / 365 | 0.945 / 994 | 0.960 / 12 | 0.958 / 18 | 0.959 / 577 | 1.000 / 2 |
| Smooth float64 series, 4 MB | 0.870 / 88 | 0.743 / 148 | 0.924 / 257 | 0.647 / 865 | 0.883 / 6 | 0.890 / 15 | 0.653 / 666 | 1.000 / 2 |
| Random bytes, 2 MB | 1.000 | 1.000 | 1.005 | 1.000 | 1.000 / 1 ms | 1.000 | 1.000 | 1.000 |

Reading it:

- **Level 3 (the default) is a speed tool, not a ratio tool**: on the 2.9 MB CSV it was about 3x faster than zlib 6 (11 ms vs 31 ms)
  at a slightly worse ratio (0.311 vs 0.292); level 10 beat zlib 9 on both ratio (0.267 vs 0.279) and, roughly, time (80 vs 73 ms).
- **Level 19 is for write-once data**: 19.6 MB of CSV took **14.4 s** for 0.241x (level 9: 0.427 s for 0.266x; level 3: 75 ms for 0.309x).
  Decompression stayed 25-30 ms at every level.
- Random-looking floats and random bytes do not compress (0.96 to 1.0); smooth numeric series only gain with strong settings
  (lzma and zstd 19 about 0.65). For float columns use a transform first (delta or byte-shuffle), as Parquet/Blosc do.
- Negative levels (`-5`) trade ratio for speed: 0.5 to 0.57 on text, 1.0 on floats.
- On a tiny 0.14 MB input, 20 decompressions took 11 ms for zstd vs 5 ms for zlib: zstd's advantage is on larger data and levels.

## Small records need a dictionary

5 000 small JSON event records (about 80 bytes each; 1 000 held out for the test): compressing each alone with zstd 3 made them
**bigger** (86 066 B vs 79 460 B raw, 1.08x). A **4 KB dictionary trained on 4 000 other records** (`zstd.train_dict(samples, 4096)`)
brought the same 1 000 records to 34 529 B (**0.43x**). Decompressing without the dictionary raises
`ZstdError: Unable to decompress Zstandard data: Dictionary mismatch`, so store the dictionary (or its `dict_id`) with the data.

## API facts

| Behaviour | Result |
|---|---|
| `compress(data, level=3, options={...})` | **`TypeError: Only one of level or options should be used.`** Put the level inside options: `options={CompressionParameter.compression_level: 9, CompressionParameter.nb_workers: 4}` |
| `nb_workers` 0 / 2 / 4 / 8 on 19.6 MB at level 9 | 421 / 399 / 379 / 388 ms: a small effect on a one-shot call here; same ratio (0.266x) |
| `level=23` | `ValueError: illegal compression level 23; the valid range is [-131072, 22]` |
| Frame header of a one-shot `compress()` | `get_frame_info(...).decompressed_size` = the real size (144 141); a streamed `ZstdFile` frame reports `None` |
| Corrupt tail / garbage input | `ZstdError: ... Data corruption detected` / `... Unknown frame descriptor` |
| Archives | `tarfile.open(p, "w:zst")` and `"r:*"` round trip; `shutil.get_archive_formats()` now lists **`zstdtar`** |
| Parquet | zstd is the common codec there (see `python-data-science/references/big-data-patterns.md`) |

## Where not to use it

A COG that must render in a browser should not use zstd (geotiff.js and OpenLayers cannot decode it; see
`space-data-pipelines/references/lunar-gis-patterns-aegis.md`). Compression is not encryption or integrity: add a checksum or
signature separately (`CompressionParameter.checksum_flag` adds a frame checksum; not exercised).

Not run: `ZstdCompressor` streaming flush modes, `finalize_dict`, long-distance matching, multi-GB inputs, memory use, or Python < 3.14.
