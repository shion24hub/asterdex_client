"""Typed models used by the Aster client."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PriceLevel = tuple[str, str]


@dataclass(slots=True, frozen=True)
class ExchangeSymbol:
    """Exchange symbol metadata.

    Args:
        symbol: Symbol name such as ``BTCUSDT``.
        raw: Original symbol payload for fields not normalized by this client.
    """

    symbol: str
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ExchangeInfo:
    """Exchange metadata response."""

    timezone: str
    server_time: int
    symbols: list[ExchangeSymbol]


@dataclass(slots=True, frozen=True)
class OrderBookSnapshot:
    """REST order book snapshot or in-memory order book state."""

    last_update_id: int
    bids: list[PriceLevel]
    asks: list[PriceLevel]


@dataclass(slots=True, frozen=True)
class BookTicker:
    """Best bid/ask snapshot."""

    symbol: str
    bid_price: str
    bid_qty: str
    ask_price: str
    ask_qty: str


@dataclass(slots=True, frozen=True)
class Order:
    """Normalized order response."""

    symbol: str
    order_id: int
    status: str
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ListenKey:
    """User stream listen key response."""

    listen_key: str


@dataclass(slots=True, frozen=True)
class DepthUpdateEvent:
    """Diff depth stream event."""

    event_type: str
    event_time: int
    symbol: str
    first_update_id: int
    final_update_id: int
    previous_final_update_id: int
    bids: list[PriceLevel]
    asks: list[PriceLevel]


@dataclass(slots=True, frozen=True)
class BookTickerEvent:
    """Book ticker stream event."""

    event_type: str
    event_time: int
    symbol: str
    bid_price: str
    bid_qty: str
    ask_price: str
    ask_qty: str


@dataclass(slots=True, frozen=True)
class AccountUpdateEvent:
    """User stream account update event."""

    event_type: str
    event_time: int
    transaction_time: int
    reason: str
    balances: list[dict[str, Any]]
    positions: list[dict[str, Any]]


@dataclass(slots=True, frozen=True)
class OrderTradeUpdateEvent:
    """User stream order/trade update event."""

    event_type: str
    event_time: int
    transaction_time: int
    order: dict[str, Any]


@dataclass(slots=True, frozen=True)
class ListenKeyExpiredEvent:
    """Listen key expiration event."""

    event_type: str
    event_time: int
    listen_key: str


def parse_exchange_info(payload: dict[str, Any]) -> ExchangeInfo:
    """Parse exchange metadata from a REST payload.

    Args:
        payload: Raw response payload.

    Returns:
        Parsed exchange info model.
    """

    symbols = [
        ExchangeSymbol(symbol=item["symbol"], raw=dict(item))
        for item in payload.get("symbols", [])
    ]
    return ExchangeInfo(
        timezone=str(payload["timezone"]),
        server_time=int(payload["serverTime"]),
        symbols=symbols,
    )


def parse_order_book_snapshot(payload: dict[str, Any]) -> OrderBookSnapshot:
    """Parse an order book snapshot payload."""

    return OrderBookSnapshot(
        last_update_id=int(payload["lastUpdateId"]),
        bids=[(str(price), str(qty)) for price, qty in payload.get("bids", [])],
        asks=[(str(price), str(qty)) for price, qty in payload.get("asks", [])],
    )


def parse_book_ticker(payload: dict[str, Any]) -> BookTicker:
    """Parse a REST book ticker payload."""

    return BookTicker(
        symbol=str(payload["symbol"]),
        bid_price=str(payload["bidPrice"]),
        bid_qty=str(payload["bidQty"]),
        ask_price=str(payload["askPrice"]),
        ask_qty=str(payload["askQty"]),
    )


def parse_order(payload: dict[str, Any]) -> Order:
    """Parse a normalized order payload."""

    return Order(
        symbol=str(payload["symbol"]),
        order_id=int(payload["orderId"]),
        status=str(payload["status"]),
        raw=dict(payload),
    )


def parse_listen_key(payload: dict[str, Any]) -> ListenKey:
    """Parse a user stream listen key payload."""

    return ListenKey(listen_key=str(payload["listenKey"]))
