"""Minimal async client for Aster perpetual futures APIs."""

from asterdex_client.auth import V1HmacSigner, V3EvmSigner
from asterdex_client.clients import AsterClient, AsterV1Client, AsterV3Client
from asterdex_client.orderbook import OrderBookBuilder, OrderBookOutOfSyncError
from asterdex_client.ws import AsterWsClient

__all__ = [
    "AsterClient",
    "AsterV1Client",
    "AsterV3Client",
    "AsterWsClient",
    "OrderBookBuilder",
    "OrderBookOutOfSyncError",
    "V1HmacSigner",
    "V3EvmSigner",
]


def main() -> None:
    """Entry point for the console script."""

    print("asterdex-client")
