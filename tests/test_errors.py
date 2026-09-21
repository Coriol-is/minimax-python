import pytest

from minimax_api.errors import (
    AmbiguousWriteError,
    ConcurrencyError,
    MinimaxAuthError,
    MinimaxError,
    NotFoundError,
    RateBudgetExceeded,
    TransportError,
    ValidationError,
)


def test_every_error_descends_from_minimax_error() -> None:
    for cls in (
        MinimaxAuthError,
        RateBudgetExceeded,
        ConcurrencyError,
        NotFoundError,
        ValidationError,
        TransportError,
        AmbiguousWriteError,
    ):
        assert issubclass(cls, MinimaxError)


def test_terminal_auth_error_is_not_retryable() -> None:
    error = MinimaxAuthError("bad password", terminal=True)
    assert error.terminal is True
    assert error.retryable is False


def test_non_terminal_auth_error_is_retryable() -> None:
    assert MinimaxAuthError("token expired", terminal=False).retryable is True


def test_transport_error_is_retryable() -> None:
    assert TransportError("connection reset").retryable is True


def test_rate_budget_exceeded_carries_retry_after_and_is_retryable() -> None:
    error = RateBudgetExceeded("daily budget spent", retry_after=3600.0)
    assert error.retry_after == 3600.0
    assert error.retryable is True


def test_concurrency_error_is_not_retryable_by_replay() -> None:
    # A RowVersion conflict must be re-read and re-evaluated, never replayed.
    assert ConcurrencyError("RowVersion conflict").retryable is False


def test_validation_error_keeps_the_server_explanation() -> None:
    error = ValidationError(
        "Name is required", status_code=400, payload={"Message": "Name is required"}
    )
    assert error.status_code == 400
    assert error.payload == {"Message": "Name is required"}
    assert error.retryable is False


def test_not_found_is_not_retryable() -> None:
    assert NotFoundError("no such customer").retryable is False


def test_errors_can_be_caught_by_base_class() -> None:
    with pytest.raises(MinimaxError):
        raise NotFoundError("no such customer")


def test_ambiguous_write_error_is_not_retryable() -> None:
    # The whole point: a caller must never resend the same payload just
    # because this type looks similar to TransportError.
    assert AmbiguousWriteError("outcome unknown").retryable is False
