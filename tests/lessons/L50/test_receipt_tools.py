"""Tests for the L50 mini-project's one new tool, ``find_matching_record``.

The point of these tests is exactly the roadmap's "written and tested in a sibling
file" line: the walkthrough writes the tool live, but the proctor trusts it because
these cover the two behaviors the lesson leans on — a confident cross-format match,
and a *graceful* miss on a malformed receipt (the failure Segment 4 traces and
Segment 5 turns into an eval case).

``check_expense_policy`` is the lesson's one **LLM-in-the-loop** tool. Its coverage is
split by what each test is actually pinning:

- The *seam* tests (``FakeModel``-driven) stay offline and default: they inject replies a
  real model won't produce on purpose — a canned verdict that contradicts the policy (to
  prove the tool trusts the model, not a hidden cap table) and an unparseable reply (to
  prove the defensive parse). Those paths *can't* be exercised against a live model.
- The *behavioral* tests — does it flag an over-cap expense, does it cite the rule, does an
  uncovered category resolve to "send for review" — read the actual policy prose, so they
  are ``@pytest.mark.integration`` tests that call **live Sonnet**. They are deselected from
  the default run (see the ``integration`` marker in ``pyproject.toml``) and skip when no
  ``ANTHROPIC_API_KEY`` is set; run them with ``uv run pytest -m integration``.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import cast

import pytest
from langchain.chat_models import init_chat_model

from fluffy_potato_curriculum.common.config import get_settings
from fluffy_potato_curriculum.common.fake_model import FakeModel, text_reply
from fluffy_potato_curriculum.lessons.L50.receipt_tools import (
    PolicyModel,
    check_reimbursement,
    find_matching_record,
    make_check_expense_policy,
    normalize_receipt,
    receipt_text,
)

# The behavioral policy tests below are live-only: without a key, an `-m integration` run
# skips them cleanly rather than erroring on a missing key mid-call.
_requires_live_model = pytest.mark.skipif(
    get_settings().anthropic_api_key is None,
    reason="live policy-check integration tests need ANTHROPIC_API_KEY (see .env.example)",
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


@pytest.fixture(scope="module")
def live_policy_check() -> Callable[[str, float], str]:
    """``check_expense_policy`` wired to live Sonnet — a genuine read of the policy prose,
    the real call the offline ``ScriptedPolicyModel`` only approximated. Mirrors the gated
    live cell in the L50 lecture (module-scoped so the model is built once per run)."""
    model = init_chat_model(
        "anthropic:claude-sonnet-4-6",
        api_key=get_settings().anthropic_api_key,
        max_tokens=256,
    )
    return make_check_expense_policy(cast(PolicyModel, model))


@pytest.mark.integration
@_requires_live_model
@pytest.mark.parametrize(
    ("category", "amount"),
    [
        ("meals", 12.75),  # coffee: well within the $50 meals guidance
        ("travel", 41.20),  # taxi: within the $75 travel guidance
    ],
)
def test_check_expense_policy_approves_within_guidance(
    live_policy_check: Callable[[str, float], str],
    category: str,
    amount: float,
) -> None:
    # A live model reading the actual policy prose approves an expense that is clearly
    # under its category cap — the authentic read the mini-project's tool exists to do.
    result = json.loads(live_policy_check(category, amount))
    assert result["within_policy"] is True


@pytest.mark.integration
@_requires_live_model
def test_check_expense_policy_does_not_approve_over_cap(
    live_policy_check: Callable[[str, float], str],
) -> None:
    # An over-cap hotel ($268.40 vs the $250 nightly limit) is never silently approved.
    # A live model may render "over policy" as a hard False *or* as a hedged None (the
    # prose says such stays "should be flagged" / "need prior approval") — both mean "not
    # approved", so we assert the property that matters rather than a brittle exact label.
    result = json.loads(live_policy_check("lodging", 268.40))
    assert result["within_policy"] in (False, None)


@pytest.mark.integration
@_requires_live_model
def test_check_expense_policy_cites_the_applied_rule(
    live_policy_check: Callable[[str, float], str],
) -> None:
    # The whole point of the LLM read: it names the rule it applied, not just a verdict.
    # Uses the unambiguous meals case so the model returns a definite verdict (and thus a
    # citation) — the over-cap hedge sometimes comes back as a bare None with no citation.
    result = json.loads(live_policy_check("meals", 12.75))
    assert "50" in (result.get("citation") or "")


@pytest.mark.integration
@_requires_live_model
def test_check_expense_policy_uncovered_category_is_null(
    live_policy_check: Callable[[str, float], str],
) -> None:
    # A category the policy prose genuinely does not cover resolves to a null verdict
    # ("send for manual review"), not a crash. (The old offline test used "gifts", but the
    # real policy *does* address gifts — a live read needs a truly-uncovered category.)
    result = json.loads(live_policy_check("medical", 40.00))
    assert result["within_policy"] is None


def test_check_expense_policy_is_model_driven() -> None:
    # Prove the verdict comes from the model's reply, not a hidden cap table: a canned
    # model that flags a *within-guidance* meal must make the tool report over-policy.
    verdict = '{"within_policy": false, "citation": "canned rule", "reason": "canned"}'
    tool = make_check_expense_policy(FakeModel([text_reply(verdict)]))
    result = json.loads(tool("meals", 12.75))
    assert result["within_policy"] is False


def test_check_expense_policy_graceful_on_unparseable_reply() -> None:
    # A model reply with no readable JSON resolves to a null verdict, never an exception —
    # the same defensive-parse contract find_matching_record has for a malformed receipt.
    tool = make_check_expense_policy(FakeModel([text_reply("I'm honestly not sure here.")]))
    result = json.loads(tool("lodging", 268.40))
    assert result["within_policy"] is None
