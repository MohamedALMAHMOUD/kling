"""
Pydantic models for the Kling AI Multi-Image to Video API.

This module defines the data models used for interacting with the Kling AI
Multi-Image to Video API, including request/response models and enums.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


class MultiImageToVideoMode(str, Enum):
    """Supported modes for multi-image to video generation."""
    STANDARD = "std"
    PROFESSIONAL = "pro"


class MultiImageToVideoAspectRatio(str, Enum):
    """Supported aspect ratios for multi-image to video."""
    SIXTEEN_NINE = "16:9"
    NINE_SIXTEEN = "9:16"
    ONE_ONE = "1:1"


class ImageItem(BaseModel):
    """Model representing a single image input for multi-image to video."""
    url: HttpUrl | None = Field(
        None,
        description="URL of the image (must be publicly accessible)",
    )
    base64: str | None = Field(
        None,
        description=(
            "Base64-encoded image data (alternative to URL). "
            "Format: 'data:image/{png,jpeg,webp};base64,{data}'"
        ),
    )

    @field_validator('base64', mode='before')
    def validate_image_data(cls, v):
        """Validate that either URL or base64 is provided, but not both."""
        if v is not None and not v.startswith(('data:image/png;base64,', 'data:image/jpeg;base64,', 'data:image/webp;base64,')):
            raise ValueError("base64 must start with 'data:image/{png,jpeg,webp};base64,'")
        return v

    @field_validator('url', mode='before')
    def validate_url_or_base64(cls, v, values):
        """Validate that either URL or base64 is provided, but not both."""
        if v is not None and values.get('base64') is not None:
            raise ValueError("Cannot specify both 'url' and 'base64'")
        if v is None and values.get('base64') is None:
            raise ValueError("Either 'url' or 'base64' must be provided")
        return v


class VideoInfo(BaseModel):
    """Information about a generated video."""
    id: str = Field(..., description="Generated video ID; globally unique")
    url: HttpUrl = Field(..., description="URL for the generated video")
    duration: float = Field(..., description="Total video duration in seconds")


class TaskInfo(BaseModel):
    """Additional information about a multi-image to video task."""
    external_task_id: str | None = Field(
        None,
        description="Custom task ID provided during task creation",
    )


class TaskResult(BaseModel):
    """Result of a multi-image to video task."""
    videos: list[VideoInfo] = Field(
        default_factory=list,
        description="List of generated videos"
    )


class MultiImageToVideoTask(BaseModel):
    """Multi-image to video task details."""
    task_id: str = Field(..., description="Unique task identifier")
    task_status: Literal["submitted", "processing", "succeed", "failed"] = Field(
        ...,
        description="Current status of the task"
    )
    task_status_msg: str | None = Field(
        None,
        description="Error message if task failed",
    )
    task_info: TaskInfo = Field(..., description="Task metadata")
    task_result: TaskResult | None = Field(
        None,
        description="Task result, available when task is completed",
    )
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @field_validator('created_at', 'updated_at', mode='before')
    def parse_timestamps(cls, v):
        """Parse Unix timestamp in milliseconds to datetime."""
        if isinstance(v, int | float):
            return datetime.fromtimestamp(v / 1000)
        return v


class MultiImageToVideoResponse(BaseModel):
    """Response model for multi-image to video task creation."""
    code: int = Field(..., description="Error code (0 for success)")
    message: str = Field(..., description="Error message")
    request_id: str = Field(..., description="Request ID for debugging")
    data: MultiImageToVideoTask = Field(..., description="Task details")


class MultiImageToVideoListResponse(BaseModel):
    """Response model for listing multi-image to video tasks."""
    code: int = Field(..., description="Error code (0 for success)")
    message: str = Field(..., description="Error message")
    request_id: str = Field(..., description="Request ID for debugging")
    data: list[MultiImageToVideoTask] = Field(..., description="List of tasks")