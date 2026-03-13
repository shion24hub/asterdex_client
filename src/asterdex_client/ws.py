"""WebSocket helpers for Aster market and user streams."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

import websockets

from asterdex_client.models import (
    AccountUpdateEvent,
    BookTickerEvent,
    DepthUpdateEvent,
    ListenKeyExpiredEvent,
    OrderTradeUpdateEvent,
)

WS_BASE_URL = "wss://fstream.asterdex.com/ws"


def parse_ws_event(
    payload: dict[str, Any],
) -> (
    DepthUpdateEvent
    | BookTickerEvent
    | AccountUpdateEvent
    | OrderTradeUpdateEvent
    | ListenKeyExpiredEvent
):
    """Parse a raw WebSocket payload into a typed event.

    Args:
        payload: Raw WebSocket payload.

    Returns:
        A typed event instance.

    Raises:
        ValueError: Raised when the payload type is unsupported.
    """

    event_type = str(payload["e"])
    if event_type == "depthUpdate":
        return DepthUpdateEvent(
            event_type=event_type,
            event_time=int(payload["E"]),
            symbol=str(payload["s"]),
            first_update_id=int(payload["U"]),
            final_update_id=int(payload["u"]),
            previous_final_update_id=int(payload.get("pu", payload["U"]) - 1),
            bids=[(str(price), str(qty)) for price, qty in payload.get("b", [])],
            asks=[(str(price), str(qty)) for price, qty in payload.get("a", [])],
        )
    if event_type == "bookTicker":
        return BookTickerEvent(
            event_type=event_type,
            event_time=int(payload["E"]),
            symbol=str(payload["s"]),
            bid_price=str(payload["b"]),
            bid_qty=str(payload["B"]),
            ask_price=str(payload["a"]),
            ask_qty=str(payload["A"]),
        )
    if event_type == "ACCOUNT_UPDATE":
        account = payload["a"]
        return AccountUpdateEvent(
            event_type=event_type,
            event_time=int(payload["E"]),
            transaction_time=int(payload["T"]),
            reason=str(account["m"]),
            balances=list(account.get("B", [])),
            positions=list(account.get("P", [])),
        )
    if event_type == "ORDER_TRADE_UPDATE":
        return OrderTradeUpdateEvent(
            event_type=event_type,
            event_time=int(payload["E"]),
            transaction_time=int(payload["T"]),
            order=dict(payload["o"]),
        )
    if event_type == "listenKeyExpired":
        return ListenKeyExpiredEvent(
            event_type=event_type,
            event_time=int(payload["E"]),
            listen_key=str(payload["listenKey"]),
        )
    raise ValueError(f"Unsupported event type: {event_type}")


class AsterWsClient:
    """Async WebSocket client for Aster stream subscriptions."""

    def depth_stream_name(self, symbol: str, speed: str | None = None) -> str:
        """Return a diff depth stream name for a symbol."""

        base = f"{symbol.lower()}@depth"
        if speed is None:
            return base
        return f"{base}@{speed}"

    def book_ticker_stream_name(self, symbol: str) -> str:
        """Return a book ticker stream name for a symbol."""

        return f"{symbol.lower()}@bookTicker"

    async def stream(self, stream_name: str) -> AsyncIterator[Any]:
        """Yield parsed events from one WebSocket stream."""

        async with websockets.connect(f"{WS_BASE_URL}/{stream_name}") as websocket:
            async for message in websocket:
                payload = json.loads(message)
                yield parse_ws_event(payload)
