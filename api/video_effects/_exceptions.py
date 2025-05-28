"""Exceptions for the Kling AI Video Effects API client."""
from __future__ import annotations

from typing import Any


class VideoEffectsError(Exception):
    """Base exception for all video effects API errors."""
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        details = f" - {self.details}" if self.details else ""
        return f"{self.message}{details}"


class VideoEffectsValidationError(VideoEffectsError):
    """Raised when request validation fails."""
    pass


class VideoEffectsRateLimitError(VideoEffectsError):
    """Raised when rate limit is exceeded."""
    def __init__(self, retry_after: int | None = None, **kwargs: Any):
        details = kwargs.pop("details", {})
        if retry_after is not None:
            details["retry_after"] = retry_after
        super().__init__("Rate limit exceeded", details=details, **kwargs)


class VideoEffectsNotFoundError(VideoEffectsError):
    """Raised when a requested resource is not found."""
    pass


class VideoEffectsUnauthorizedError(VideoEffectsError):
    """Raised when authentication fails or access is denied."""
    pass


class VideoEffectsServerError(VideoEffectsError):
    """Raised when the server encounters an error."""
    pass


class VideoEffectsTimeoutError(VideoEffectsError):
    """Raised when a request times out."""
    pass


class VideoEffectsConnectionError(VideoEffectsError):
    """Raised when a connection to the API fails."""
    pass


def map_http_error(status_code: int, error_data: dict[str, Any] | None = None) -> VideoEffectsError:
    """Map HTTP status code to an appropriate exception.
    
    Args:
        status_code: HTTP status code
        error_data: Optional error details from the response
        
    Returns:
        An appropriate VideoEffectsError subclass
    """
    error_data = error_data or {}
    message = error_data.get("message", "An error occurred")
    
    if status_code == 400:
        return VideoEffectsValidationError(message, details=error_data)
    elif status_code == 401:
        return VideoEffectsUnauthorizedError(message, details=error_data)
    elif status_code == 404:
        return VideoEffectsNotFoundError(message, details=error_data)
    elif status_code == 429:
        retry_after = error_data.get("retry_after")
        return VideoEffectsRateLimitError(retry_after=retry_after, details=error_data)
    elif 500 <= status_code < 600:
        return VideoEffectsServerError(message, details=error_data)
    else:
        return VideoEffectsError(message, details=error_data)
