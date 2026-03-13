"""Local order book synchronization tests."""

import pytest

from asterdex_client.models import DepthUpdateEvent, OrderBookSnapshot
from asterdex_client.orderbook import OrderBookBuilder, OrderBookOutOfSyncError


def test_orderbook_applies_snapshot_and_delta() -> None:
    book = OrderBookBuilder(symbol="BTCUSDT")
    book.apply_snapshot(
        OrderBookSnapshot(
            last_update_id=100,
            bids=[("100.0", "1.0")],
            asks=[("101.0", "2.0")],
        )
    )
    book.apply_depth_update(
        DepthUpdateEvent(
            event_type="depthUpdate",
            event_time=1,
            symbol="BTCUSDT",
            first_update_id=100,
            final_update_id=102,
            previous_final_update_id=99,
            bids=[("100.0", "1.5"), ("99.5", "3.0")],
            asks=[("101.0", "0")],
        )
    )

    state = book.snapshot()
    assert state.last_update_id == 102
    assert state.bids == [("100.0", "1.5"), ("99.5", "3.0")]
    assert state.asks == []


def test_orderbook_requires_valid_first_event_range() -> None:
    book = OrderBookBuilder(symbol="BTCUSDT")
    book.apply_snapshot(OrderBookSnapshot(last_update_id=100, bids=[], asks=[]))

    with pytest.raises(OrderBookOutOfSyncError):
        book.apply_depth_update(
            DepthUpdateEvent(
                event_type="depthUpdate",
                event_time=1,
                symbol="BTCUSDT",
                first_update_id=105,
                final_update_id=106,
                previous_final_update_id=104,
                bids=[],
                asks=[],
            )
        )


def test_orderbook_requires_contiguous_previous_update_ids() -> None:
    book = OrderBookBuilder(symbol="BTCUSDT")
    book.apply_snapshot(OrderBookSnapshot(last_update_id=100, bids=[], asks=[]))
    book.apply_depth_update(
        DepthUpdateEvent(
            event_type="depthUpdate",
            event_time=1,
            symbol="BTCUSDT",
            first_update_id=100,
            final_update_id=101,
            previous_final_update_id=99,
            bids=[],
            asks=[],
        )
    )

    with pytest.raises(OrderBookOutOfSyncError):
        book.apply_depth_update(
            DepthUpdateEvent(
                event_type="depthUpdate",
                event_time=2,
                symbol="BTCUSDT",
                first_update_id=102,
                final_update_id=103,
                previous_final_update_id=55,
                bids=[],
                asks=[],
            )
        )
