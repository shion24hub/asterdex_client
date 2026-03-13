# Local Order Book Synchronization

This client follows the official Aster local order book procedure described in
the futures API documentation for both v1 and v3.

## Procedure

1. Open a diff depth stream for the symbol on `wss://fstream.asterdex.com`.
2. Buffer incoming depth events in arrival order.
3. Fetch a REST snapshot from `/fapi/v3/depth` or `/fapi/v1/depth`.
4. Drop buffered events where `u < lastUpdateId`.
5. The first applied event must satisfy `U <= lastUpdateId <= u`.
6. Each subsequent event must satisfy `pu == previous.u`.
7. Every quantity in the stream is absolute, not a delta.
8. A quantity of `0` removes the price level.
9. Removing a price level that is not present locally is valid and should be ignored.

## Client State Machine

- `initialized`: No snapshot has been applied yet.
- `synced`: Snapshot applied and stream sequence is contiguous.
- `resync_required`: Sequence gap or invalid first event detected. The caller must
  fetch a new snapshot and replay buffered events again.

## Implementation Rules

- Use string price and quantity values internally to avoid lossy float handling.
- Track bids and asks independently, keyed by price string.
- Publish `last_update_id` after every applied diff event.
- Expose an explicit method to apply a snapshot and another to apply one stream
  event so callers can control resync behavior.
