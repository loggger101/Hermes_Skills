#!/usr/bin/env python3
"""Top-k-per-group via two-stage MapReduce — simulates the sales_rank case study from
donnemartin/system-design-primer (Amazon's "most popular products by category").

The non-obvious trick being demonstrated: you get a *distributed sort for free* when you
re-key stage 1's output to (group, rank_value) and let MapReduce's shuffle/sort step do
the sorting. Stage 2's reducer is the identity — all work happens in the key ordering.

Pipeline (mirrors SalesRanker.steps() from the primer):
  input log line: timestamp product_id category_id qty total_price seller_id buyer_id
    stage 1 mapper   : keep past-week rows -> emit ((category, product), qty)
    stage 1 reducer  : sum qty per key     -> (category, product): total_qty
    stage 2 mapper   : re-key               -> ((category, total_qty), product)
    stage 2 reducer  : identity             -> sorted by (category, total_qty) ascending

Run:  py topk_mapreduce_sim.py     (self-tests run automatically; prints the final table)
"""

from collections import defaultdict


# --- The primer's sample log data (tab-delimited), verbatim -------------------
SAMPLE_LOG = """\
t1\tproduct1\tcategory1\t2\t20.00\t1\t1
t2\tproduct1\tcategory2\t2\t20.00\t2\t2
t2\tproduct1\tcategory2\t1\t10.00\t2\t3
t3\tproduct2\tcategory1\t3\t7.00\t3\t4
t4\tproduct3\tcategory2\t7\t2.00\t4\t5
t5\tproduct4\tcategory1\t1\t5.00\t5\t6
""".splitlines()

# In the real system timestamps are comparable; here we model "past week" as t1..t5 all in
# window and add one out-of-window row to prove the filter works.
SAMPLE_LOG_WITH_STALE = SAMPLE_LOG + ["t9\totherproduct\tcategory1\t99\t999.00\t6\t7"]


def stage1_mapper(lines):
    """Emit ((category, product), qty) for in-window rows (filter by timestamp)."""
    for line in lines:
        ts, product_id, category_id, qty, _price, _seller, _buyer = line.split("\t")
        if ts.startswith("t9"):            # stand-in for within_past_week(timestamp)
            continue
        yield (category_id, product_id), int(qty)


def stage1_reduce(pairs):
    """Shuffle by key + sum values -> {(category, product): total_qty}."""
    buckets = defaultdict(int)
    for (cat, prod), qty in pairs:
        buckets[(cat, prod)] += qty
    return dict(buckets)


def stage2_mapper(totals):
    """Re-key to ((category, total_qty), product); shuffle/sort then orders by both."""
    for (cat, prod), total in totals.items():
        yield (cat, total), prod


def top_k_per_category(lines, k=3):
    """Full two-stage pipeline -> {category: [(product, qty)]} sorted DESC by qty per cat.

    The framework sorts keys ascending; we reverse within each group so rank 1 = best seller,
    matching the case study's intent (most popular first).
    """
    totals = stage1_reduce(stage1_mapper(lines))
    grouped = defaultdict(list)
    for (cat, _total), prod in sorted(stage2_mapper(totals)):   # 'distributed sort' step
        grouped[cat].append(prod)
    out = {}
    for cat, prods in grouped.items():
        ranked = sorted(((p, totals[(cat, p)]) for p in prods), key=lambda t: -t[1])
        out[cat] = ranked[:k]
    return out


def _self_test() -> None:
    result = top_k_per_category(SAMPLE_LOG_WITH_STALE, k=3)

    # Expected (from the primer's own worked example):
    expected = {
        "category1": [("product2", 3), ("product1", 2), ("product4", 1)],
        "category2": [("product3", 7), ("product1", 3)],   # only two products in cat2
    }
    assert result == expected, f"mismatch:\n got {result}\nwant {expected}"

    # Stale row (t9) must have been filtered: product 'otherproduct' with qty 99 absent.
    flat = [p for prods in result.values() for p, _ in prods]
    assert "otherproduct" not in flat, "past-week filter failed"

    # k-limit respected (category1 has exactly 3 rows despite having only 3 products;
    # a larger group would be truncated — verify truncation explicitly).
    big = [f"t{i}\tp{j}\tcA\t{5 - j}\t1.0\t1\t2" for i in range(6) for j in range(4)]
    limited = top_k_per_category(big, k=2)["cA"]
    assert len(limited) == 2 and limited[0][1] >= limited[-1][1], "k-limit / ordering broken"

    print("top-k per category (desc by qty):")
    for cat in sorted(result):
        for rank, (prod, qty) in enumerate(result[cat], start=1):
            print(f"  {cat}: #{rank} {prod} ({qty})")
    print("topk_mapreduce_sim: all self-tests passed "
          "(stage-1 sum, past-week filter, stage-2 key-sort trick, k-limit)")


if __name__ == "__main__":
    _self_test()
