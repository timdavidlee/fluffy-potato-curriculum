"""A mock "orders" API for the L23 script-centric skill example.

This is *teaching material* for L23 (Skill patterns & composition), not part of
the real curriculum-authoring toolchain. It fills the **script-centric
(API/integration recipe)** archetype gap: a deterministic operation whose payload
is a genuinely messy, nested, heterogeneous JSON contract. The point of the
paired ``example-get-order`` skill is that wrapping this contract in a script the
agent *runs* beats making the model reason through the raw shape on every call.

Everything here is offline and deterministic — three canned orders, no network.
Run it as a CLI::

    uv run python -m fluffy_potato_curriculum.lessons.L23.example_skills.get_order.get_order_api ORD-1001

or import :func:`get_order` / :func:`get_order_json` directly.
"""

from __future__ import annotations

import json
import sys
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class OrderNotFoundError(KeyError):
    """Raised when an order id is not in the canned dataset."""


class Address(BaseModel):
    kind: Literal["billing", "shipping"]
    street: str
    city: str
    region: str
    postal_code: str
    country: str


class Customer(BaseModel):
    customer_id: str
    name: str
    email: str
    loyalty_tier: Literal["none", "silver", "gold", "platinum"]
    # A variable-length list: some orders ship and bill to the same place (one
    # entry), some to two. The caller can't assume a fixed count.
    addresses: list[Address]


class LineItem(BaseModel):
    sku: str
    name: str
    quantity: int
    unit_price_cents: int
    category: str
    # Per-item options vary by product (size / color / engraving ...) — the keys
    # are heterogeneous across items, which is part of why the raw contract is
    # annoying to reason through by hand.
    options: dict[str, str] = Field(default_factory=dict)


class CardPayment(BaseModel):
    method: Literal["card"] = "card"
    brand: str
    last4: str
    exp: str


class PaypalPayment(BaseModel):
    method: Literal["paypal"] = "paypal"
    email: str


class GiftCardPayment(BaseModel):
    method: Literal["gift_card"] = "gift_card"
    code_last4: str
    remaining_balance_cents: int


# A discriminated union: the shape of ``payment`` depends on ``method``. This is
# the heterogeneity that makes a hand-written parse error-prone and a script that
# knows the contract valuable. Always read ``method`` before the other fields.
Payment = Annotated[
    CardPayment | PaypalPayment | GiftCardPayment,
    Field(discriminator="method"),
]


class Promotion(BaseModel):
    code: str
    kind: Literal["percent", "fixed", "free_shipping"]
    amount_cents: int


class Pricing(BaseModel):
    subtotal_cents: int
    discount_cents: int
    tax_cents: int
    shipping_cents: int
    total_cents: int
    applied_promotions: list[Promotion]


class Tracking(BaseModel):
    carrier: str
    number: str
    url: str


class FulfillmentEvent(BaseModel):
    event: Literal["created", "packed", "shipped", "delivered", "returned"]
    at: str
    # Optional: only some events carry a note. Another "present sometimes" field.
    note: str | None = None


class Fulfillment(BaseModel):
    events: list[FulfillmentEvent]
    # Present only once an order has shipped — ``None`` otherwise.
    tracking: Tracking | None = None


class Order(BaseModel):
    order_id: str
    status: Literal["pending", "paid", "fulfilled", "cancelled", "refunded"]
    placed_at: str
    customer: Customer
    line_items: list[LineItem]
    payment: Payment
    pricing: Pricing
    fulfillment: Fulfillment
    metadata: dict[str, str] = Field(default_factory=dict)


# --- Canned dataset (three orders, one per payment method) -------------------

