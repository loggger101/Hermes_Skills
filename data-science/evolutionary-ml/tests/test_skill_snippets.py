"""Run the code SKILL.md teaches and assert the claims its prose makes about it.

The snippets are pulled out of SKILL.md itself, so editing the doc re-tests the doc.
Two of them shipped broken once: the Swiss example paired nobody after round 1 (its
`paired` set was never reset), and the worker example called a function it could not see,
turned the NameError into a -inf fitness for every agent, and so built in the "silent
evaluation failure" the same file warns about.

Needs numpy; skips cleanly without it. The worker-pool test swaps multiprocessing.Pool for a
ThreadPool, because the defect it guards is scoping, not pickling.
"""

import logging
import math
import random
import re
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")

SKILL_MD = Path(__file__).resolve().parents[1] / "SKILL.md"
POOL_IMPORT = "from multiprocessing import Pool, cpu_count"
THREAD_IMPORT = (
    "from multiprocessing.pool import ThreadPool as Pool\nfrom multiprocessing import cpu_count"
)


def code_block(marker):
    text = SKILL_MD.read_bytes().decode("utf-8").replace("\r\n", "\n")
    hits = [b for b in re.findall(r"```python\n(.*?)```", text, flags=re.S) if marker in b]
    assert len(hits) == 1, f"expected one python block containing {marker!r}, found {len(hits)}"
    return hits[0]


def load_swiss(n):
    ns = {"math": math, "scores": [random.random() for _ in range(n)]}
    exec(code_block("def swiss_round"), ns)  # also runs the demo loop at the bottom
    return ns


def load_pool():
    ns = {"np": np, "log": logging.getLogger("evolutionary-ml-test")}
    src = code_block("def evaluate_population")
    assert POOL_IMPORT in src
    exec(src.replace(POOL_IMPORT, THREAD_IMPORT), ns)
    return ns


@pytest.mark.parametrize("n", [2, 8, 15, 16, 33, 64])
def test_swiss_pairs_everyone_each_round_without_rematches_or_repeat_byes(n):
    random.seed(n)
    ns = load_swiss(n)
    scores, swiss_round = ns["scores"], ns["swiss_round"]
    played, had_bye = set(), set()
    pairs, byes = [], []
    for _ in range(math.ceil(math.log2(n))):
        pairings, bye = swiss_round(scores, played, had_bye)
        seated = [a for p in pairings for a in p] + ([] if bye is None else [bye])
        assert sorted(seated) == list(range(n)), "every agent sits exactly once per round"
        pairs += [frozenset(p) for p in pairings]
        byes += [] if bye is None else [bye]
        for a, b in pairings:  # results move the scores, so the next round re-pairs
            scores[random.choice((a, b))] += 1
    assert len(pairs) == len(set(pairs)), "no rematches"
    assert len(byes) == len(set(byes)), "no agent sits out twice"
    assert (len(byes) > 0) == (n % 2 == 1)


def test_swiss_match_count_matches_the_prose():
    # SKILL.md: at N=200 that is 800 matchups against 19,900 for round-robin
    random.seed(0)
    ns = load_swiss(200)
    played, had_bye = set(), set()
    total = 0
    for _ in range(math.ceil(math.log2(200))):
        pairings, _ = ns["swiss_round"](ns["scores"], played, had_bye)
        total += len(pairings)
    assert total == 800
    assert 200 * 199 // 2 == 19900


def test_pool_returns_each_agents_own_fitness_in_order():
    out = load_pool()["evaluate_population"]([1, 2, 3, 4], lambda a: float(a * 2), n_workers=2)
    assert out == [2.0, 4.0, 6.0, 8.0]


def test_pool_survives_one_failing_agent_and_scores_it_minus_inf():
    def flaky(a):
        if a == 3:
            raise ValueError("planted")
        return float(a)

    out = load_pool()["evaluate_population"]([1, 2, 3, 4], flaky, n_workers=2)
    assert out == [1.0, 2.0, -math.inf, 4.0]


def test_pool_raises_when_every_agent_fails():
    def boom(a):
        raise ValueError("planted")

    with pytest.raises(RuntimeError, match="every evaluation failed"):
        load_pool()["evaluate_population"]([1, 2, 3], boom, n_workers=2)
