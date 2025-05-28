"""
Response models for the Kling AI Video Extension API.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_serializer

from ._requests import TaskStatus


class VideoInfo(BaseModel):
    """Information about a video."""
    id: str = Field(..., description="Unique video ID")
    url: HttpUrl | None = Field(None, description="URL of the video")
    duration: float | None = Field(None, description="Duration in seconds")

    @field_serializer('url')
    def serialize_url(self, url: HttpUrl | None, _info: Any) -> str | None:
        return str(url) if url else None


class TaskInfo(BaseModel):
    """Information about a video extension task."""
    parent_video: VideoInfo = Field(..., description="Original video information")
    # Add other task info fields as needed


class VideoResult(BaseModel):
    """Result of a video generation task."""
    id: str = Field(..., description="Generated video ID")
    url: HttpUrl | None = Field(None, description="URL of the generated video")
    seed: str | None = Field(None, description="Random seed used for generation")
    duration: float | None = Field(None, description="Duration in seconds")

    @field_serializer('url')
    def serialize_url(self, url: HttpUrl | None, _info: Any) -> str | None:
        return str(url) if url else None


class TaskResult(BaseModel):
    """Result of a video extension task."""
    videos: list[VideoResult] = Field(..., description="List of generated videos")


class BaseResponse(BaseModel):
    """Base response model for all API responses."""
    code: int = Field(..., description="Error code (0 = success, non-zero = error)")
    message: str = Field(..., description="Error message")
    request_id: str = Field(..., description="Unique request ID for tracking")


class VideoExtensionResponse(BaseResponse):
    """Response model for video extension task creation."""
    data: VideoExtensionTaskData = Field(..., description="Task information")


class TaskStatusResponse(BaseResponse):
    """Response model for task status query."""
    data: TaskStatusData = Field(..., description="Task status information")


class TaskListResponse(BaseResponse):
    """Response model for task list query."""
    data: list[TaskStatusData] = Field(..., description="List of task statuses")


class VideoExtensionTaskData(BaseModel):
    """Data model for video extension task response."""
    task_id: str = Field(..., description="Unique task ID")
    task_status: TaskStatus = Field(..., description="Current task status")
    created_at: int = Field(..., description="Task creation timestamp (ms)")
    updated_at: int = Field(..., description="Task update timestamp (ms)")


class TaskStatusData(BaseModel):
    """Data model for task status response."""
    task_id: str = Field(..., description="Unique task ID")
    task_status: TaskStatus = Field(..., description="Current task status")
    task_status_msg: str | None = Field(
        None,
        description="Detailed status message"
    )
    task_info: TaskInfo = Field(..., description="Task information")
    task_result: TaskResult | None = Field(None, description="Task result data")
    created_at: int = Field(..., description="Task creation timestamp (ms)")
    updated_at: int = Field(..., description="Task update timestamp (ms)")
