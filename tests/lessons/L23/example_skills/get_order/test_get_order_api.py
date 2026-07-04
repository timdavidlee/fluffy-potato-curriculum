import json

import pytest

from fluffy_potato_curriculum.lessons.L23.example_skills.get_order.get_order_api import (
    OrderNotFoundError,
    get_order,
    get_order_json,
    known_order_ids,
    main,
)


def test_known_ids_are_the_three_canned_orders() -> None:
    assert known_order_ids() == ["ORD-1001", "ORD-1002", "ORD-1003"]


def test_get_order_returns_matching_id() -> None:
    assert get_order("ORD-1001").order_id == "ORD-1001"


def test_unknown_id_raises() -> None:
    with pytest.raises(OrderNotFoundError):
        get_order("ORD-9999")


@pytest.mark.parametrize(
    ("order_id", "method"),
    [("ORD-1001", "card"), ("ORD-1002", "paypal"), ("ORD-1003", "gift_card")],
)
def test_payment_is_discriminated_by_method(order_id: str, method: str) -> None:
    assert get_order(order_id).payment.method == method


def test_json_is_parseable_and_round_trips_id() -> None:
    payload = json.loads(get_order_json("ORD-1002"))
    assert payload["order_id"] == "ORD-1002"


def test_shipped_order_has_tracking() -> None:
    assert get_order("ORD-1002").fulfillment.tracking is not None


def test_unshipped_order_has_no_tracking() -> None:
    assert get_order("ORD-1001").fulfillment.tracking is None


def test_main_valid_id_exits_zero() -> None:
    assert main(["ORD-1001"]) == 0


def test_main_valid_id_prints_order_json(capsys: pytest.CaptureFixture[str]) -> None:
    main(["ORD-1001"])
    assert json.loads(capsys.readouterr().out)["order_id"] == "ORD-1001"


def test_main_unknown_id_exits_one() -> None:
    assert main(["ORD-9999"]) == 1


def test_main_unknown_id_reports_error_on_stderr(capsys: pytest.CaptureFixture[str]) -> None:
    main(["ORD-9999"])
    assert json.loads(capsys.readouterr().err)["error"] == "order not found"


def test_main_no_args_exits_two() -> None:
    assert main([]) == 2
