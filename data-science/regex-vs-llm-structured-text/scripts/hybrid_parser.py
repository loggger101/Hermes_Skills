"""Hybrid structured-text parser: regex first, LLM only for flagged edge cases.

Reference implementation for the ``regex-vs-llm-structured-text`` skill.
Stdlib-only; the LLM step is an injected callable so any client works and no
vendor API leaks into the pipeline.

Pipeline::

    source text -> regex parser (95-98% of items)
                -> confidence scorer (flags low-confidence extractions)
                -> LLM validator   (flagged items only, if a validator is given)

Design rules:
  * ``ParsedItem`` / ``ConfidenceFlag`` are frozen dataclasses — cleaning and
    validation steps return NEW instances; they never mutate inputs.
  * The regex pass always runs first, even when imperfect: it gives a
    measurable baseline (success rate, flag count) to track over time.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Callable, List, Optional, Sequence, Tuple

__all__ = [
    "ParsedItem",
    "ConfidenceFlag",
    "parse_structured_text",
    "score_confidence",
    "identify_low_confidence",
    "validate_with_llm",
    "process_document",
]


@dataclass(frozen=True)
class ParsedItem:
    """One extracted structured item (e.g. a quiz question)."""

    id: str
    text: str
    choices: Tuple[str, ...] = ()
    answer: Optional[str] = None
    confidence: float = 1.0


@dataclass(frozen=True)
class ConfidenceFlag:
    """Confidence assessment for one parsed item."""

    item_id: str
    score: float
    reasons: Tuple[str, ...] = ()


# Matches blocks like::
#
#     42. What is the capital of France?
#     A. London
#     B. Paris
#     C. Berlin
#     D. Madrid
#     Answer: B
#
# The answer line and any choices are optional so malformed items still parse
# (and get flagged by :func:`score_confidence` instead of vanishing).
_ITEM_RE = re.compile(
    r"(?P<id>\d+)\.\s*(?P<text>.+?)\n"
    r"(?P<choices>(?:[A-Da-d]\..+?\n)*)"
    r"(?:Answer:\s*(?P<answer>[A-Da-d])\b)?",
    re.MULTILINE,
)

_CHOICE_RE = re.compile(r"[A-Da-d]\.\s*(.+)")


def parse_structured_text(content: str) -> List[ParsedItem]:
    """Regex pass over ``content``; returns one :class:`ParsedItem` per match.

    Malformed blocks are still returned (with whatever fields matched) so the
    confidence scorer can flag them — silent drops hide pipeline rot.
    """
    items: List[ParsedItem] = []
    for m in _ITEM_RE.finditer(content):
        choices = tuple(c.strip() for c in _CHOICE_RE.findall(m.group("choices") or ""))
        answer = (m.group("answer") or "").upper() or None
        text = " ".join((m.group("text") or "").split())  # collapse whitespace/newlines
        items.append(
            ParsedItem(id=m.group("id"), text=text, choices=choices, answer=answer)
        )
    return items


def score_confidence(item: ParsedItem) -> ConfidenceFlag:
    """Score one item's extraction confidence; lower is worse.

    Heuristics are deliberately simple and visible — tune per corpus, but keep
    the reasons explicit so downstream logs explain every flag.
    """
    reasons: List[str] = []
    score = 1.0

    if len(item.choices) < 3:
        reasons.append("few_choices")
        score -= 0.3
    if not item.answer:
        reasons.append("missing_answer")
        score -= 0.5
    if len(item.text) < 10:
        reasons.append("short_text")
        score -= 0.2

    return ConfidenceFlag(
        item_id=item.id, score=max(0.0, round(score, 4)), reasons=tuple(reasons)
    )


def identify_low_confidence(
    items: Sequence[ParsedItem], threshold: float = 0.95
) -> List[ConfidenceFlag]:
    """Return the flags for every item scoring below ``threshold``."""
    return [f for f in (score_confidence(i) for i in items) if f.score < threshold]


def validate_with_llm(
    item: ParsedItem, original_text: str, client_call: Callable[[str], Optional[str]]
) -> ParsedItem:
    """Re-extract one flagged item via an injected LLM call.

    ``client_call`` receives a prompt and returns the corrected answer letter
    (or None if the model could not improve it). Returns a NEW item; on no-op
    or failure the original is returned unchanged.
    """
    prompt = (
        "Extract the question, choices, and correct answer from this text.\n"
        f"Text:\n{original_text}\n\n"
        f"Current extraction: id={item.id} text={item.text!r} "
        f"choices={list(item.choices)} answer={item.answer}\n"
        "Reply with the corrected answer letter (A-D) or 'CORRECT' if accurate."
    )
    try:
        reply = (client_call(prompt) or "").strip().upper()
    except Exception:  # noqa: BLE001 - validator must never kill the pipeline
        return item
    if len(reply) == 1 and reply in "ABCD":
        return replace(item, answer=reply, confidence=1.0)
    return item


def process_document(
    content: str,
    *,
    llm_validator: Optional[Callable[[ParsedItem, str], ParsedItem]] = None,
    confidence_threshold: float = 0.95,
) -> List[ParsedItem]:
    """Full pipeline: regex -> confidence check -> LLM for flagged items only.

    ``llm_validator`` (if given) is called as ``validator(item, content)`` and
    must return a replacement item; when omitted the document parses with the
    regex pass alone. High-confidence items are never touched by the validator.
    """
    items = parse_structured_text(content)
    flagged_ids = {f.item_id for f in identify_low_confidence(items, confidence_threshold)}

    if not flagged_ids or llm_validator is None:
        return items

    out: List[ParsedItem] = []
    for item in items:
        if item.id in flagged_ids:
            replacement = llm_validator(item, content)
            out.append(replacement if isinstance(replacement, ParsedItem) else item)
        else:
            out.append(item)
    return out
