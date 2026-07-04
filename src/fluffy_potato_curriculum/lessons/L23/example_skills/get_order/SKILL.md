---
name: example-get-order
description: L23 teaching example (script-centric archetype). Fetch a single order's full record from the mock orders API by order id, returning the raw JSON contract — customer, line items, a discriminated-union payment, a pricing breakdown, and fulfillment events. Use when you have a known order id and need its structured details in the exact API shape. Not for searching or listing orders, and not a real integration — the data is canned and offline.
---

# Example skill — get one order (script-centric)

> **This is L23 teaching material, not a real capability.** It illustrates the
> **script-centric (API/integration recipe)** archetype: the skill body is a thin
> wrapper and the real work is a bundled script. The orders API is a mock
> (`get_order_api.py`), offline and deterministic. See [../README.md](../README.md).

The order JSON is deliberately messy — nested objects, a per-item `options` map
whose keys differ per product, a **discriminated-union** `payment` (its fields
depend on `method`), a pricing breakdown, and a variable-length list of
fulfillment events. Reasoning through that raw shape on every call is
error-prone; running the script that already knows the contract is not. That is
the whole point of this archetype: **push the determinism into the script and
keep the markdown thin.**

## When to run it

Run this when you have a specific **order id** and need its full record. If you
only have a customer name, an email, or a date range, this is the wrong skill —
it does an id lookup and nothing else.

## How to call it

From the repo root:

```sh
uv run python -m fluffy_potato_curriculum.lessons.L23.example_skills.get_order.get_order_api <ORDER_ID>
```

Known ids for the mock: `ORD-1001` (card), `ORD-1002` (paypal, shipped with
tracking), `ORD-1003` (gift card, refunded).

## How to read the output

- **Success:** indented JSON for the order is printed to **stdout**, exit code
  `0`. Read `payment.method` **first** — it tells you which other `payment.*`
  fields exist (`card` → `brand`/`last4`/`exp`; `paypal` → `email`; `gift_card`
  → `code_last4`/`remaining_balance_cents`). `fulfillment.tracking` is present
  only once the order has shipped.
- **Unknown id:** a small JSON error object is printed to **stderr** (with the
  list of known ids), exit code `1`. Don't retry with the same id.
- **Wrong usage** (no id, or more than one): JSON usage error on stderr, exit
  code `2`.

Don't reformat or "tidy" the JSON — hand the parsed fields to the caller as they
are. The script is the contract; the markdown just says when and how to run it.
