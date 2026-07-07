"""The one NEW tool the L50 mini-project needs: ``find_matching_record``.

L50 is a capstone *assembly* lesson — the loop, the tracing, and the eval types are
all imported from :mod:`fluffy_potato_curriculum.common`. The only genuinely new code
is a single small domain tool, authored here with the L07/L08 checklist: a plain
typed function, a docstring that reads as its contract, and error handling that turns
a bad input into a *value*, never a crash.

The domain is **receipt reconciliation**. A receipt arrives in one of several source
formats (a cafe POS JSON blob, a rideshare API object with entirely different field
names, a hotel folio as raw printed text) and must be matched against a canonical
**records ledger**. The hard part — and the reason this is *warranted* as a tool
rather than left to the model's eyeball — is **normalizing across those formats** to a
common ``(vendor, total)`` shape before looking the record up.

This module is the *tested* sibling the L50 walkthrough writes live: the notebook
re-derives ``find_matching_record`` inline (the Segment 2 live-coding beat), but the
proctor knows it works because this copy is covered by
``tests/lessons/L50/test_receipt_tools.py``. Keep the two in sync.

``check_reimbursement`` is the deliberately-scoped-out **stretch** tool (Segment 6 /
the student bonus): it is real and tested, but it is *not* wired into the core
one-new-tool agent — it is the "first thing you'd add next" hand-off, not part of the
vertical slice.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

_DATA_DIR = Path(__file__).parent / "data"

# How close two amounts must be to count as the same money (float cents).
_AMOUNT_TOLERANCE = 0.01

# The source-format aliases: the same field wears a different name per vendor. This
# alias table IS the cross-format normalization the tool exists to do — a rideshare
# receipt says "company"/"amount_charged" where a cafe receipt says "merchant"/"total".
_VENDOR_KEYS = ("merchant", "vendor", "company", "store", "name")
_AMOUNT_KEYS = ("total", "amount", "amount_due", "amount_charged", "grand_total")
_DATE_KEYS = ("date", "trip_date", "txn_date", "charged_on", "checkout")


def _load(filename: str) -> list[dict[str, Any]]:
    """Read one JSON bundle file from the co-located ``data/`` dir into a list of dicts."""
    text = (_DATA_DIR / filename).read_text(encoding="utf-8")
    data: list[dict[str, Any]] = json.loads(text)
    return data


RECORDS_LEDGER: list[dict[str, Any]] = _load("records_ledger.json")
"""The canonical expense records — the source of truth ``find_matching_record`` matches against."""

RECEIPTS: list[dict[str, Any]] = _load("receipts.json")
"""The varied-format receipts (each with an ``id``, a ``source`` tag, and a ``raw`` payload)."""

BANK_TRANSACTIONS: list[dict[str, Any]] = _load("bank_transactions.json")
"""The bank side of the ledger — used only by the stretch ``check_reimbursement`` tool."""


@dataclass(frozen=True)
class NormalizedReceipt:
    """A receipt reduced to the common shape every format is coerced into.

    ``date`` is optional because not every source format carries one; ``vendor`` and
    ``total`` are the two fields a match actually keys on, so normalization *fails*
    (returns ``None``, below) when either can't be recovered.
    """

    vendor: str
    total: float
    date: str | None = None


def _vendor_key(name: str) -> str:
    """Fold a vendor name to a comparable key: lowercase, whitespace collapsed."""
    return " ".join(name.lower().split())


def _coerce_amount(value: Any) -> float | None:
    """Parse an amount from an int/float/str, or return ``None`` if it isn't a number.

    This is where the malformed receipt (``"amt": "??"``) is turned into a *value*
    (``None``) instead of an exception — the graceful-failure contract in one helper.
    """
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip().lstrip("$"))
        except ValueError:
            return None
    return None


def _first_present(raw: Mapping[str, Any], keys: tuple[str, ...]) -> Any | None:
    """Return the value of the first key in ``keys`` that is present in ``raw``."""
    for key in keys:
        if key in raw:
            return raw[key]
    return None


def _normalize_mapping(raw: Mapping[str, Any]) -> NormalizedReceipt | None:
    """Normalize a dict-shaped receipt (cafe POS, rideshare API) via the alias table."""
    vendor_value = _first_present(raw, _VENDOR_KEYS)
    amount_value = _first_present(raw, _AMOUNT_KEYS)
    if not isinstance(vendor_value, str) or not vendor_value.strip():
        return None
    total = _coerce_amount(amount_value)
    if total is None:
        return None
    date_value = _first_present(raw, _DATE_KEYS)
    date = date_value if isinstance(date_value, str) else None
    return NormalizedReceipt(vendor=vendor_value, total=total, date=date)


# "Amount due: 268.40" / "Total   $41.20" — a label, then the number we want.
_TEXT_AMOUNT_RE = re.compile(
    r"(?:amount due|total|amount|balance)\s*[:$]*\s*\$?\s*([0-9]+(?:\.[0-9]{1,2})?)",
    re.IGNORECASE,
)
_TEXT_CHECKOUT_RE = re.compile(r"check-?out\s*[:]?\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", re.IGNORECASE)


def _normalize_text(raw: str) -> NormalizedReceipt | None:
    """Normalize a raw-text receipt (a hotel folio): vendor = first line, amount by label."""
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    if not lines:
        return None
    vendor = lines[0]
    amount_match = _TEXT_AMOUNT_RE.search(raw)
    if amount_match is None:
        return None
    total = _coerce_amount(amount_match.group(1))
    if total is None:
        return None
    checkout_match = _TEXT_CHECKOUT_RE.search(raw)
    date = checkout_match.group(1) if checkout_match is not None else None
    return NormalizedReceipt(vendor=vendor, total=total, date=date)


def normalize_receipt(receipt: str) -> NormalizedReceipt | None:
    """Coerce a receipt in *any* supported source format to a :class:`NormalizedReceipt`.

    Tries JSON first (the cafe/rideshare/scan formats are JSON objects); if that fails
    the receipt is treated as raw text (the hotel folio). Returns ``None`` — never
    raises — when neither path can recover a vendor *and* an amount.
    """
    try:
        parsed: Any = json.loads(receipt)
    except json.JSONDecodeError:
        return _normalize_text(receipt)
    if isinstance(parsed, Mapping):
        return _normalize_mapping(cast("Mapping[str, Any]", parsed))
    return None


def find_matching_record(receipt: str) -> str:
    """Match one receipt against the expense records ledger; return the record or a miss.

    Pass the receipt exactly as you received it — a JSON object as text (cafe POS,
    rideshare) or the raw printed lines (a hotel folio). This tool normalizes whatever
    format it gets to a common ``(vendor, amount)`` shape and looks for the *one*
    ledger record with the same vendor and a matching amount.

    Returns a JSON string, one of two shapes:

    - a confident match::

        {"match": {"record_id": "EXP-1001", "vendor": "blue bottle coffee",
                   "amount": 12.75, "date": "2026-06-03", "category": "meals"},
         "normalized": {"vendor": "Blue Bottle Coffee", "total": 12.75}}

    - no confident match (unreadable format, or nothing in the ledger lines up)::

        {"match": null, "reason": "no confident match in the records ledger"}

    It never raises: a malformed or unknown-format receipt resolves to a
    ``"match": null`` value, so the agent can report "no confident match" gracefully
    instead of looping on a bad input.
    """
    normalized = normalize_receipt(receipt)
    if normalized is None:
        return json.dumps(
            {
                "match": None,
                "reason": "could not read a vendor and amount from this receipt "
                "(unrecognized format)",
            }
        )

    wanted = _vendor_key(normalized.vendor)
    candidates = [
        record
        for record in RECORDS_LEDGER
        if _vendor_key(str(record["vendor"])) == wanted
        and abs(float(record["amount"]) - normalized.total) <= _AMOUNT_TOLERANCE
    ]
    normalized_view = {"vendor": normalized.vendor, "total": normalized.total}
    if len(candidates) == 1:
        return json.dumps({"match": candidates[0], "normalized": normalized_view})
    return json.dumps(
        {
            "match": None,
            "reason": "no confident match in the records ledger",
            "normalized": normalized_view,
        }
    )


def check_reimbursement(expense_id: str) -> str:
    """STRETCH (Segment 6 / bonus): has ``expense_id`` already been paid back?

    Scans the bank transactions for a **credit** that offsets the expense's amount —
    the money hit the account, so the expense cancels out. Returns a JSON string with
    ``reimbursed`` true/false (or ``null`` for an unknown expense id) plus the matching
    transaction when found.

    This is deliberately *not* part of the core mini-project's one-new-tool slice — it
    is the canonical "first thing you'd add next" that seams into the end-of-week
    project.
    """
    record = next((r for r in RECORDS_LEDGER if r["record_id"] == expense_id), None)
    if record is None:
        return json.dumps({"reimbursed": None, "reason": f"unknown expense id {expense_id!r}"})

    amount = float(record["amount"])
    for txn in BANK_TRANSACTIONS:
        is_credit = str(txn["type"]) == "credit"
        offsets = abs(float(txn["amount"]) - amount) <= _AMOUNT_TOLERANCE
        if is_credit and offsets:
            return json.dumps({"reimbursed": True, "transaction": txn})
    return json.dumps({"reimbursed": False, "expense_id": expense_id})


def receipt_text(receipt_id: str) -> str:
    """Return a receipt's ``raw`` payload as the string an agent would be handed.

    A convenience for building tasks and tests: dict-shaped receipts come back as a
    JSON string, the text-shaped folio comes back verbatim. Raises ``KeyError`` for an
    unknown id (a test/authoring helper, not a tool the model calls).
    """
    receipt = next((r for r in RECEIPTS if r["id"] == receipt_id), None)
    if receipt is None:
        raise KeyError(f"no receipt with id {receipt_id!r}")
    raw = receipt["raw"]
    return raw if isinstance(raw, str) else json.dumps(raw)
