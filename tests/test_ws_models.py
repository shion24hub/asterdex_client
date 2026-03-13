"""WebSocket event parsing tests."""

from asterdex_client.models import (
    AccountUpdateEvent,
    BookTickerEvent,
    DepthUpdateEvent,
    ListenKeyExpiredEvent,
    OrderTradeUpdateEvent,
)
from asterdex_client.ws import parse_ws_event


def test_parse_depth_update_event() -> None:
    event = parse_ws_event(
        {
            "e": "depthUpdate",
            "E": 1,
            "s": "BTCUSDT",
            "U": 10,
            "u": 12,
            "pu": 9,
            "b": [["100.0", "1.0"]],
            "a": [["101.0", "2.0"]],
        }
    )

    assert isinstance(event, DepthUpdateEvent)


def test_parse_book_ticker_event() -> None:
    event = parse_ws_event(
        {
            "e": "bookTicker",
            "E": 1,
            "s": "BTCUSDT",
            "b": "100.0",
            "B": "2.0",
            "a": "100.1",
            "A": "3.0",
        }
    )

    assert isinstance(event, BookTickerEvent)


def test_parse_account_update_event() -> None:
    event = parse_ws_event(
        {
            "e": "ACCOUNT_UPDATE",
            "E": 1,
            "T": 2,
            "a": {"m": "ORDER", "B": [], "P": []},
        }
    )

    assert isinstance(event, AccountUpdateEvent)


def test_parse_order_trade_update_event() -> None:
    event = parse_ws_event(
        {
            "e": "ORDER_TRADE_UPDATE",
            "E": 1,
            "T": 2,
            "o": {"s": "BTCUSDT", "i": 1, "X": "NEW"},
        }
    )

    assert isinstance(event, OrderTradeUpdateEvent)


def test_parse_listen_key_expired_event() -> None:
    event = parse_ws_event(
        {
            "e": "listenKeyExpired",
            "E": 1,
            "listenKey": "abc",
        }
    )

    assert isinstance(event, ListenKeyExpiredEvent)
