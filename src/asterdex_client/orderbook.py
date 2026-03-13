"""Local order book construction."""

from __future__ import annotations

from dataclasses import dataclass, field

from asterdex_client.models import DepthUpdateEvent, OrderBookSnapshot


class OrderBookOutOfSyncError(RuntimeError):
    """Raised when the local order book can no longer be trusted."""


@dataclass(slots=True)
class OrderBookBuilder:
    """Build and maintain a local order book from snapshot and diff events.

    Args:
        symbol: Symbol associated with the book.
    """

    symbol: str
    _bids: dict[str, str] = field(init=False, default_factory=dict)
    _asks: dict[str, str] = field(init=False, default_factory=dict)
    _last_update_id: int | None = field(init=False, default=None)
    _stream_update_id: int | None = field(init=False, default=None)

    def apply_snapshot(self, snapshot: OrderBookSnapshot) -> None:
        """Replace the current book with a fresh REST snapshot.

        Args:
            snapshot: Snapshot to install.
        """

        self._bids = {price: qty for price, qty in snapshot.bids}
        self._asks = {price: qty for price, qty in snapshot.asks}
        self._last_update_id = snapshot.last_update_id
        self._stream_update_id = None

    def apply_depth_update(self, event: DepthUpdateEvent) -> None:
        """Apply one diff depth event.

        Args:
            event: Stream delta to apply.

        Raises:
            OrderBookOutOfSyncError: Raised when sequence continuity is broken.
        """

        if self._last_update_id is None:
            raise OrderBookOutOfSyncError("Snapshot must be applied before deltas")
        if self._stream_update_id is None:
            if not (
                event.first_update_id <= self._last_update_id <= event.final_update_id
            ):
                raise OrderBookOutOfSyncError("First event does not bridge snapshot")
        elif event.previous_final_update_id != self._stream_update_id:
            raise OrderBookOutOfSyncError("Depth stream gap detected")

        self._apply_levels(self._bids, event.bids)
        self._apply_levels(self._asks, event.asks)
        self._stream_update_id = event.final_update_id
        self._last_update_id = event.final_update_id

    def snapshot(self) -> OrderBookSnapshot:
        """Return the current in-memory state as a snapshot."""

        if self._last_update_id is None:
            raise OrderBookOutOfSyncError("No snapshot available")
        return OrderBookSnapshot(
            last_update_id=self._last_update_id,
            bids=sorted(
                self._bids.items(), key=lambda item: float(item[0]), reverse=True
            ),
            asks=sorted(self._asks.items(), key=lambda item: float(item[0])),
        )

    @staticmethod
    def _apply_levels(levels: dict[str, str], updates: list[tuple[str, str]]) -> None:
        for price, quantity in updates:
            if quantity == "0":
                levels.pop(price, None)
            else:
                levels[price] = quantity
