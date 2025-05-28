"""
Custom exceptions for the Virtual Try-On API.
"""
from __future__ import annotations

from typing import Any


class VirtualTryOnError(Exception):
    """Base exception for all Virtual Try-On API errors."""
    def __init__(
        self,
        message: str = "An error occurred with the Virtual Try-On API",
        code: int | None = None,
        request_id: str | None = None,
        status_code: int | None = None,
        response: Any = None,
    ) -> None:
        self.message = message
        self.code = code
        self.request_id = request_id
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)

    def __str__(self) -> str:
        msg = self.message
        if self.code is not None:
            msg = f"{self.code}: {msg}"
        if self.request_id is not None:
            msg = f"{msg} (request_id: {self.request_id})"
        return msg


class APIError(VirtualTryOnError):
    """Raised when the API returns an error response."""
    pass


class AuthenticationError(VirtualTryOnError):
    """Raised when authentication fails."""
    pass


class RateLimitError(VirtualTryOnError):
    """Raised when rate limit is exceeded."""
    pass


class TimeoutError(VirtualTryOnError):
    """Raised when a request times out."""
    pass


class ValidationError(VirtualTryOnError, ValueError):
    """Raised when input validation fails."""
    pass


class InvalidImageError(ValidationError):
    """Raised when an invalid image is provided."""
    pass


class TaskFailedError(VirtualTryOnError):
    """Raised when a task fails to complete successfully."""
    def __init__(
        self,
        message: str = "Task failed to complete successfully",
        task_id: str | None = None,
        status: str | None = None,
        status_message: str | None = None,
        **kwargs: Any,
    ) -> None:
        self.task_id = task_id
        self.status = status
        self.status_message = status_message
        if task_id:
            message = f"{message} (task_id: {task_id})"
        if status:
            message = f"{message}, status: {status}"
        if status_message:
            message = f"{message}, reason: {status_message}"
        super().__init__(message=message, **kwargs)
