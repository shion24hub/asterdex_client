"""Submit a market order through the Aster v3 API.

Usage:
    uv run python examples/check_create_market_order.py \
        --symbol BTCUSDT \
        --side BUY \
        --quantity 0.001 \
        --address 0xYourAccountAddress \
        --private-key 0xYourPrivateKey
"""

from __future__ import annotations

import argparse
import asyncio
import json
from typing import Any

from eth_account import Account

from asterdex_client import AsterV3Client, V3EvmSigner


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the market order example.

    Returns:
        Parsed CLI namespace.
    """

    parser = argparse.ArgumentParser(description="Submit an Aster market order.")
    parser.add_argument(
        "--symbol", required=True, help="Market symbol such as BTCUSDT."
    )
    parser.add_argument(
        "--side",
        required=True,
        choices=("BUY", "SELL"),
        help="Order side.",
    )
    parser.add_argument(
        "--quantity",
        required=True,
        help="Order quantity, sent as-is to the API.",
    )
    parser.add_argument(
        "--address",
        required=True,
        help="Aster account address used as the API user address.",
    )
    parser.add_argument(
        "--private-key",
        required=True,
        help="Hex private key used to sign the request.",
    )
    return parser.parse_args()


async def submit_market_order(args: argparse.Namespace) -> dict[str, Any]:
    """Create a market order and return the raw normalized payload.

    Args:
        args: Parsed CLI arguments.

    Returns:
        The normalized order payload as a dictionary.
    """

    signer_address = Account.from_key(args.private_key).address
    signer = V3EvmSigner(private_key=args.private_key, signer=signer_address)
    client = AsterV3Client(account=args.address, signer=signer)

    order = await client.create_order(
        symbol=args.symbol,
        side=args.side,
        order_type="MARKET",
        quantity=args.quantity,
    )
    return {
        "symbol": order.symbol,
        "orderId": order.order_id,
        "status": order.status,
        "raw": order.raw,
    }


def main() -> None:
    """Run the CLI example."""

    args = parse_args()
    result = asyncio.run(submit_market_order(args))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
