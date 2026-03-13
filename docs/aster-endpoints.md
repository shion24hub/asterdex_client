# Aster Client Endpoint Inventory

This document defines the complete endpoint scope implemented by this project.
The scope is intentionally narrower than the full Aster API surface and is
limited to trading, user stream lifecycle, market data required for order
placement, and local order book construction.

## Sources

- v1 futures API: https://github.com/asterdex/api-docs/blob/master/aster-finance-futures-api.md
- v3 futures API: https://github.com/asterdex/api-docs/blob/master/aster-finance-futures-api-v3.md

## REST Endpoints

| Family | Method | Path | Security | Purpose | Implemented by |
| --- | --- | --- | --- | --- | --- |
| v1 | GET | `/fapi/v1/exchangeInfo` | NONE | Exchange metadata and filters | `AsterV1Client.get_exchange_info` |
| v1 | GET | `/fapi/v1/depth` | NONE | Order book snapshot for local book sync | `AsterV1Client.get_order_book` |
| v1 | GET | `/fapi/v1/ticker/bookTicker` | NONE | Best bid/ask snapshot | `AsterV1Client.get_book_ticker` |
| v1 | POST | `/fapi/v1/order` | TRADE | Place order | `AsterV1Client.create_order` |
| v1 | GET | `/fapi/v1/order` | USER_DATA | Query order by id or client id | `AsterV1Client.get_order` |
| v1 | DELETE | `/fapi/v1/order` | TRADE | Cancel order by id or client id | `AsterV1Client.cancel_order` |
| v1 | DELETE | `/fapi/v1/allOpenOrders` | TRADE | Cancel all open orders for a symbol | `AsterV1Client.cancel_all_open_orders` |
| v1 | GET | `/fapi/v1/openOrder` | USER_DATA | Query a currently open order | `AsterV1Client.get_open_order` |
| v1 | GET | `/fapi/v1/openOrders` | USER_DATA | List open orders for one symbol or all symbols | `AsterV1Client.get_open_orders` |
| v1 | GET | `/fapi/v1/allOrders` | USER_DATA | List historical orders for a symbol | `AsterV1Client.get_all_orders` |
| v1 | POST | `/fapi/v1/listenKey` | USER_STREAM | Start or extend a user stream | `AsterV1Client.start_user_stream` |
| v1 | PUT | `/fapi/v1/listenKey` | USER_STREAM | Keep a user stream alive | `AsterV1Client.keepalive_user_stream` |
| v1 | DELETE | `/fapi/v1/listenKey` | USER_STREAM | Close a user stream | `AsterV1Client.close_user_stream` |
| v3 | GET | `/fapi/v3/exchangeInfo` | MARKET_DATA | Exchange metadata and filters | `AsterV3Client.get_exchange_info` |
| v3 | GET | `/fapi/v3/depth` | MARKET_DATA | Order book snapshot for local book sync | `AsterV3Client.get_order_book` |
| v3 | GET | `/fapi/v3/ticker/bookTicker` | MARKET_DATA | Best bid/ask snapshot | `AsterV3Client.get_book_ticker` |
| v3 | POST | `/fapi/v3/order` | TRADE | Place order | `AsterV3Client.create_order` |
| v3 | GET | `/fapi/v3/order` | USER_DATA | Query order by id or client id | `AsterV3Client.get_order` |
| v3 | DELETE | `/fapi/v3/order` | TRADE | Cancel order by id or client id | `AsterV3Client.cancel_order` |
| v3 | DELETE | `/fapi/v3/allOpenOrders` | TRADE | Cancel all open orders for a symbol | `AsterV3Client.cancel_all_open_orders` |
| v3 | GET | `/fapi/v3/openOrder` | USER_DATA | Query a currently open order | `AsterV3Client.get_open_order` |
| v3 | GET | `/fapi/v3/openOrders` | USER_DATA | List open orders for one symbol or all symbols | `AsterV3Client.get_open_orders` |
| v3 | GET | `/fapi/v3/allOrders` | USER_DATA | List historical orders for a symbol | `AsterV3Client.get_all_orders` |
| v3 | POST | `/fapi/v3/listenKey` | USER_STREAM | Start or extend a user stream | `AsterV3Client.start_user_stream` |
| v3 | PUT | `/fapi/v3/listenKey` | USER_STREAM | Keep a user stream alive | `AsterV3Client.keepalive_user_stream` |
| v3 | DELETE | `/fapi/v3/listenKey` | USER_STREAM | Close a user stream | `AsterV3Client.close_user_stream` |

## WebSocket Streams

| Channel | Purpose | Implemented by |
| --- | --- | --- |
| `<symbol>@depth` | Default diff book depth stream | `AsterWsClient.subscribe_depth` |
| `<symbol>@depth@500ms` | Lower-frequency diff book depth stream | `AsterWsClient.subscribe_depth` |
| `<symbol>@depth@100ms` | Higher-frequency diff book depth stream | `AsterWsClient.subscribe_depth` |
| `<symbol>@bookTicker` | Best bid/ask stream | `AsterWsClient.subscribe_book_ticker` |
| `<listenKey>` | User data stream session | `AsterWsClient.connect_user_stream` |

## WebSocket Event Types

| Event | Purpose | Implemented by |
| --- | --- | --- |
| `depthUpdate` | Apply order book deltas | `DepthUpdateEvent` + `OrderBookBuilder` |
| `bookTicker` | Best bid/ask updates | `BookTickerEvent` |
| `ACCOUNT_UPDATE` | Balance and position updates | `AccountUpdateEvent` |
| `ORDER_TRADE_UPDATE` | Order lifecycle and trade fills | `OrderTradeUpdateEvent` |
| `listenKeyExpired` | Stream expiration notification | `ListenKeyExpiredEvent` |

## Out of Scope

The following Aster endpoints are intentionally not implemented in this project:

- trades, aggregate trades, klines, mark price, funding, and ticker families
- leverage, margin type, position mode, multi-asset mode, and transfer endpoints
- batch order endpoints
- account balance, account information, position risk, income, and commission endpoints
