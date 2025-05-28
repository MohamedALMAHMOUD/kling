"""Utility functions for the Kling AI Callback Protocol."""
import hashlib
import hmac
import json
from typing import Any, Callable, TypeVar, cast

from fastapi import Request
from pydantic import BaseModel

from ._exceptions import CallbackSecurityError

T = TypeVar('T', bound=BaseModel)


def validate_signature(
    request: Request,
    secret: str,
    header_name: str = "X-Kling-Signature",
) -> bool:
    """Validate the signature of a callback request.
    
    Args:
        request: The incoming request
        secret: The shared secret for signature verification
        header_name: The header containing the signature
        
    Returns:
        bool: True if the signature is valid, False otherwise
        
    Raises:
        CallbackSecurityError: If the signature is invalid or missing
    """
    if not secret:
        return True  # Skip validation if no secret is provided
        
    signature = request.headers.get(header_name)
    if not signature:
        raise CallbackSecurityError("Missing signature header")
    
    # Read the request body
    body = request.body()
    if not body:
        raise CallbackSecurityError("Empty request body")
    
    # Calculate the expected signature
    expected_signature = hmac.new(
        secret.encode(),
        msg=body,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    # Compare the signatures in constant time
    if not hmac.compare_digest(expected_signature, signature):
        raise CallbackSecurityError("Invalid signature")
    
    return True


def parse_and_validate(
    data: dict[str, Any],
    model: type[T],
    context: dict[str, Any] | None = None,
) -> T:
    """Parse and validate data against a Pydantic model.
    
    Args:
        data: The data to validate
        model: The Pydantic model to validate against
        context: Additional context for validation
        
    Returns:
        The validated model instance
        
    Raises:
        CallbackValidationError: If validation fails
    """
    try:
        if context:
            return model(**data, **context)
        return model(**data)
    except Exception as e:
        from ._exceptions import CallbackValidationError
        raise CallbackValidationError(
            f"Failed to validate {model.__name__}: {str(e)}",
            details={"validation_error": str(e)}
        ) from e


def create_response(
    status: str = "success",
    message: str = "",
    data: dict[str, Any] | None = None,
    status_code: int = 200,
) -> dict[str, Any]:
    """Create a standardized API response.
    
    Args:
        status: Response status (e.g., "success", "error")
        message: Human-readable message
        data: Additional response data
        status_code: HTTP status code
        
    Returns:
        dict: Standardized response dictionary
    """
    response = {
        "status": status,
        "message": message,
    }
    
    if data is not None:
        response["data"] = data
    
    return response


def async_retry(
    max_retries: int = 3,
    initial_delay: float = 0.1,
    max_delay: float = 5.0,
    backoff_factor: float = 2.0,
    exceptions: tuple[type[Exception], ...] | None = None,
):
    """Decorator for retrying async functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Factor by which the delay increases after each retry
        exceptions: Tuple of exceptions to catch and retry on
        
    Returns:
        Decorated async function with retry logic
    """
    if exceptions is None:
        exceptions = (Exception,)
    
    def decorator(func):
        import asyncio
        from functools import wraps
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        break
                        
                    # Calculate next delay with exponential backoff
                    delay = min(delay * backoff_factor, max_delay)
                    
                    # Add jitter to avoid thundering herd
                    jitter = delay * 0.1  # 10% jitter
                    actual_delay = delay + (jitter * (2 * (hash(f"{id(func)}{attempt}") / 2**64) - 1))
                    
                    # Wait before retry
                    await asyncio.sleep(actual_delay)
            
            # If we've exhausted all retries, raise the last exception
            raise last_exception  # type: ignore
            
        return wrapper
    
    return decorator
