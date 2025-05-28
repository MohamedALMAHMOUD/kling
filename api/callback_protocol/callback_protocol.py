"""
Kling AI Callback Protocol API.

This module provides functionality to handle Kling AI's asynchronous task callbacks,
including validation, processing, and response generation.
"""
from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any, TypeVar

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, ValidationError

from . import _exceptions as exc
from . import _requests as models
from . import _responses as response_models
from ._utils import validate_signature as _validate_signature

# Re-export public types and models
__all__ = [
    # Router
    "router",
    # Models
    "CallbackRequest",
    "TaskStatus",
    "ParentVideo",
    "TaskInfo",
    "ImageResult",
    "VideoResult",
    "TaskResult",
    "CallbackAckResponse",
    "CallbackValidationErrorResponse",
    "CallbackProcessingResponse",
    # Exceptions
    "CallbackError",
    "CallbackValidationError",
    "CallbackProcessingError",
    "CallbackSecurityError",
    "CallbackNotFoundError",
    "CallbackRateLimitError",
    # Functions
    "register_callback_handler",
    "verify_callback_signature",
]

# Type aliases
T = TypeVar("T", bound=BaseModel)
CallbackHandler = Callable[[models.CallbackRequest], None]  # noqa: UP007

# Create API router
router = APIRouter(
    prefix="/callbacks",
    tags=["callbacks"],
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Bad Request"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden"},
        status.HTTP_404_NOT_FOUND: {"description": "Not Found"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation Error"},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Too Many Requests"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error"},
    },
)

# Global callback handler
_callback_handler: CallbackHandler | None = None

# Re-export models for easier access
CallbackRequest = models.CallbackRequest
TaskStatus = models.TaskStatus
ParentVideo = models.ParentVideo
TaskInfo = models.TaskInfo
ImageResult = models.ImageResult
VideoResult = models.VideoResult
TaskResult = models.TaskResult
CallbackAckResponse = response_models.CallbackAckResponse
CallbackValidationErrorResponse = response_models.CallbackValidationErrorResponse
CallbackProcessingResponse = response_models.CallbackProcessingResponse

# Re-export exceptions
CallbackError = exc.CallbackError
CallbackValidationError = exc.CallbackValidationError
CallbackProcessingError = exc.CallbackProcessingError
CallbackSecurityError = exc.CallbackSecurityError
CallbackNotFoundError = exc.CallbackNotFoundError
CallbackRateLimitError = exc.CallbackRateLimitError


def register_callback_handler(handler: CallbackHandler) -> None:
    """Register a callback handler function that will be called for each valid callback.
    
    Args:
        handler: A callable that takes a CallbackRequest and returns None.
                This will be called asynchronously for each valid callback.
    
    Example:
        ```python
        from kling_ai.api.callback_protocol import register_callback_handler, CallbackRequest
        
        async def handle_callback(callback: CallbackRequest) -> None:
            print(f"Received callback for task {callback.task_id}")
            print(f"Status: {callback.task_status}")
            
            if callback.task_status == "succeed" and callback.task_result:
                print("Generated media:")
                if callback.task_result.images:
                    for img in callback.task_result.images:
                        print(f"  - Image {img.index}: {img.url}")
                if callback.task_result.videos:
                    for vid in callback.task_result.videos:
                        print(f"  - Video {vid.id}: {vid.url} ({vid.duration}s)")
        
        # Register the handler
        register_callback_handler(handle_callback)
        ```
    """
    global _callback_handler
    _callback_handler = handler


def verify_callback_signature(
    request: Request,
    secret: str,
    header_name: str = "X-Kling-Signature",
) -> bool:
    """Verify the callback signature.
    
    Args:
        request: The incoming request
        secret: The shared secret for signature verification
        header_name: The header containing the signature (default: "X-Kling-Signature")
        
    Returns:
        bool: True if signature is valid, False otherwise
        
    Raises:
        CallbackSecurityError: If the signature is invalid or missing
    """
    return _validate_signature(request, secret, header_name)


@router.post(
    "/kling",
    response_model=response_models.CallbackAckResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_202_ACCEPTED: {
            "model": response_models.CallbackAckResponse,
            "description": "Callback received and being processed",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": response_models.CallbackValidationErrorResponse,
            "description": "Invalid callback data",
        },
    },
)
async def handle_kling_callback(
    request: Request,
    callback_data: dict[str, Any],
) -> response_models.CallbackAckResponse:
    """Handle incoming Kling AI callback.
    
    This endpoint receives callbacks from Kling AI when async tasks complete.
    It validates the callback data and processes it asynchronously.
    
    Args:
        request: The incoming request
        callback_data: The raw callback data from Kling AI
        
    Returns:
        Acknowledgment response
        
    Raises:
        HTTPException: If there's an error processing the callback
    """
    try:
        # 1. Validate callback data
        try:
            callback = models.CallbackRequest(**callback_data)
        except ValidationError as e:
            error_details = {"validation_errors": e.errors()}
            error = exc.CallbackValidationError(
                "Invalid callback data", 
                details=error_details
            )
            raise HTTPException(
                status_code=error.status_code,
                detail={
                    "status": "error",
                    "error": "validation_error",
                    "message": str(error),
                    "details": error.details,
                },
            ) from e
            
            # 2. Verify signature if configured
        # Note: In production, you should implement signature verification
        # verify_callback_signature(request, "your-secret-key")
        
        # 3. Process the callback asynchronously if a handler is registered
        if _callback_handler:
            # Process in background to avoid blocking the response
            asyncio.create_task(_callback_handler(callback))
        
        # 4. Return acknowledgment
        return response_models.CallbackAckResponse(
            message="Callback received and queued for processing",
            task_id=callback.task_id,
        )
        
    except exc.CallbackError as e:
        # Handle known callback errors
        status_code = getattr(e, 'status_code', 500)
        raise HTTPException(
            status_code=status_code,
            detail={
                "status": "error",
                "error": e.__class__.__name__,
                "message": str(e),
                "details": getattr(e, 'details', {}),
            },
        ) from e
    except Exception as e:
        # Log unexpected errors
        import logging
        logging.exception("Unexpected error processing callback")
        
        # Return 500 for unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "error": "internal_server_error",
                "message": "An unexpected error occurred",
            },
        ) from e
