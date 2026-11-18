"""Exception hierarchy."""


class AtmError(Exception):
    """Base class for all errors raised by this library."""


class AtmBlockedError(AtmError):
    """The edge/bot protection (Akamai) rejected the request (HTTP 403)."""


class AtmNotFoundError(AtmError):
    """The requested resource (line, stop, place) does not exist."""


class AtmApiError(AtmError):
    """The upstream service returned an unexpected status or payload."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
