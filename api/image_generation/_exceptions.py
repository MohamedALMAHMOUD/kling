"""Custom exceptions for the Kling AI Image Generation API client."""

from typing import Any


class KlingAIError(Exception):
    """Base exception for all Kling AI API errors."""
    
    def __init__(
        self,
        message: str = "An error occurred with the Kling AI API",
        code: int | None = None,
        request_id: str | None = None,
        response: Any = None,
    ) -> None:
        """Initialize the exception.
        
        Args:
            message: Human-readable error message.
            code: Error code from the API.
            request_id: Unique identifier for the request.
            response: The full response object from the API.
        """
        self.message = message
        self.code = code
        self.request_id = request_id
        self.response = response
        super().__init__(self.message)


class APIError(KlingAIError):
    """Raised when the API returns an error response."""
    pass


class AuthenticationError(KlingAIError):
    """Raised when authentication fails."""
    pass


class RateLimitError(KlingAIError):
    """Raised when the rate limit is exceeded."""
    pass


class ValidationError(KlingAIError):
    """Raised when input validation fails."""
    pass


class TimeoutError(KlingAIError):
    """Raised when a request times out."""
    pass


class ServiceUnavailableError(KlingAIError):
    """Raised when the service is temporarily unavailable."""
    pass


def handle_api_error(
    response_data: dict[str, Any],
    status_code: int | None = None,
) -> KlingAIError:
    """Create an appropriate exception based on the API response.
    
    Args:
        response_data: The JSON response from the API.
        status_code: The HTTP status code.
        
    Returns:
        An appropriate exception instance.
    """
    error_code = response_data.get("code", 0)
    message = response_data.get("message", "An unknown error occurred")
    request_id = response_data.get("request_id")
    
    if status_code == 401:
        return AuthenticationError(
            message=f"Authentication failed: {message}",
            code=error_code,
            request_id=request_id,
            response=response_data,
        )
    elif status_code == 429:
        return RateLimitError(
            message=f"Rate limit exceeded: {message}",
            code=error_code,
            request_id=request_id,
            response=response_data,
        )
    elif status_code == 503:
        return ServiceUnavailableError(
            message=f"Service unavailable: {message}",
            code=error_code,
            request_id=request_id,
            response=response_data,
        )
    elif 400 <= status_code < 500:
        return ValidationError(
            message=f"Invalid request: {message}",
            code=error_code,
            request_id=request_id,
            response=response_data,
        )
    else:
        return APIError(
            message=f"API error: {message}",
            code=error_code,
            request_id=request_id,
            response=response_data,
        )
