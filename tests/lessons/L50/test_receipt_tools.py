"""Tests for the L50 mini-project's one new tool, ``find_matching_record``.

The point of these tests is exactly the roadmap's "written and tested in a sibling
file" line: the walkthrough writes the tool live, but the proctor trusts it because
these cover the two behaviors the lesson leans on — a confident cross-format match,
and a *graceful* miss on a malformed receipt (the failure Segment 4 traces and
Segment 5 turns into an eval case).
"""

from __future__ import annotations

import json

import pytest

from fluffy_potato_curriculum.lessons.L50.receipt_tools import (
    check_reimbursement,
    find_matching_record,
    normalize_receipt,
    receipt_text,
)


@pytest.mark.parametrize(
    ("receipt_id", "expected_record_id"),
    [
        ("R-coffee", "EXP-1001"),  # cafe POS JSON: merchant / total
        ("R-ride", "EXP-1002"),  # rideshare JSON: company / amount_charged (different names)
        ("R-hotel", "EXP-1003"),  # hotel folio: raw text lines, no JSON at all
    ],
)
def test_matches_expected_record_across_formats(receipt_id: str, expected_record_id: str) -> None:
    result = json.loads(find_matching_record(receipt_text(receipt_id)))
    assert result["match"]["record_id"] == expected_record_id


@pytest.mark.parametrize("receipt_id", ["R-unknown-vendor", "R-mystery"])
def test_no_confident_match_returns_null(receipt_id: str) -> None:
    result = json.loads(find_matching_record(receipt_text(receipt_id)))
    assert result["match"] is None


def test_malformed_receipt_is_graceful_not_raising() -> None:
    # The malformed case must resolve to a value, never an exception — this is what
    # lets the agent say "no confident match" instead of looping on a bad input.
    result = json.loads(find_matching_record("\x00 not a receipt at all <<>>"))
    assert result["match"] is None


def test_normalize_recovers_vendor_from_renamed_field() -> None:
    # The rideshare receipt names its vendor "company", not "merchant" — normalization
    # is the cross-format work the tool exists to do.
    normalized = normalize_receipt(receipt_text("R-ride"))
    assert normalized is not None and normalized.vendor == "Citywide Taxi"


def test_malformed_receipt_normalizes_to_none() -> None:
    assert normalize_receipt(receipt_text("R-mystery")) is None


@pytest.mark.parametrize(
    ("expense_id", "expected"),
    [
        ("EXP-1003", True),  # hotel expense: offset by a bank credit (BANK-501)
        ("EXP-1001", False),  # coffee expense: only a debit, never reimbursed
    ],
)
def test_check_reimbursement_detects_offsetting_credit(expense_id: str, expected: bool) -> None:
    result = json.loads(check_reimbursement(expense_id))
    assert result["reimbursed"] is expected


def test_check_reimbursement_unknown_expense_is_null() -> None:
    result = json.loads(check_reimbursement("EXP-9999"))
    assert result["reimbursed"] is None
