"""REST client request construction tests."""

from collections.abc import Mapping
from typing import Any

import pytest

from asterdex_client.auth import V1HmacSigner, V3EvmSigner
from asterdex_client.clients import AsterV1Client, AsterV3Client
from asterdex_client.models import BookTicker, ExchangeInfo, OrderBookSnapshot
from asterdex_client.transport import RecordedRequest, ResponseStub, StubTransport


@pytest.mark.asyncio
async def test_v1_create_order_signs_query_request() -> None:
    transport = StubTransport(
        [
            ResponseStub(
                {
                    "symbol": "BTCUSDT",
                    "orderId": 10,
                    "status": "NEW",
                }
            )
        ]
    )
    client = AsterV1Client(
        api_key="key",
        signer=V1HmacSigner(api_key="key", api_secret="secret"),
        transport=transport,
    )

    await client.create_order(
        symbol="BTCUSDT", side="BUY", order_type="LIMIT", quantity="1"
    )

    request = transport.requests[0]
    assert request.method == "POST"
    assert request.path == "/fapi/v1/order"
    assert request.headers["X-MBX-APIKEY"] == "key"
    assert "signature" in request.params
    assert request.params["symbol"] == "BTCUSDT"


@pytest.mark.asyncio
async def test_v3_exchange_info_uses_market_data_auth_headers() -> None:
    transport = StubTransport(
        [ResponseStub({"timezone": "UTC", "serverTime": 1, "symbols": []})]
    )
    client = AsterV3Client(
        account="0x90f79bf6eb2c4f870365e785982e1f101e93b906",
        signer=V3EvmSigner(
            private_key="0x59c6995e998f97a5a0044976f7d7d567f2f91e6d4b8b9d43ab2c1b9e4dc2621c",
            signer="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
        ),
        transport=transport,
    )

    await client.get_exchange_info()

    request = transport.requests[0]
    assert request.method == "GET"
    assert request.path == "/fapi/v3/exchangeInfo"
    assert request.params["user"] == "0x90f79bf6eb2c4f870365e785982e1f101e93b906"
    assert request.params["signer"] == "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"
    assert request.params["nonce"]
    assert request.params["signature"].startswith("0x")


@pytest.mark.asyncio
async def test_v3_get_order_requires_order_identifier() -> None:
    client = AsterV3Client(
        account="0x90f79bf6eb2c4f870365e785982e1f101e93b906",
        signer=V3EvmSigner(
            private_key="0x59c6995e998f97a5a0044976f7d7d567f2f91e6d4b8b9d43ab2c1b9e4dc2621c",
            signer="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
        ),
        transport=StubTransport([]),
    )

    with pytest.raises(ValueError):
        await client.get_order(symbol="BTCUSDT")


@pytest.mark.asyncio
async def test_v1_market_data_responses_are_parsed_into_models() -> None:
    transport = StubTransport(
        [
            ResponseStub(
                {"timezone": "UTC", "serverTime": 1, "symbols": [{"symbol": "BTCUSDT"}]}
            ),
            ResponseStub(
                {
                    "lastUpdateId": 11,
                    "bids": [["100.0", "1.2"]],
                    "asks": [["100.5", "1.1"]],
                }
            ),
            ResponseStub(
                {
                    "symbol": "BTCUSDT",
                    "bidPrice": "100.0",
                    "bidQty": "2",
                    "askPrice": "100.1",
                    "askQty": "3",
                }
            ),
        ]
    )
    client = AsterV1Client(
        api_key="key",
        signer=V1HmacSigner(api_key="key", api_secret="secret"),
        transport=transport,
    )

    exchange_info = await client.get_exchange_info()
    order_book = await client.get_order_book("BTCUSDT", limit=20)
    book_ticker = await client.get_book_ticker("BTCUSDT")

    assert isinstance(exchange_info, ExchangeInfo)
    assert isinstance(order_book, OrderBookSnapshot)
    assert isinstance(book_ticker, BookTicker)


def test_recorded_request_exposes_default_empty_mappings() -> None:
    request = RecordedRequest(method="GET", path="/test")

    assert isinstance(request.params, Mapping)
    assert request.params == {}
    assert request.headers == {}
    assert request.json is None


def test_response_stub_allows_optional_status_code() -> None:
    stub = ResponseStub({"ok": True}, status_code=201)

    assert stub.payload["ok"] is True
    assert stub.status_code == 201
