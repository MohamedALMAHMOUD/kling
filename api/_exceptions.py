from typing import Any


class KlingAPIError(Exception):
    """Base exception for all Kling API errors.
    
    Args:
        message: Error message
        status_code: HTTP status code if applicable
        details: Additional error details
    """
    def __init__(
        self,
        message: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or "An error occurred with the Kling API"
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.status_code:
            return f"{self.message} (status: {self.status_code})"
        return self.message


