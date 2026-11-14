"""Typed errors for the Amália IAEdu client."""


class AmaliaError(Exception):
    """Base error for the Amália SDK."""


class AmaliaAuthError(AmaliaError):
    """Raised on 401/403 from the API."""


class AmaliaHTTPError(AmaliaError):
    """Raised on other non-2xx responses."""

    def __init__(self, status_code: int, body: str) -> None:
        super().__init__(f"HTTP {status_code}: {body[:500]}")
        self.status_code = status_code
        self.body = body
