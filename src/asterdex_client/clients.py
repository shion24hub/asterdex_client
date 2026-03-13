"""Public async REST clients for Aster API families."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, cast
from urllib.parse import urlencode

from asterdex_client.auth import V1HmacSigner, V3EvmSigner
from asterdex_client.models import (
    BookTicker,
    ExchangeInfo,
    ListenKey,
    Order,
    OrderBookSnapshot,
    parse_book_ticker,
    parse_exchange_info,
    parse_listen_key,
    parse_order,
    parse_order_book_snapshot,
)
from asterdex_client.transport import AbstractTransport, HttpxTransport

REST_BASE_URL = "https://fapi.asterdex.com"


@dataclass(slots=True, frozen=True)
class AsterV1Client:
    """Async client for the Aster v1 futures API.

    Args:
        api_key: Public API key.
        signer: HMAC signer.
        transport: Optional custom transport.
    """

    api_key: str
    signer: V1HmacSigner
    transport: AbstractTransport | None = None

    def __post_init__(self) -> None:
        if self.transport is None:
            object.__setattr__(
                self, "transport", HttpxTransport(base_url=REST_BASE_URL)
            )

    @property
    def _transport(self) -> AbstractTransport:
        if self.transport is None:
            raise RuntimeError("Transport is not configured")
        return self.transport

    async def get_exchange_info(self) -> ExchangeInfo:
        """Fetch exchange metadata."""

        payload = await self._transport.request(
            method="GET", path="/fapi/v1/exchangeInfo"
        )
        return parse_exchange_info(payload)

    async def get_order_book(
        self, symbol: str, *, limit: int | None = None
    ) -> OrderBookSnapshot:
        """Fetch an order book snapshot."""

        params = {"symbol": symbol}
        if limit is not None:
            params["limit"] = str(limit)
        payload = await self._transport.request(
            method="GET", path="/fapi/v1/depth", params=params
        )
        return parse_order_book_snapshot(payload)

    async def get_book_ticker(self, symbol: str) -> BookTicker:
        """Fetch the best bid/ask for a symbol."""

        payload = await self._transport.request(
            method="GET",
            path="/fapi/v1/ticker/bookTicker",
            params={"symbol": symbol},
        )
        return parse_book_ticker(payload)

    async def create_order(
        self,
        *,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        **extra: str,
    ) -> Order:
        """Create a new order."""

        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            **extra,
        }
        payload = await self._signed_request("POST", "/fapi/v1/order", params=params)
        return parse_order(payload)

    async def get_order(
        self,
        *,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
    ) -> Order:
        """Query one order."""

        params = self._order_lookup_params(
            symbol=symbol,
            order_id=order_id,
            orig_client_order_id=orig_client_order_id,
        )
        payload = await self._signed_request("GET", "/fapi/v1/order", params=params)
        return parse_order(payload)

    async def cancel_order(
        self,
        *,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
    ) -> Order:
        """Cancel one order."""

        params = self._order_lookup_params(
            symbol=symbol,
            order_id=order_id,
            orig_client_order_id=orig_client_order_id,
        )
        payload = await self._signed_request("DELETE", "/fapi/v1/order", params=params)
        return parse_order(payload)

    async def cancel_all_open_orders(self, symbol: str) -> list[dict[str, Any]]:
        """Cancel all open orders for a symbol."""

        payload = await self._signed_request(
            "DELETE",
            "/fapi/v1/allOpenOrders",
            params={"symbol": symbol},
        )
        return cast(list[dict[str, Any]], payload)

    async def get_open_order(
        self,
        *,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
    ) -> Order:
        """Query one open order."""

        params = self._order_lookup_params(
            symbol=symbol,
            order_id=order_id,
            orig_client_order_id=orig_client_order_id,
        )
        payload = await self._signed_request("GET", "/fapi/v1/openOrder", params=params)
        return parse_order(payload)

    async def get_open_orders(
        self, *, symbol: str | None = None
    ) -> list[dict[str, Any]]:
        """Fetch open orders."""

        params = {"symbol": symbol} if symbol is not None else {}
        payload = await self._signed_request(
            "GET", "/fapi/v1/openOrders", params=params
        )
        return cast(list[dict[str, Any]], payload)

    async def get_all_orders(
        self, *, symbol: str, **extra: str
    ) -> list[dict[str, Any]]:
        """Fetch historical orders for a symbol."""

        payload = await self._signed_request(
            "GET",
            "/fapi/v1/allOrders",
            params={"symbol": symbol, **extra},
        )
        return cast(list[dict[str, Any]], payload)

    async def start_user_stream(self) -> ListenKey:
        """Create or extend a user stream."""

        payload = await self._transport.request(
            method="POST",
            path="/fapi/v1/listenKey",
            headers={"X-MBX-APIKEY": self.api_key},
        )
        return parse_listen_key(payload)

    async def keepalive_user_stream(self, listen_key: str) -> ListenKey:
        """Keep a user stream alive."""

        payload = await self._transport.request(
            method="PUT",
            path="/fapi/v1/listenKey",
            params={"listenKey": listen_key},
            headers={"X-MBX-APIKEY": self.api_key},
        )
        return parse_listen_key(payload)

    async def close_user_stream(self, listen_key: str) -> None:
        """Close a user stream."""

        await self._transport.request(
            method="DELETE",
            path="/fapi/v1/listenKey",
            params={"listenKey": listen_key},
            headers={"X-MBX-APIKEY": self.api_key},
        )

    async def _signed_request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, str | int],
    ) -> Any:
        signed_params = {key: str(value) for key, value in params.items()}
        signed_params["timestamp"] = str(self.signer.current_timestamp_ms())
        signature_payload = urlencode(signed_params)
        signed_params["signature"] = self.signer.sign_payload(signature_payload)
        return await self._transport.request(
            method=method,
            path=path,
            params=signed_params,
            headers={"X-MBX-APIKEY": self.api_key},
        )

    @staticmethod
    def _order_lookup_params(
        *,
        symbol: str,
        order_id: int | None,
        orig_client_order_id: str | None,
    ) -> dict[str, str | int]:
        if order_id is None and orig_client_order_id is None:
            raise ValueError("Either order_id or orig_client_order_id must be provided")
        params: dict[str, str | int] = {"symbol": symbol}
        if order_id is not None:
            params["orderId"] = order_id
        if orig_client_order_id is not None:
            params["origClientOrderId"] = orig_client_order_id
        return params


@dataclass(slots=True, frozen=True)
class AsterV3Client:
    """Async client for the Aster v3 futures API.

    Args:
        account: User wallet address.
        signer: EVM signer helper.
        transport: Optional custom transport.
    """

    account: str
    signer: V3EvmSigner
    transport: AbstractTransport | None = None

    def __post_init__(self) -> None:
        if self.transport is None:
            object.__setattr__(
                self, "transport", HttpxTransport(base_url=REST_BASE_URL)
            )

    @property
    def _transport(self) -> AbstractTransport:
        if self.transport is None:
            raise RuntimeError("Transport is not configured")
        return self.transport

    async def get_exchange_info(self) -> ExchangeInfo:
        """Fetch exchange metadata."""

        payload = await self._signed_request(
            "GET",
            "/fapi/v3/exchangeInfo",
            instruction="market_data",
        )
        return parse_exchange_info(payload)

    async def get_order_book(
        self, symbol: str, *, limit: int | None = None
    ) -> OrderBookSnapshot:
        """Fetch an order book snapshot."""

        params = {"symbol": symbol}
        if limit is not None:
            params["limit"] = str(limit)
        payload = await self._signed_request(
            "GET",
            "/fapi/v3/depth",
            instruction="market_data",
            params=params,
        )
        return parse_order_book_snapshot(payload)

    async def get_book_ticker(self, symbol: str) -> BookTicker:
        """Fetch the best bid/ask for a symbol."""

        payload = await self._signed_request(
            "GET",
            "/fapi/v3/ticker/bookTicker",
            instruction="market_data",
            params={"symbol": symbol},
        )
        return parse_book_ticker(payload)

    async def create_order(
        self,
        *,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        **extra: str,
    ) -> Order:
        """Create a new order."""

        payload = await self._signed_request(
            "POST",
            "/fapi/v3/order",
            instruction="order",
            data={
                "symbol": symbol,
                "side": side,
                "type": order_type,
                "quantity": quantity,
                **extra,
            },
        )
        return parse_order(payload)

    async def get_order(
        self,
        *,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
    ) -> Order:
        """Query one order."""

        payload = await self._signed_request(
            "GET",
            "/fapi/v3/order",
            instruction="order",
            params=self._order_lookup_params(
                symbol=symbol,
                order_id=order_id,
                orig_client_order_id=orig_client_order_id,
            ),
        )
        return parse_order(payload)

    async def cancel_order(
        self,
        *,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
    ) -> Order:
        """Cancel one order."""

        payload = await self._signed_request(
            "DELETE",
            "/fapi/v3/order",
            instruction="order",
            params=self._order_lookup_params(
                symbol=symbol,
                order_id=order_id,
                orig_client_order_id=orig_client_order_id,
            ),
        )
        return parse_order(payload)

    async def cancel_all_open_orders(self, symbol: str) -> list[dict[str, Any]]:
        """Cancel all open orders for a symbol."""

        payload = await self._signed_request(
            "DELETE",
            "/fapi/v3/allOpenOrders",
            instruction="order",
            params={"symbol": symbol},
        )
        return cast(list[dict[str, Any]], payload)

    async def get_open_order(
        self,
        *,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
    ) -> Order:
        """Query one open order."""

        payload = await self._signed_request(
            "GET",
            "/fapi/v3/openOrder",
            instruction="order",
            params=self._order_lookup_params(
                symbol=symbol,
                order_id=order_id,
                orig_client_order_id=orig_client_order_id,
            ),
        )
        return parse_order(payload)

    async def get_open_orders(
        self, *, symbol: str | None = None
    ) -> list[dict[str, Any]]:
        """Fetch open orders."""

        params = {"symbol": symbol} if symbol is not None else {}
        payload = await self._signed_request(
            "GET",
            "/fapi/v3/openOrders",
            instruction="order",
            params=params,
        )
        return cast(list[dict[str, Any]], payload)

    async def get_all_orders(
        self, *, symbol: str, **extra: str
    ) -> list[dict[str, Any]]:
        """Fetch historical orders for a symbol."""

        payload = await self._signed_request(
            "GET",
            "/fapi/v3/allOrders",
            instruction="order",
            params={"symbol": symbol, **extra},
        )
        return cast(list[dict[str, Any]], payload)

    async def start_user_stream(self) -> ListenKey:
        """Create or extend a user stream."""

        payload = await self._signed_request(
            "POST",
            "/fapi/v3/listenKey",
            instruction="listen_key",
        )
        return parse_listen_key(payload)

    async def keepalive_user_stream(self, listen_key: str) -> ListenKey:
        """Keep a user stream alive."""

        payload = await self._signed_request(
            "PUT",
            "/fapi/v3/listenKey",
            instruction="listen_key",
            params={"listenKey": listen_key},
        )
        return parse_listen_key(payload)

    async def close_user_stream(self, listen_key: str) -> None:
        """Close a user stream."""

        await self._signed_request(
            "DELETE",
            "/fapi/v3/listenKey",
            instruction="listen_key",
            params={"listenKey": listen_key},
        )

    async def _signed_request(
        self,
        method: str,
        path: str,
        *,
        instruction: str,
        params: Mapping[str, str | int] | None = None,
        data: Mapping[str, str | int] | None = None,
    ) -> Any:
        nonce = self.signer.current_nonce_us()
        auth_params = {
            "user": self.account,
            "signer": self.signer.signer,
            "nonce": str(nonce),
            "signature": self.signer.sign_action(
                instruction=instruction,
                account=self.account,
                user=self.account,
                nonce=nonce,
            ),
        }
        request_params = None
        request_data = None
        if method == "POST":
            request_data = {
                **{key: str(value) for key, value in (data or {}).items()},
                **auth_params,
            }
        else:
            request_params = {
                **{key: str(value) for key, value in (params or {}).items()},
                **auth_params,
            }
        return await self._transport.request(
            method=method,
            path=path,
            params=request_params,
            data=request_data,
        )

    @staticmethod
    def _order_lookup_params(
        *,
        symbol: str,
        order_id: int | None,
        orig_client_order_id: str | None,
    ) -> dict[str, str | int]:
        if order_id is None and orig_client_order_id is None:
            raise ValueError("Either order_id or orig_client_order_id must be provided")
        params: dict[str, str | int] = {"symbol": symbol}
        if order_id is not None:
            params["orderId"] = order_id
        if orig_client_order_id is not None:
            params["origClientOrderId"] = orig_client_order_id
        return params


@dataclass(slots=True, frozen=True)
class AsterClient:
    """Thin facade exposing the recommended client split.

    Args:
        v1: Optional v1 client.
        v3: Optional v3 client.
    """

    v1: AsterV1Client | None = None
    v3: AsterV3Client | None = None

    async def get_exchange_info(self) -> ExchangeInfo:
        """Fetch exchange metadata using the public v1 endpoint."""

        if self.v1 is None:
            raise ValueError("AsterClient.v1 is not configured")
        return await self.v1.get_exchange_info()

    async def get_order_book(
        self, symbol: str, *, limit: int | None = None
    ) -> OrderBookSnapshot:
        """Fetch an order book snapshot using the public v1 endpoint."""

        if self.v1 is None:
            raise ValueError("AsterClient.v1 is not configured")
        return await self.v1.get_order_book(symbol, limit=limit)

    async def get_book_ticker(self, symbol: str) -> BookTicker:
        """Fetch a book ticker using the public v1 endpoint."""

        if self.v1 is None:
            raise ValueError("AsterClient.v1 is not configured")
        return await self.v1.get_book_ticker(symbol)

    async def create_order(
        self,
        *,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        **extra: str,
    ) -> Order:
        """Create an order using the recommended v3 private path."""

        if self.v3 is None:
            raise ValueError("AsterClient.v3 is not configured")
        return await self.v3.create_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            **extra,
        )
