"""
Custom exceptions for the Kling AI Callback Protocol.
"""
from typing import Any, Optional


class CallbackError(Exception):
    """Base exception for all callback-related errors."""
    def __init__(self, message: str, status_code: int = 400, details: Optional[dict[str, Any]] = None):
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class CallbackValidationError(CallbackError):
    """Raised when callback data validation fails."""
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=f"Callback validation failed: {message}",
            status_code=422,
            details=details or {}
        )


class CallbackProcessingError(CallbackError):
    """Raised when there's an error processing a callback."""
    def __init__(self, message: str, status_code: int = 500, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=f"Error processing callback: {message}",
            status_code=status_code,
            details=details or {}
        )


class CallbackSecurityError(CallbackError):
    """Raised when there's a security-related issue with a callback."""
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=f"Security error in callback: {message}",
            status_code=403,
            details=details or {}
        )


class CallbackNotFoundError(CallbackError):
    """Raised when a referenced task or resource is not found."""
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} not found: {resource_id}",
            status_code=404,
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


class CallbackRateLimitError(CallbackError):
    """Raised when rate limits are exceeded for callbacks."""
    def __init__(self, retry_after: Optional[int] = None):
        message = "Rate limit exceeded for callbacks"
        if retry_after:
            message += f", please retry after {retry_after} seconds"
        
        details = {"retry_after": retry_after} if retry_after else {}
        
        super().__init__(
            message=message,
            status_code=429,
            details=details
        )
