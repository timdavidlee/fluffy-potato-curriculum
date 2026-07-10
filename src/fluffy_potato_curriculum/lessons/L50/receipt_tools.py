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

``check_expense_policy`` is the second **core** tool the agent runs. Unlike
``find_matching_record`` (a deterministic lookup the walkthrough writes live), it is
*provided* here pre-built — students register it rather than author it, so the live
tool-design workout stays a single tool while the agent still makes a genuine three-way
tool decision (match → total → check the policy). It is the lesson's one **LLM-in-the-loop
tool**: the policy is *free-form prose* (``data/expense_policy.md``), so instead of a cap
lookup the tool spins up a single ``model.invoke`` that reads the policy, judges the
expense, and cites the rule it applied — deliberately the "expensive" way where a dict
lookup would do, because real policy is guidance to interpret, not a table. Build it with
:func:`make_check_expense_policy`, handing it the model it should consult: the offline
:class:`ScriptedPolicyModel` for a reproducible keyless run (the module-level
``check_expense_policy`` is pre-wired to it), or live Sonnet in class for a genuine read —
the same live/offline seam :class:`~fluffy_potato_curriculum.common.fake_model.FakeModel`
gives the agent's own brain.

``check_reimbursement`` is the deliberately-scoped-out **stretch** tool (Segment 6 /
the student bonus): it is real and tested, but it is *not* wired into the core agent —
it is the "first thing you'd add next" hand-off, not part of the vertical slice.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, cast

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

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


POLICY_TEXT: str = (_DATA_DIR / "expense_policy.md").read_text(encoding="utf-8")
"""The company's expense policy as free-form prose — the guidance the LLM read interprets.

This is *not* a cap table: it's the paragraphs ``check_expense_policy`` hands to a model
so the model (not a dict lookup) decides whether an expense is within policy and quotes
the rule it relied on."""


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


class PolicyModel(Protocol):
    """The slice of a chat model ``check_expense_policy`` consults: a message list in, a reply out.

    A real LangChain chat model (Sonnet via ``init_chat_model``) and the offline
    :class:`ScriptedPolicyModel` below both satisfy this — the same live/offline seam
    :class:`~fluffy_potato_curriculum.common.fake_model.FakeModel` gives the agent loop.
    The ``messages`` parameter is positional-only so a real runnable (whose first arg is
    ``input``) and a scripted stand-in (``messages``) both match structurally.
    """

    def invoke(self, messages: list[BaseMessage], /) -> BaseMessage: ...


_POLICY_SYSTEM = (
    "You are an expense-policy reviewer. Read the company policy below and decide "
    "whether a single expense is within policy. Quote the specific rule you applied.\n\n"
    f"{POLICY_TEXT}\n\n"
    'Reply with ONLY a JSON object of the form: {"within_policy": <true|false|null>, '
    '"citation": "<the rule you applied, quoted from the policy>", '
    '"reason": "<one short sentence>"}. Use null for within_policy when the policy '
    "gives no clear guidance for this category."
)


def _policy_messages(category: str, amount: float) -> list[BaseMessage]:
    """Build the two-message prompt the policy model reads: the policy, then the expense."""
    human = f"Expense to evaluate:\n- category: {category}\n- amount: {amount:.2f}"
    return [SystemMessage(content=_POLICY_SYSTEM), HumanMessage(content=human)]


_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def _reply_text(reply: BaseMessage) -> str:
    """The reply's text, coerced to ``str`` (message content can be a list of blocks)."""
    content = reply.content
    return content if isinstance(content, str) else str(content)


def _parse_verdict(reply_text: str) -> dict[str, Any]:
    """Pull the JSON verdict out of the model's reply; a bad reply becomes a value, not a crash.

    The same prompt-only-JSON + defensive-parse pattern L02 taught: the model is *asked*
    for JSON but we never trust it blindly — an unreadable reply resolves to a graceful
    ``within_policy: null`` value the agent can report, instead of raising into the loop.

    Example input:
        '{"within_policy": false, "citation": "Hotels ... $250", "reason": "over cap"}'
    Example output:
        {"within_policy": False, "citation": "Hotels ... $250", "reason": "over cap"}
    """
    match = _JSON_OBJECT_RE.search(reply_text)
    if match is not None:
        try:
            parsed: Any = json.loads(match.group(0))
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict) and "within_policy" in parsed:
            return cast("dict[str, Any]", parsed)
    return {
        "within_policy": None,
        "reason": "could not read a policy verdict from the model's reply",
    }


