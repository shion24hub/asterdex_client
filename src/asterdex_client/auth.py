"""Authentication helpers for Aster API families."""

from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass
from typing import Final, cast

from eth_account import Account
from eth_account.messages import encode_typed_data
from eth_utils import to_checksum_address

ASTER_SIGN_DOMAIN: Final[dict[str, object]] = {
    "name": "AsterSignTransaction",
    "version": "1",
    "chainId": 1666600000,
    "verifyingContract": "0x0000000000000000000000000000000000000000",
}


@dataclass(slots=True, frozen=True)
class V1HmacSigner:
    """Create v1 HMAC signatures for signed REST requests.

    Args:
        api_key: Public API key.
        api_secret: Secret used for HMAC-SHA256 signing.
    """

    api_key: str
    api_secret: str

    def sign_payload(self, payload: str) -> str:
        """Return a hex-encoded HMAC-SHA256 signature.

        Args:
            payload: Query string payload to sign.

        Returns:
            Lowercase hex signature.
        """

        return hmac.new(
            self.api_secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    def current_timestamp_ms() -> int:
        """Return the current UNIX time in milliseconds."""

        return int(time.time() * 1000)


@dataclass(slots=True, frozen=True)
class V3EvmSigner:
    """Create v3 EIP-712 signatures for authenticated requests.

    Args:
        private_key: Hex private key used for signing.
        signer: Externally visible signer address.
    """

    private_key: str
    signer: str

    def sign_action(
        self,
        *,
        instruction: str,
        account: str,
        user: str,
        nonce: int,
    ) -> str:
        """Return an EIP-712 signature for an Aster action.

        Args:
            instruction: Action identifier such as ``order`` or ``market_data``.
            account: Wallet address owning the account.
            user: User address sent to the API.
            nonce: Microsecond nonce required by the API.

        Returns:
            Hex-encoded ``0x``-prefixed signature.
        """

        message = encode_typed_data(
            full_message={
                "types": {
                    "EIP712Domain": [
                        {"name": "name", "type": "string"},
                        {"name": "version", "type": "string"},
                        {"name": "chainId", "type": "uint256"},
                        {"name": "verifyingContract", "type": "address"},
                    ],
                    "aster": [
                        {"name": "action", "type": "string"},
                        {"name": "account", "type": "address"},
                        {"name": "user", "type": "address"},
                        {"name": "nonce", "type": "uint64"},
                    ],
                },
                "primaryType": "aster",
                "domain": ASTER_SIGN_DOMAIN,
                "message": {
                    "action": instruction,
                    "account": to_checksum_address(account),
                    "user": to_checksum_address(user),
                    "nonce": nonce,
                },
            }
        )
        signed = Account.sign_message(message, private_key=self.private_key)
        return cast(str, signed.signature.to_0x_hex())

    @staticmethod
    def current_nonce_us() -> int:
        """Return the current UNIX time in microseconds."""

        return int(time.time() * 1_000_000)
