import pytest

from fluffy_potato_curriculum.common.tools import calculator, flaky_fetch, lookup


@pytest.mark.parametrize(
    ("expression", "expected"),
    [("17*23", "391"), ("2 + 2", "4"), ("(3-1)*5", "10")],
)
def test_calculator_evaluates_arithmetic(expression: str, expected: str) -> None:
    assert calculator(expression) == expected


@pytest.mark.parametrize("expression", ["", "import os", "city name", "1; drop"])
def test_calculator_rejects_non_arithmetic(expression: str) -> None:
    with pytest.raises(ValueError):
        calculator(expression)


@pytest.mark.parametrize(
    ("city", "expected"),
    [("Tokyo", "37000000"), ("  lagos ", "15000000"), ("PARIS", "11000000")],
)
def test_lookup_returns_population(city: str, expected: str) -> None:
    assert lookup(city) == expected


def test_lookup_raises_on_missing_city() -> None:
    with pytest.raises(KeyError):
        lookup("Atlantis")


def test_flaky_fetch_ok_returns_a_value() -> None:
    assert flaky_fetch("https://ok") == "the answer is 42"


def test_flaky_fetch_error_returns_error_as_data() -> None:
    assert "error" in flaky_fetch("https://error")


def test_flaky_fetch_crash_raises() -> None:
    with pytest.raises(RuntimeError):
        flaky_fetch("https://crash")


def test_flaky_fetch_garbage_returns_unusable_output() -> None:
    assert flaky_fetch("https://garbage") != "the answer is 42"


@pytest.mark.parametrize("url", ["https://unknown", "http://ok", "ftp://x"])
def test_flaky_fetch_unknown_url_raises(url: str) -> None:
    with pytest.raises(ValueError):
        flaky_fetch(url)
