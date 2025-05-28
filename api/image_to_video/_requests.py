"""
Request handling for the Kling AI Image-to-Video API.
"""
from __future__ import annotations

import json
import logging
from typing import Any

import httpx
from pydantic import BaseModel, Field, ValidationError

from ...config import KlingConfig
from ._exceptions import (
    APIRequestError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError as KlingValidationError,
    handle_api_error,
)

logger = logging.getLogger(__name__)


class APIRequest(BaseModel):
    """Base class for API requests."""

    def to_dict(self) -> dict[str, Any]:
        """Convert the request to a dictionary."""
        return self.dict(exclude_none=True, by_alias=True)


class ImageToVideoRequest(APIRequest):
    """Request model for creating an image-to-video task."""

    image: str = Field(..., description="Base64 encoded image or image URL")
    model_name: str = Field("kling-v1", description="Model to use for generation")
    prompt: str = Field(..., description="Text prompt for video generation")
    negative_prompt: str = Field(
        "", description="Negative prompt to avoid certain elements"
    )
    duration: float = Field(5.0, ge=1.0, le=10.0, description="Video duration in seconds")
    fps: int = Field(8, ge=1, le=30, description="Frames per second")
    width: int = Field(512, ge=256, le=1024, description="Video width")
    height: int = Field(512, ge=256, le=1024, description="Video height")
    seed: int | None = Field(None, ge=0, le=2**32 - 1, description="Random seed")


class TaskStatusRequest(APIRequest):
    """Request model for checking task status."""

    task_id: str = Field(..., description="Task ID to check status for")


class ListTasksRequest(APIRequest):
    """Request model for listing tasks."""

    limit: int = Field(10, ge=1, le=100, description="Maximum number of tasks to return")
    offset: int = Field(0, ge=0, description="Pagination offset")
    status: str | None = Field(None, description="Filter tasks by status")

