"""
Custom exceptions for Kling AI Multi-Image to Video API.
"""


class MultiImageToVideoError(Exception):
    """Base exception for all Multi-Image to Video API errors."""


class MultiImageToVideoValidationError(MultiImageToVideoError, ValueError):
    """Raised when input validation fails."""


class MultiImageToVideoAPIError(MultiImageToVideoError):
    """Raised when the Kling AI API returns an error response."""

    def __init__(self, status_code: int, message: str, request_id: str | None = None):
        self.status_code = status_code
        self.message = message
        self.request_id = request_id
        super().__init__(f"API Error {status_code}: {message} (Request ID: {request_id or 'N/A'})")


class MultiImageToVideoRateLimitError(MultiImageToVideoAPIError):
    """Raised when rate limit is exceeded."""


class MultiImageToVideoAuthenticationError(MultiImageToVideoAPIError):
    """Raised when authentication fails."""


class MultiImageToVideoNotFoundError(MultiImageToVideoAPIError):
    """Raised when a requested resource is not found."""


class MultiImageToVideoServerError(MultiImageToVideoAPIError):
    """Raised when the server encounters an error."""


class MultiImageToVideoTimeoutError(MultiImageToVideoError, TimeoutError):
    """Raised when a request times out."""


class MultiImageToVideoTaskError(MultiImageToVideoError):
    """Raised when a task fails to complete successfully."""

    def __init__(self, task_id: str, status: str, message: str | None = None):
        self.task_id = task_id
        self.status = status
        self.message = message or f"Task {task_id} failed with status: {status}"
        super().__init__(self.message)


def handle_api_error(error: Exception) -> MultiImageToVideoError:
    """Convert HTTP and API errors into appropriate custom exceptions.

    Args:
        error: The original exception that was raised

    Returns:
        An appropriate MultiImageToVideoError subclass
    """
    import httpx
    from httpx import HTTPStatusError

    if isinstance(error, MultiImageToVideoError):
        return error

    if isinstance(error, HTTPStatusError):
        status_code = error.response.status_code
        try:
            response_data = error.response.json()
            message = response_data.get("message", str(error))
            request_id = response_data.get("request_id")
        except Exception:
            message = str(error)
            request_id = None

        if status_code == 401:
            return MultiImageToVideoAuthenticationError(status_code, message, request_id)
        if status_code == 404:
            return MultiImageToVideoNotFoundError(status_code, message, request_id)
        if status_code == 429:
            return MultiImageToVideoRateLimitError(status_code, message, request_id)
        if 500 <= status_code < 600:
            return MultiImageToVideoServerError(status_code, message, request_id)
        return MultiImageToVideoAPIError(status_code, message, request_id)

    if isinstance(error, httpx.TimeoutException | TimeoutError):
        return MultiImageToVideoTimeoutError("Request timed out")

    if isinstance(error, httpx.RequestError):
        return MultiImageToVideoAPIError(0, f"Request failed: {error}")

    return MultiImageToVideoError(f"An unexpected error occurred: {error}")

