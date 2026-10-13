"""The four worked-example scripts: their built-in self-tests run, and are not vacuous.

Each script ends in `_self_test()` under `__main__`, but no runner executed them until
round-257. Here every script runs exactly as SKILL.md tells a reader to run it, and each
self-test is shown to fail when the function it guards is broken (a self-test that cannot
fail proves nothing).
"""

import importlib.util
import random
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
NAMES = ["availability_math", "lru_cache_o1", "shortlink_base62", "topk_mapreduce_sim"]


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("name", NAMES)
def test_script_runs_clean(name):
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / f"{name}.py")], capture_output=True, text=True, timeout=60
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip(), "the worked example printed nothing"


# ------------------------------------------------------- each self-test can fail
def test_availability_self_test_catches_wrong_sequence_math(monkeypatch):
    mod = load("availability_math")
    monkeypatch.setattr(mod, "seq_availability", lambda *a: min(a))  # the classic mistake
    with pytest.raises(AssertionError):
        mod._self_test()


def test_lru_self_test_catches_wrong_eviction(monkeypatch):
    mod = load("lru_cache_o1")
    # Evict the MOST recent entry instead of the least recent one.
    original_set = mod.LRUCache.set

    def evict_mru(self, key, value):
        if key not in self.lookup and self.size == self.max_size:
            mru = self.head.next
            self._unlink(mru)
            del self.lookup[mru.key]
            self.size -= 1
        original_set(self, key, value)

    monkeypatch.setattr(mod.LRUCache, "set", evict_mru)
    with pytest.raises(AssertionError):
        mod._self_test()


def test_shortlink_self_test_catches_unsafe_alphabet(monkeypatch):
    mod = load("shortlink_base62")
    monkeypatch.setattr(mod, "ALPHABET", mod.ALPHABET[:-2] + "+/")
    with pytest.raises(AssertionError):
        mod._self_test()


def test_topk_self_test_catches_missing_time_filter(monkeypatch):
    mod = load("topk_mapreduce_sim")

    def no_filter(lines):
        for line in lines:
            _ts, product_id, category_id, qty, *_ = line.split("\t")
            yield (category_id, product_id), int(qty)

    monkeypatch.setattr(mod, "stage1_mapper", no_filter)
    with pytest.raises(AssertionError):
        mod._self_test()


# ------------------------------------------------------- properties beyond the examples
def test_lru_matches_a_reference_model():
    mod = load("lru_cache_o1")
    rng = random.Random(257)
    for cap in (1, 2, 5):
        cache, model = mod.LRUCache(cap), []  # model: list of (key, value), MRU last
        for _ in range(500):
            key = rng.randrange(8)
            if rng.random() < 0.5:
                hit = next((v for k, v in model if k == key), None)
                assert cache.get(key) == hit
                if hit is not None:
                    model = [(k, v) for k, v in model if k != key] + [(key, hit)]
            else:
                value = rng.randrange(100)
                model = [(k, v) for k, v in model if k != key] + [(key, value)]
                model = model[-cap:]
                cache.set(key, value)
            assert cache.keys_in_lru_order() == [k for k, _ in model]
            assert cache.size == len(model) == len(cache.lookup)


def test_lru_rejects_zero_capacity():
    with pytest.raises(ValueError):
        load("lru_cache_o1").LRUCache(0)


def test_base62_roundtrips():
    mod = load("shortlink_base62")
    for n in [0, 1, 61, 62, 3843, 3844, 2**64, 2**128 - 1]:
        s = mod.base_encode(n)
        assert sum(mod.ALPHABET.index(c) * 62**i for i, c in enumerate(reversed(s))) == n


def test_availability_composition_bounds():
    mod = load("availability_math")
    for a, b in [(99.0, 99.9), (90.0, 50.0), (100.0, 99.0)]:
        assert mod.seq_availability(a, b) <= min(a, b) + 1e-9
        assert mod.parallel_availability(a, b) >= max(a, b) - 1e-9
