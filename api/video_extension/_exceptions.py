"""
Custom exceptions for the Kling AI Video Extension API.
"""
from __future__ import annotations

from typing import Any

from .._exceptions import KlingAPIError


class VideoExtensionError(KlingAPIError):
    """Base exception for video extension related errors."""
    pass


class VideoExtensionValidationError(VideoExtensionError):
    """Raised when video extension request validation fails."""
    pass


class VideoExtensionRateLimitError(VideoExtensionError):
    """Raised when rate limit is exceeded for video extension API."""
    pass


class VideoExtensionNotFoundError(VideoExtensionError):
    """Raised when a requested video extension task is not found."""
    pass


class VideoExtensionServerError(VideoExtensionError):
    """Raised when the video extension API returns a server error."""
    pass


class VideoExtensionTimeoutError(VideoExtensionError):
    """Raised when a video extension request times out."""
    pass


class VideoExtensionAuthenticationError(VideoExtensionError):
    """Raised when authentication fails for video extension API."""
    pass


def handle_video_extension_error(error: dict[str, Any] | None = None) -> None:
    """Handle API errors and raise appropriate exceptions.

    Args:
        error: Error response from the API

    Raises:
        VideoExtensionValidationError: For validation errors (400)
        VideoExtensionAuthenticationError: For authentication errors (401, 403)
        VideoExtensionNotFoundError: For not found errors (404)
        VideoExtensionRateLimitError: For rate limit errors (429)
        VideoExtensionServerError: For server errors (5xx)
        VideoExtensionError: For other API errors
    """
    if not error:
        raise VideoExtensionError("Unknown API error occurred")

    error_code = error.get("code", -1)
    error_message = error.get("message", "Unknown error occurred")

    if error_code in (400, 422):
        raise VideoExtensionValidationError(
            f"Validation error: {error_message}", status_code=error_code
        )
    if error_code in (401, 403):
        raise VideoExtensionAuthenticationError(
            f"Authentication failed: {error_message}", status_code=error_code
        )
    if error_code == 404:
        raise VideoExtensionNotFoundError(
            f"Resource not found: {error_message}", status_code=error_code
        )
    if error_code == 429:
        raise VideoExtensionRateLimitError(
            f"Rate limit exceeded: {error_message}", status_code=error_code
        )
    if 500 <= error_code < 600:
        raise VideoExtensionServerError(
            f"Server error: {error_message}", status_code=error_code
        )
    
    raise VideoExtensionError(
        f"API error {error_code}: {error_message}", status_code=error_code
    )
