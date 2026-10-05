---
description: "gensim 4.4.0 (topic models, Word2Vec) install reality (no cp314 wheel) and a verified small run in a 3.11 venv: reproducibility, OOV errors, LDA"
source_repo: piskvorky/gensim (LGPL-2.1)
tested_version: gensim 4.4.0 with numpy 2.4.6 / scipy 1.17.1 in a uv Python 3.11.16 venv on Windows; PyPI metadata for wheel availability; Python 3.14 install dry-run only
verified_date: "2026-10-05"
---

# gensim: topic modelling and word vectors

Unsupervised text modelling: `Word2Vec`/`FastText`/`Doc2Vec` embeddings, `LdaModel`/`LsiModel` topic models, TF-IDF, similarity indexes, streaming corpora. License **LGPL-2.1-only**.
Latest 4.4.0 (2025-10-18); depends on `numpy>=1.18.5`, `scipy>=1.7.0`, `smart_open`.

## Install reality

PyPI wheels exist for CPython 3.9-3.13 only (cp39, cp310, cp311, cp312, cp313). On Python 3.14.6, `pip install gensim` downloads the 23.3 MB **sdist** and would have to compile the Cython extensions
(needs a C compiler; unattended it will fail on a machine without MSVC), and without them gensim's training loops would be the slow pure-Python path. Use a 3.11-3.13 venv:
`uv venv --python 3.11 nlpenv && uv pip install --python nlpenv/Scripts/python.exe gensim` installed cleanly in this check. After installing, read `gensim.models.word2vec.FAST_VERSION`: `0` here (optimised routines present); `-1` would mean the slow fallback.

## Verified run (synthetic corpus: 400 sentences of 8 words, two clusters "animals" and "vehicles")

```python
from gensim.models import Word2Vec, LdaModel
from gensim.corpora import Dictionary
m = Word2Vec(sentences, vector_size=16, window=3, min_count=1, workers=1, seed=7, epochs=20)
```

| Check | Result |
|---|---|
| Two `Word2Vec` trainings with `workers=1`, same `seed` | identical vector matrices (same SHA-256 prefix) |
| Two trainings with `workers=4`, same `seed` | also identical on this tiny corpus; gensim's docs say multi-threaded training is not guaranteed reproducible, so for a bit-identity claim use `workers=1` (and set `PYTHONHASHSEED`) and re-verify on your real corpus |
| `wv.similarity("cat","dog")` vs `("cat","car")` | 0.992 vs 0.259: within-cluster words are near, cross-cluster words far |
| `wv.most_similar("cat", topn=3)` | `lion 1.0, mouse 1.0, dog 0.99`; words come back as `numpy.str_` (a `str` subclass; convert with `str()` if a library rejects it) |
| `most_similar("zebra")` out of vocabulary | `KeyError: "Key 'zebra' not present in vocabulary"`; check `word in m.wv.key_to_index` first |
| `LdaModel(corpus, num_topics=2, random_state=0, passes=5)` twice | identical topic matrices; topic 0 = boat/plane/bus/car, topic 1 = mouse/tiger/dog/cat |

## Practical notes

- Pass `seed`/`random_state` and fix `workers=1` for reproducible experiments; record the gensim, numpy and scipy versions alongside results (see `bit-identity-float-pipelines`).
- Tiny corpora give degenerate similarities (several words at 1.0): meaningful embeddings need real data, `min_count > 1`, and many epochs.
- For modern semantic search, transformer sentence embeddings usually beat Word2Vec/LDA; gensim remains useful for fast, CPU-only topic models, streaming TF-IDF, and similarity indexes over large corpora.
- LGPL-2.1 allows use from proprietary code if the library stays replaceable (dynamic linking/import); read the licence before vendoring it.
