"""
Custom exceptions for the Kling AI Text-to-Video API client.
"""
from __future__ import annotations

from typing import Any


class KlingAPIError(Exception):
    """Base exception for all Kling AI API errors."""

    def __init__(
        self,
        message: str = "An error occurred with the Kling AI API",
        status_code: int | None = None,
        response: Any | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class APIRequestError(KlingAPIError):
    """Raised when an API request fails."""

    def __init__(
        self,
        message: str = "Failed to make request to Kling AI API",
        status_code: int | None = None,
        response: Any | None = None,
    ) -> None:
        super().__init__(message, status_code, response)


class AuthenticationError(KlingAPIError):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed. Please check your API key.",
        status_code: int | None = 401,
        response: Any | None = None,
    ) -> None:
        super().__init__(message, status_code, response)


class RateLimitError(KlingAPIError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please try again later.",
        status_code: int | None = 429,
        response: Any | None = None,
        retry_after: int | None = None,
    ) -> None:
        self.retry_after = retry_after
        super().__init__(message, status_code, response)


class ValidationError(KlingAPIError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str = "Invalid request parameters",
        status_code: int | None = 400,
        response: Any | None = None,
        errors: list[dict[str, Any]] | None = None,
    ) -> None:
        self.errors = errors or []
        super().__init__(message, status_code, response)


class NotFoundError(KlingAPIError):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        message: str = "The requested resource was not found",
        status_code: int | None = 404,
        response: Any | None = None,
    ) -> None:
        super().__init__(message, status_code, response)


class ServerError(KlingAPIError):
    """Raised when the server encounters an error."""

    def __init__(
        self,
        message: str = "An unexpected server error occurred",
        status_code: int | None = 500,
        response: Any | None = None,
    ) -> None:
        super().__init__(message, status_code, response)


class TaskFailedError(KlingAPIError):
    """Raised when a task fails to complete successfully."""

    def __init__(
        self,
        message: str = "Task failed to complete successfully",
        status_code: int | None = None,
        response: Any | None = None,
        task_id: str | None = None,
        task_status: str | None = None,
    ) -> None:
        self.task_id = task_id
        self.task_status = task_status
        super().__init__(message, status_code, response)


class TimeoutError(KlingAPIError):
    """Raised when a request times out."""

    def __init__(
        self,
        message: str = "Request timed out. Please try again.",
        status_code: int | None = 408,
        response: Any | None = None,
    ) -> None:
        super().__init__(message, status_code, response)


def handle_api_error(
    error: Exception,
    default_message: str = "An error occurred with the Kling AI API",
) -> KlingAPIError:
    """
    Convert various exceptions into KlingAPIError instances.
    
    Args:
        error: The original exception
        default_message: Default message if no specific handler matches
        
    Returns:
        An appropriate KlingAPIError instance
    """
    if isinstance(error, KlingAPIError):
        return error

    if hasattr(error, "status_code"):
        status_code = error.status_code  # type: ignore[attr-defined]
        response = getattr(error, "response", None)
        
        if status_code == 401:
            return AuthenticationError(response=response)
        elif status_code == 404:
            return NotFoundError(response=response)
        elif status_code == 429:
            retry_after = getattr(error, "response", {}).get("retry_after")
            return RateLimitError(response=response, retry_after=retry_after)
        elif 400 <= status_code < 500:
            return ValidationError(
                message=getattr(error, "message", "Invalid request"),
                status_code=status_code,
                response=response,
            )
        elif status_code >= 500:
            return ServerError(
                message=getattr(error, "message", "Server error"),
                status_code=status_code,
                response=response,
            )
    
    # Handle specific exception types
    if isinstance(error, TimeoutError):
        return TimeoutError()

    # Default case
    return KlingAPIError(
        message=str(error) or default_message,
        response=getattr(error, "response", None),
    )
