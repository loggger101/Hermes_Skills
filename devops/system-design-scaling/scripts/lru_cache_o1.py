#!/usr/bin/env python3
"""O(1) LRU cache — implements the design doc from donnemartin/system-design-primer's
query_cache case study (the primer ships it as stubbed notebook code; this is a real,
tested implementation).

Design: hash table {key -> node} for O(1) lookup + doubly linked list where head = most
recently used and tail = eviction candidate. get() moves the hit to front; set() updates+
moves existing keys or appends new ones, evicting the tail at capacity.

Run:  py lru_cache_o1.py     (self-tests run automatically)
"""


class _Node:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """Least-recently-used cache with O(1) get and set."""

    def __init__(self, max_size: int):
        if max_size < 1:
            raise ValueError("max_size must be >= 1")
        self.max_size = max_size
        self.size = 0
        self.lookup = {}          # key -> _Node
        # Sentinels avoid head/tail edge cases in the pointer surgery.
        self.head = _Node()       # dummy; real MRU node follows
        self.tail = _Node()       # dummy; real LRU node precedes it
        self.head.next = self.tail
        self.tail.prev = self.head

    def _unlink(self, node: _Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _push_front(self, node: _Node) -> None:
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        """Return the value for key (marking it most-recently-used), or None on miss."""
        node = self.lookup.get(key)
        if node is None:
            return None
        self._unlink(node)
        self._push_front(node)
        return node.value

    def set(self, key, value) -> None:
        """Insert/update key; evicts the least-recently-used entry when at capacity."""
        node = self.lookup.get(key)
        if node is not None:
            node.value = value
            self._unlink(node)
            self._push_front(node)
            return
        if self.size == self.max_size:
            lru = self.tail.prev          # real LRU node (sentinel-safe)
            self._unlink(lru)
            del self.lookup[lru.key]
            self.size -= 1
        new_node = _Node(key, value)
        self._push_front(new_node)
        self.lookup[key] = new_node
        self.size += 1

    def keys_in_lru_order(self):
        """Tail-most (least recent) first — handy for tests and debugging."""
        out = []
        node = self.tail.prev
        while node is not self.head:
            out.append(node.key)
            node = node.prev
        return out


def _self_test() -> None:
    c = LRUCache(3)

    # Basic set/get.
    c.set("a", 1); c.set("b", 2); c.set("c", 3)
    assert c.get("a") == 1, "get existing"
    assert c.keys_in_lru_order() == ["b", "c", "a"], f"order after get: {c.keys_in_lru_order()}"

    # Eviction of the LRU entry.
    c.set("d", 4)                       # evicts 'b' (least recent now)
    assert c.get("b") is None, "LRU should be evicted"
    assert c.size == 3 and set(c.lookup) == {"a", "c", "d"}

    # Update does not change capacity or recency wrongly.
    c.set("c", 30)                      # 'c' value updated + becomes MRU again; order tail->head: a,d,c
    assert c.get("c") == 30
    c.set("e", 5)                       # evicts 'a' (the LRU entry); remaining {c, d, e}
    # After the two sets above, recency tail->head was [d? ...] — verify explicitly:
    assert "a" not in c.lookup and set(c.lookup) == {"c", "d", "e"}, f"got {set(c.lookup)}"

    # Miss handling.
    assert c.get("nope") is None
    assert c.size == 3, "miss must not change size"

    # Stale-value check: evicted key re-inserted gets fresh value.
    c.set("b", 20)                      # evicts 'd'
    assert c.get("b") == 20 and "d" not in c.lookup

    # Single-element cache edge case.
    s = LRUCache(1)
    s.set("x", 1); s.set("y", 2)
    assert s.get("x") is None and s.get("y") == 2

    print("lru_cache_o1: all self-tests passed "
          "(get/set O(1), eviction order, update-in-place, miss handling, size-1 edge)")


if __name__ == "__main__":
    _self_test()
