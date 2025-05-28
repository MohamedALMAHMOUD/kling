"""
Response models for the Kling AI Image-to-Video API.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, HttpUrl


class TaskStatus(str, Enum):
    """Status of an image-to-video generation task."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VideoQuality(str, Enum):
    """Video quality options."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"


class VideoFormat(str, Enum):
    """Supported video formats."""

    MP4 = "mp4"
    WEBM = "webm"
    GIF = "gif"


class VideoMetadata(BaseModel):
    """Metadata about the generated video."""

    duration: float = Field(..., description="Duration of the video in seconds")
    width: int = Field(..., description="Width of the video in pixels")
    height: int = Field(..., description="Height of the video in pixels")
    fps: int = Field(..., description="Frames per second")
    format: VideoFormat = Field(..., description="Video format")
    size_bytes: int = Field(..., description="Size of the video file in bytes")
    bitrate: int | None = Field(None, description="Video bitrate in kbps")
    codec: str | None = Field(None, description="Video codec used")
    has_audio: bool = Field(False, description="Whether the video includes audio")


class TaskProgress(BaseModel):
    """Progress information for a task."""

    current: int = Field(0, ge=0, description="Current progress value")
    total: int = Field(100, ge=0, description="Total progress value")
    percentage: float = Field(0.0, ge=0.0, le=100.0, description="Progress percentage")
    message: str | None = Field(None, description="Optional progress message")


class ErrorDetail(BaseModel):
    """Detailed error information."""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict[str, Any]] = Field(None, description="Additional error details")


class TaskResponse(BaseModel):
    """Base response model for task operations."""

    task_id: str = Field(..., description="Unique identifier for the task")
    status: TaskStatus = Field(..., description="Current status of the task")
    created_at: datetime = Field(..., description="When the task was created")
    updated_at: datetime = Field(..., description="When the task was last updated")
    progress: TaskProgress = Field(..., description="Current progress information")
    error: ErrorDetail | None = Field(None, description="Error details if task failed")


class VideoGenerationResponse(TaskResponse):
    """Response model for video generation tasks."""

    video_url: HttpUrl | None = Field(None, description="URL to download the generated video")
    thumbnail_url: HttpUrl | None = Field(None, description="URL to download the video thumbnail")
    metadata: VideoMetadata | None = Field(None, description="Video metadata")
    expires_at: datetime | None = Field(
        None, description="When the generated video will expire and be deleted"
    )


class TaskListResponse(BaseModel):
    """Response model for listing tasks."""

    tasks: list[TaskResponse] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks")
    limit: int = Field(..., description="Maximum number of tasks returned")
    offset: int = Field(..., description="Pagination offset")
    has_more: bool = Field(..., description="Whether there are more tasks available")


class APIResponse(BaseModel):
    """Generic API response wrapper."""

    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[dict[str, Any] | list[Any]] = Field(
        None, description="Response data"
    )
    error: Optional[ErrorDetail] = Field(None, description="Error details if any")
    request_id: Optional[str] = Field(None, description="Unique identifier for the request")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the response was generated")