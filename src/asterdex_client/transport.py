"""Transport primitives for Aster REST clients."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

import httpx


@dataclass(slots=True, frozen=True)
class RecordedRequest:
    """Record a REST request for testing.

    Args:
        method: HTTP method.
        path: Request path.
        params: Query string parameters.
        headers: Request headers.
        json: Optional JSON body.
        data: Optional form body.
    """

    method: str
    path: str
    params: Mapping[str, str] = field(default_factory=dict)
    headers: Mapping[str, str] = field(default_factory=dict)
    json: dict[str, Any] | None = None
    data: Mapping[str, str] | None = None


@dataclass(slots=True, frozen=True)
class ResponseStub:
    """Stub response for tests.

    Args:
        payload: Response payload.
        status_code: HTTP status code to simulate.
    """

    payload: dict[str, Any] | list[dict[str, Any]]
    status_code: int = 200


class AsterHttpError(RuntimeError):
    """Raised when the API returns an error response."""

    def __init__(self, status_code: int, payload: Any) -> None:
        super().__init__(f"Aster API error {status_code}: {payload}")
        self.status_code = status_code
        self.payload = payload


class AbstractTransport:
    """Async transport interface used by REST clients."""

    async def request(
        self,
        *,
        method: str,
        path: str,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        json: dict[str, Any] | None = None,
        data: Mapping[str, str] | None = None,
    ) -> Any:
        """Perform an HTTP request."""

        raise NotImplementedError


class HttpxTransport(AbstractTransport):
    """Production transport backed by ``httpx.AsyncClient``.

    Args:
        base_url: API base URL.
        timeout: Request timeout in seconds.
        client: Optional preconfigured async client.
    """

    def __init__(
        self,
        *,
        base_url: str,
        timeout: float = 10.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._client = client or httpx.AsyncClient(base_url=base_url, timeout=timeout)
        self._owns_client = client is None

    async def request(
        self,
        *,
        method: str,
        path: str,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        json: dict[str, Any] | None = None,
        data: Mapping[str, str] | None = None,
    ) -> Any:
        """Perform an HTTP request and return the decoded JSON payload."""

        response = await self._client.request(
            method=method,
            url=path,
            params=params,
            headers=headers,
            json=json,
            data=data,
        )
        payload = response.json()
        if response.status_code >= 400:
            raise AsterHttpError(response.status_code, payload)
        return payload

    async def aclose(self) -> None:
        """Close the underlying client if this transport created it."""

        if self._owns_client:
            await self._client.aclose()


class StubTransport(AbstractTransport):
    """Record requests and return predefined responses for tests.

    Args:
        responses: Sequence of stub responses returned in order.
    """

    def __init__(self, responses: Sequence[ResponseStub]) -> None:
        self._responses = list(responses)
        self.requests: list[RecordedRequest] = []

    async def request(
        self,
        *,
        method: str,
        path: str,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        json: dict[str, Any] | None = None,
        data: Mapping[str, str] | None = None,
    ) -> Any:
        """Record a request and return the next stub response."""

        self.requests.append(
            RecordedRequest(
                method=method,
                path=path,
                params=dict(params or {}),
                headers=dict(headers or {}),
                json=json,
                data=dict(data) if data is not None else None,
            )
        )
        if not self._responses:
            raise AssertionError("No stub responses remaining")
        response = self._responses.pop(0)
        if response.status_code >= 400:
            raise AsterHttpError(response.status_code, response.payload)
        return response.payload
