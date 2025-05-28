"""
Virtual Try-On API client for Kling AI.

This module provides an asynchronous client for interacting with the Kling AI
Virtual Try-On API, enabling virtual try-on of clothing items on human images.
"""
from __future__ import annotations

from ._exceptions import (
    APIError,
    AuthenticationError,
    InvalidImageError,
    RateLimitError,
    TaskFailedError,
    TimeoutError,
    ValidationError,
    VirtualTryOnError,
)
from ._requests import ImageSource, ModelName, TaskListQuery, VirtualTryOnRequest
from ._responses import (
    PaginatedResponse,
    TaskListPaginatedResponse,
    TaskListResponse,
    TaskResponse,
    VirtualTryOnTaskResponse,
)
from .virtual_try_on import VirtualTryOnAPI, VirtualTryOnClient

__all__ = [
    # Main client classes
    "VirtualTryOnAPI",
    "VirtualTryOnClient",
    
    # Request models
    "VirtualTryOnRequest",
    "TaskListQuery",
    "ModelName",
    "ImageSource",
    
    # Response models
    "TaskResponse",
    "TaskListResponse",
    "VirtualTryOnTaskResponse",
    "PaginatedResponse",
    "TaskListPaginatedResponse",
    
    # Exceptions
    "VirtualTryOnError",
    "APIError",
    "AuthenticationError",
    "RateLimitError",
    "TimeoutError",
    "ValidationError",
    "InvalidImageError",
    "TaskFailedError",
]