def make_check_expense_policy(model: PolicyModel) -> Callable[[str, float], str]:
    """Build the policy-check tool, wired to the model it should consult.

    Unlike ``find_matching_record`` (a deterministic lookup), the policy is *free-form
    prose*, so this tool does a single LLM read to interpret it — deliberately the
    "expensive" call where a cap table would be a dict lookup. Hand it the offline
    :class:`ScriptedPolicyModel` for a reproducible keyless run, or live Sonnet in class
    for a genuine read; the tool body is identical, only the model changes.
    """

    def check_expense_policy(category: str, amount: float) -> str:
        """Is an expense within company policy? Reads the policy prose and cites the rule.

        Call this after a receipt matches a record — the matched record carries both
        ``category`` and ``amount``. This does **not** apply a fixed cap table: it hands
        the free-form expense policy to a model, which interprets it and quotes the rule
        it relied on.

        Returns a JSON string, one of two shapes:

        - a judged expense::

            {"within_policy": false,
             "citation": "Hotels are reimbursed up to $250 per night, taxes included.",
             "reason": "268.40 is over the $250 nightly lodging limit — flag for approval."}

        - or, when the policy gives no clear guidance (or the reply can't be read), a
          graceful "can't judge this" value, never a crash::

            {"within_policy": null, "reason": "..."}
        """
        reply = model.invoke(_policy_messages(category, amount))
        return json.dumps(_parse_verdict(_reply_text(reply)))

    return check_expense_policy


# The offline stand-in for the model the policy tool consults. The tool always does a
# real ``model.invoke``; offline we point it here so a keyless restart-run-all stays
# deterministic. This approximates the judgement a policy-reading model *would* reach
# with a small cap table read from the same prose — it stands in for an interpretation,
# it is not one. In class you swap it for live Sonnet (see make_check_expense_policy).
_OFFLINE_CAPS: dict[str, tuple[float, str]] = {
    "meals": (50.0, "Individual meals while travelling are reimbursed up to $50 per person."),
    "travel": (75.0, "Taxis, rideshares, and transit are reimbursed up to $75 per trip."),
    "lodging": (250.0, "Hotels are reimbursed up to $250 per night, taxes included."),
    "supplies": (150.0, "Office and project supplies are reimbursed up to $150 per purchase."),
}

_EXPENSE_RE = re.compile(
    r"category:\s*(?P<category>.+)\n-\s*amount:\s*(?P<amount>[0-9.]+)", re.IGNORECASE
)


def _offline_verdict(category: str, amount: float) -> dict[str, Any]:
    """The verdict the offline stand-in returns — a cap-table approximation of a read."""
    entry = _OFFLINE_CAPS.get(category.strip().lower())
    if entry is None:
        return {
            "within_policy": None,
            "reason": f"the policy gives no clear guidance for category {category!r}; "
            "send it for manual review.",
        }
    cap, citation = entry
    within = amount <= cap + _AMOUNT_TOLERANCE
    reason = (
        f"{amount:.2f} is within the ${cap:.0f} {category} limit."
        if within
        else f"{amount:.2f} is over the ${cap:.0f} {category} limit — flag for approval."
    )
    return {"within_policy": within, "citation": citation, "reason": reason}


@dataclass
class ScriptedPolicyModel:
    """Deterministic offline stand-in for the model the policy tool consults.

    Mirrors :class:`~fluffy_potato_curriculum.common.fake_model.FakeModel`'s role for the
    agent's brain: the tool always calls ``model.invoke``, but offline this scripted judge
    reads the expense out of the prompt and returns the verdict a policy-reading model
    *would* reach (approximated by a cap table), so a keyless run is reproducible. Swap it
    for live Sonnet in class to get a genuine read of the prose.
    """

    def invoke(self, messages: list[BaseMessage], /) -> AIMessage:
        human = messages[-1].content if messages else ""
        text = human if isinstance(human, str) else str(human)
        match = _EXPENSE_RE.search(text)
        if match is None:
            verdict: dict[str, Any] = {
                "within_policy": None,
                "reason": "could not read the expense from the prompt",
            }
        else:
            verdict = _offline_verdict(
                match.group("category").strip(), float(match.group("amount"))
            )
        return AIMessage(content=json.dumps(verdict))


check_expense_policy = make_check_expense_policy(ScriptedPolicyModel())
"""The provided policy tool, pre-wired to the offline stand-in so ``import`` is drop-in
and the walkthrough runs reproducibly with no key. Rebuild it with
``make_check_expense_policy(live_model)`` to have a real model read the prose — see the
gated live cell in the L50 notebook."""


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
