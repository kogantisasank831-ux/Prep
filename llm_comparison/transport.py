from __future__ import annotations

from typing import Mapping, Protocol, Self, cast
from urllib.error import HTTPError
from urllib.request import (
    HTTPRedirectHandler,
    OpenerDirector,
    ProxyHandler,
    Request,
    build_opener,
)

from llm_comparison.ports import HttpResponse


MAX_RESPONSE_BYTES = 4 * 1024 * 1024


class RedirectRejectedError(OSError):
    """A localhost response attempted to redirect the client."""


class _ReadableResponse(Protocol):
    status: int
    headers: object

    def read(self, size: int) -> bytes: ...

    def __enter__(self) -> Self: ...

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None: ...


class _RejectRedirects(HTTPRedirectHandler):
    def redirect_request(
        self,
        req: Request,
        fp: object,
        code: int,
        msg: str,
        headers: object,
        newurl: str,
    ) -> None:
        return None


class LocalOpener:
    proxies_disabled = True
    redirects_disabled = True

    def __init__(self, director: OpenerDirector) -> None:
        self._director = director

    def open(self, request: Request, *, timeout: float) -> _ReadableResponse:
        return cast(_ReadableResponse, self._director.open(request, timeout=timeout))


def build_local_opener() -> LocalOpener:
    """Build an opener that ignores ambient proxies and never follows redirects."""
    return LocalOpener(build_opener(ProxyHandler({}), _RejectRedirects()))


class UrllibHttpTransport:
    def __init__(self, *, opener: LocalOpener | None = None) -> None:
        self._opener = opener if opener is not None else build_local_opener()

    def request(
        self,
        *,
        method: str,
        url: str,
        headers: Mapping[str, str],
        body: bytes | None,
        timeout_seconds: float,
    ) -> HttpResponse:
        request = Request(url=url, data=body, headers=dict(headers), method=method)
        try:
            with self._opener.open(request, timeout=timeout_seconds) as response:
                if 300 <= response.status < 400:
                    raise RedirectRejectedError("redirect responses are prohibited")
                return HttpResponse(
                    status_code=response.status,
                    body=self._bounded_read(response),
                    headers=dict(cast(Mapping[str, str], response.headers).items()),
                )
        except HTTPError as exc:
            if 300 <= exc.code < 400:
                raise RedirectRejectedError(
                    "redirect responses are prohibited"
                ) from exc
            return HttpResponse(
                status_code=exc.code,
                body=self._bounded_read(exc),
                headers=dict(exc.headers.items()),
            )

    @staticmethod
    def _bounded_read(response: object) -> bytes:
        headers = getattr(response, "headers", None)
        get_all = getattr(headers, "get_all", None)
        declared_values: list[str] = []
        if callable(get_all):
            raw_values: object = get_all("Content-Length", [])
            if isinstance(raw_values, list) and all(
                isinstance(item, str) for item in raw_values
            ):
                declared_values = raw_values
        for raw_value in declared_values:
            parts = [part.strip() for part in raw_value.split(",")]
            if not parts or any(not part.isdecimal() for part in parts):
                raise OSError("invalid Content-Length")
            lengths = {int(part) for part in parts}
            if len(lengths) != 1:
                raise OSError("conflicting Content-Length")
            if next(iter(lengths)) > MAX_RESPONSE_BYTES:
                raise OSError("response body exceeds configured limit")
        read = getattr(response, "read", None)
        if not callable(read):
            raise OSError("response does not provide a readable body")
        body: object = read(MAX_RESPONSE_BYTES + 1)
        if not isinstance(body, bytes):
            raise OSError("response body must be bytes")
        if len(body) > MAX_RESPONSE_BYTES:
            raise OSError("response body exceeds configured limit")
        return body
