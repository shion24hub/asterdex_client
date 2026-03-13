"""Signing tests for Aster API families."""

import hashlib
import hmac

from asterdex_client.auth import V1HmacSigner, V3EvmSigner


def test_v1_hmac_signer_generates_expected_signature() -> None:
    signer = V1HmacSigner(api_key="key", api_secret="secret")
    payload = "symbol=BTCUSDT&side=BUY&type=LIMIT&timestamp=1700000000000"

    assert (
        signer.sign_payload(payload)
        == hmac.new(
            b"secret",
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
    )


def test_v3_evm_signer_is_deterministic_for_same_payload() -> None:
    signer = V3EvmSigner(
        private_key="0x59c6995e998f97a5a0044976f7d7d567f2f91e6d4b8b9d43ab2c1b9e4dc2621c",
        signer="0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
    )

    first = signer.sign_action(
        instruction="order",
        account="0x90f79bf6eb2c4f870365e785982e1f101e93b906",
        user="0x15d34aaf54267db7d7c367839aaf71a00a2c6a65",
        nonce=1700000000000000,
    )
    second = signer.sign_action(
        instruction="order",
        account="0x90f79bf6eb2c4f870365e785982e1f101e93b906",
        user="0x15d34aaf54267db7d7c367839aaf71a00a2c6a65",
        nonce=1700000000000000,
    )

    assert first == second
    assert first.startswith("0x")
    assert len(first) == 132
