"""Exceptions for the Kling AI Lip Sync API client."""
from __future__ import annotations

from typing import Any


class LipSyncError(Exception):
    """Base exception for all Lip Sync API errors."""

    def __init__(self, message: str, status_code: int | None = None, details: Any = None):
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class LipSyncValidationError(LipSyncError):
    """Raised when request validation fails."""
    status_code = 400


class LipSyncAuthenticationError(LipSyncError):
    """Raised when authentication fails."""
    status_code = 401


class LipSyncPermissionError(LipSyncError):
    """Raised when the API key doesn't have sufficient permissions."""
    status_code = 403


class LipSyncNotFoundError(LipSyncError):
    """Raised when a requested resource is not found."""
    status_code = 404


class LipSyncRateLimitError(LipSyncError):
    """Raised when the rate limit is exceeded."""
    status_code = 429


class LipSyncServerError(LipSyncError):
    """Raised when the server encounters an error."""
    status_code = 500


class LipSyncTimeoutError(LipSyncError):
    """Raised when a request times out."""
    status_code = 504


def handle_lip_sync_error(response: dict[str, Any]) -> None:
    """Handle API errors and raise appropriate exceptions.
    
    Args:
        response: The error response from the API
        
    Raises:
        LipSyncError: The appropriate exception for the error
    """
    error_code = response.get("code", "unknown")
    error_msg = response.get("message", "An unknown error occurred")
    error_details = response.get("details", {})
    
    error_map = {
        400: LipSyncValidationError,
        401: LipSyncAuthenticationError,
        403: LipSyncPermissionError,
        404: LipSyncNotFoundError,
        429: LipSyncRateLimitError,
        500: LipSyncServerError,
        504: LipSyncTimeoutError,
    }
    
    exception_class = error_map.get(response.get("status_code"), LipSyncError)
    raise exception_class(
        message=f"{error_code}: {error_msg}",
        status_code=response.get("status_code"),
        details=error_details,
    )
