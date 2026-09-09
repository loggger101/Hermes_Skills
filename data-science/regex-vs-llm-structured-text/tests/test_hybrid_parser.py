"""Tests for the hybrid regex/LLM structured-text parser.

Run from anywhere: ``python -m pytest`` (CI's discovery runner picks this up)
or directly with stdlib unittest if pytest is unavailable::

    python tests/test_hybrid_parser.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from hybrid_parser import (  # noqa: E402
    ParsedItem,
    identify_low_confidence,
    parse_structured_text,
    process_document,
    score_confidence,
    validate_with_llm,
)

DOC = """\
1. What is the capital of France?
A. London
B. Paris
C. Berlin
D. Madrid
Answer: B

2. Which planet has rings?
A. Earth
B. Mars
C. Jupiter
D. Saturn
Answer: D

3. Tiny text
A. One
B. Two
"""


class TestParseStructuredText(unittest.TestCase):
    def test_parses_well_formed_items(self):
        items = parse_structured_text(DOC)
        self.assertEqual(len(items), 3)
        first = items[0]
        self.assertEqual(first.id, "1")
        self.assertIn("capital of France", first.text)
        self.assertEqual(first.choices, ("London", "Paris", "Berlin", "Madrid"))
        self.assertEqual(first.answer, "B")

    def test_second_item(self):
        items = parse_structured_text(DOC)
        second = items[1]
        self.assertEqual(second.id, "2")
        self.assertEqual(second.choices, ("Earth", "Mars", "Jupiter", "Saturn"))
        self.assertEqual(second.answer, "D")

    def test_malformed_item_is_still_returned(self):
        # Item 3 has short text and only two choices: it must parse (and be
        # flagged later), not silently vanish.
        items = parse_structured_text(DOC)
        third = items[2]
        self.assertEqual(third.id, "3")
        self.assertEqual(len(third.choices), 2)
        self.assertIsNone(third.answer)

    def test_empty_input(self):
        self.assertEqual(parse_structured_text(""), [])


class TestConfidence(unittest.TestCase):
    def test_healthy_item_scores_one(self):
        items = parse_structured_text(DOC)
        flag = score_confidence(items[0])
        self.assertEqual(flag.score, 1.0)
        self.assertEqual(flag.reasons, ())

    def test_malformed_item_flagged_with_reasons(self):
        items = parse_structured_text(DOC)
        flags = {f.item_id: f for f in identify_low_confidence(items)}
        self.assertIn("3", flags)
        self.assertNotIn("1", flags)
        reasons = set(flags["3"].reasons)
        self.assertEqual(reasons, {"few_choices", "missing_answer", "short_text"})

    def test_threshold_respected(self):
        items = parse_structured_text(DOC)
        strict = identify_low_confidence(items, threshold=1.01)  # flag everything
        self.assertEqual(len(strict), 3)


class TestImmutability(unittest.TestCase):
    def test_parsed_item_is_frozen(self):
        item = ParsedItem(id="9", text="x")
        with self.assertRaises(Exception):
            item.answer = "A"  # type: ignore[misc]

    def test_validate_returns_new_instance(self):
        item = ParsedItem(id="9", text="q?", choices=("a", "b", "c"), answer=None)

        def fake_client(prompt):
            return "B"

        fixed = validate_with_llm(item, "raw text", fake_client)
        self.assertIsNot(fixed, item)
        self.assertEqual(fixed.answer, "B")
        self.assertIsNone(item.answer)  # original untouched


class TestValidateWithLlm(unittest.TestCase):
    def test_correct_reply_is_noop(self):
        item = ParsedItem(id="1", text="q?", choices=("a", "b"), answer="A")

        fixed = validate_with_llm(item, "raw", lambda p: "CORRECT")
        self.assertEqual(fixed.answer, "A")

    def test_exception_in_client_is_swallowed(self):
        item = ParsedItem(id="1", text="q?", choices=("a", "b"), answer=None)

        def boom(prompt):
            raise RuntimeError("client down")

        fixed = validate_with_llm(item, "raw", boom)
        self.assertEqual(fixed.answer, None)


class TestProcessDocument(unittest.TestCase):
    def test_no_validator_returns_regex_result(self):
        out = process_document(DOC)
        self.assertEqual(len(out), 3)
        self.assertIsNone(out[2].answer)

    def test_validator_called_only_for_flagged_items(self):
        calls = []

        def validator(item, content):
            calls.append(item.id)
            return ParsedItem(
                id=item.id, text=item.text, choices=item.choices, answer="C"
            )

        out = process_document(DOC, llm_validator=validator)
        self.assertEqual(calls, ["3"])  # only the flagged item
        self.assertEqual(out[2].answer, "C")
        self.assertEqual(out[0].answer, "B")  # unflagged items untouched

    def test_validator_must_return_parsed_item(self):
        def bad(item, content):
            return "not an item"  # type: ignore[return-value]

        out = process_document(DOC, llm_validator=bad)
        self.assertEqual(out[2].answer, None)  # original kept


if __name__ == "__main__":
    unittest.main()