_ORDERS: dict[str, Order] = {
    "ORD-1001": Order(
        order_id="ORD-1001",
        status="paid",
        placed_at="2026-06-30T14:05:00Z",
        customer=Customer(
            customer_id="CUST-42",
            name="Ada Lovelace",
            email="ada@example.com",
            loyalty_tier="gold",
            addresses=[
                Address(
                    kind="billing",
                    street="12 Analytical Way",
                    city="London",
                    region="LDN",
                    postal_code="EC1A 1BB",
                    country="GB",
                ),
                Address(
                    kind="shipping",
                    street="1 Engine Room",
                    city="London",
                    region="LDN",
                    postal_code="EC2A 2AA",
                    country="GB",
                ),
            ],
        ),
        line_items=[
            LineItem(
                sku="KEEB-87",
                name="Mechanical keyboard",
                quantity=1,
                unit_price_cents=12900,
                category="peripherals",
                options={"layout": "ISO", "switch": "brown"},
            ),
            LineItem(
                sku="CBL-USC-2M",
                name="USB-C cable (2m)",
                quantity=2,
                unit_price_cents=1500,
                category="cables",
            ),
        ],
        payment=CardPayment(brand="visa", last4="4242", exp="2029-04"),
        pricing=Pricing(
            subtotal_cents=15900,
            discount_cents=1590,
            tax_cents=2862,
            shipping_cents=0,
            total_cents=17172,
            applied_promotions=[Promotion(code="LOYAL10", kind="percent", amount_cents=1590)],
        ),
        fulfillment=Fulfillment(
            events=[
                FulfillmentEvent(event="created", at="2026-06-30T14:05:00Z"),
                FulfillmentEvent(event="packed", at="2026-06-30T18:20:00Z", note="fragile"),
            ],
        ),
        metadata={"channel": "web", "gift": "false"},
    ),
    "ORD-1002": Order(
        order_id="ORD-1002",
        status="fulfilled",
        placed_at="2026-06-28T09:10:00Z",
        customer=Customer(
            customer_id="CUST-7",
            name="Grace Hopper",
            email="grace@example.com",
            loyalty_tier="platinum",
            addresses=[
                Address(
                    kind="shipping",
                    street="200 Compiler Ct",
                    city="Arlington",
                    region="VA",
                    postal_code="22201",
                    country="US",
                ),
            ],
        ),
        line_items=[
            LineItem(
                sku="BOOK-COBOL",
                name="History of COBOL",
                quantity=1,
                unit_price_cents=3200,
                category="books",
            ),
            LineItem(
                sku="MUG-BUG",
                name="First-bug mug",
                quantity=3,
                unit_price_cents=1200,
                category="drinkware",
                options={"color": "navy"},
            ),
            LineItem(
                sku="STK-PACK",
                name="Sticker pack",
                quantity=1,
                unit_price_cents=600,
                category="misc",
            ),
        ],
        payment=PaypalPayment(email="grace@example.com"),
        pricing=Pricing(
            subtotal_cents=7400,
            discount_cents=0,
            tax_cents=444,
            shipping_cents=0,
            total_cents=7844,
            applied_promotions=[Promotion(code="SHIPFREE", kind="free_shipping", amount_cents=0)],
        ),
        fulfillment=Fulfillment(
            events=[
                FulfillmentEvent(event="created", at="2026-06-28T09:10:00Z"),
                FulfillmentEvent(event="packed", at="2026-06-28T11:00:00Z"),
                FulfillmentEvent(event="shipped", at="2026-06-28T16:45:00Z"),
                FulfillmentEvent(
                    event="delivered", at="2026-06-30T13:02:00Z", note="left with neighbor"
                ),
            ],
            tracking=Tracking(
                carrier="UPS",
                number="1Z999AA10123456784",
                url="https://track.example.com/1Z999AA10123456784",
            ),
        ),
        metadata={"channel": "mobile", "gift": "true"},
    ),
    "ORD-1003": Order(
        order_id="ORD-1003",
        status="refunded",
        placed_at="2026-06-20T20:00:00Z",
        customer=Customer(
            customer_id="CUST-99",
            name="Alan Turing",
            email="alan@example.com",
            loyalty_tier="silver",
            addresses=[
                Address(
                    kind="billing",
                    street="7 Bletchley Rd",
                    city="Milton Keynes",
                    region="MK",
                    postal_code="MK3 6EB",
                    country="GB",
                ),
            ],
        ),
        line_items=[
            LineItem(
                sku="PUZ-ENIGMA",
                name="Enigma puzzle box",
                quantity=1,
                unit_price_cents=8900,
                category="puzzles",
                options={"difficulty": "hard", "engraving": "AMT"},
            ),
        ],
        payment=GiftCardPayment(code_last4="8080", remaining_balance_cents=1100),
        pricing=Pricing(
            subtotal_cents=8900,
            discount_cents=0,
            tax_cents=1780,
            shipping_cents=499,
            total_cents=11179,
            applied_promotions=[],
        ),
        fulfillment=Fulfillment(
            events=[
                FulfillmentEvent(event="created", at="2026-06-20T20:00:00Z"),
                FulfillmentEvent(event="packed", at="2026-06-21T08:30:00Z"),
                FulfillmentEvent(event="shipped", at="2026-06-21T15:00:00Z"),
                FulfillmentEvent(
                    event="returned", at="2026-06-27T10:15:00Z", note="customer changed mind"
                ),
            ],
        ),
        metadata={"channel": "web", "gift": "false", "refund_reason": "return"},
    ),
}


def known_order_ids() -> list[str]:
    """The order ids the mock API knows about, in a stable order."""
    return list(_ORDERS)


def get_order(order_id: str) -> Order:
    """Return the canned :class:`Order` for ``order_id``.

    Raises :class:`OrderNotFoundError` if the id is unknown.
    """
    try:
        return _ORDERS[order_id]
    except KeyError as exc:
        raise OrderNotFoundError(order_id) from exc


def get_order_json(order_id: str) -> str:
    """Return the order as indented JSON — the exact string the CLI prints."""
    return get_order(order_id).model_dump_json(indent=2)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: print one order's JSON to stdout, or an error to stderr.

    Exit codes: ``0`` success, ``1`` unknown order id, ``2`` wrong usage.
    """
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        error = {"error": "usage: get_order_api <ORDER_ID>", "known": known_order_ids()}
        print(json.dumps(error), file=sys.stderr)
        return 2

    order_id = args[0]
    try:
        print(get_order_json(order_id))
    except OrderNotFoundError:
        error = {"error": "order not found", "order_id": order_id, "known": known_order_ids()}
        print(json.dumps(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
