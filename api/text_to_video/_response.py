"""
Response models for the Kling AI Text-to-Video API.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class TaskStatus(str, Enum):
    """Status of a text-to-video task."""
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    SUCCEEDED = "succeed"
    FAILED = "failed"


class VideoInfo(BaseModel):
    """Information about a generated video."""
    id: str = Field(..., description="Unique identifier for the video")
    url: str = Field(..., description="URL to download the video")
    duration: float = Field(..., description="Duration of the video in seconds")


class TaskResult(BaseModel):
    """Result of a text-to-video task."""
    videos: list[VideoInfo] = Field(..., description="List of generated videos")


class TaskInfo(BaseModel):
    """Information about a text-to-video task."""
    external_task_id: str | None = Field(
        None,
        description="Custom task ID provided during task creation"
    )


class TaskResponse(BaseModel):
    """Response model for a text-to-video task."""
    task_id: str = Field(..., description="Unique identifier for the task")
    task_status: TaskStatus = Field(..., description="Current status of the task")
    task_status_msg: str | None = Field(
        None,
        description="Additional status message, especially for failed tasks"
    )
    task_info: TaskInfo = Field(..., description="Task creation parameters")
    created_at: int = Field(..., description="Task creation timestamp in milliseconds")
    updated_at: int = Field(..., description="Task update timestamp in milliseconds")
    task_result: TaskResult | None = Field(
        None,
        description="Task result, available when task is completed"
    )

    @field_validator('created_at', 'updated_at', pre=True)
    def convert_timestamps(cls, v: int) -> int:
        """Convert timestamps to milliseconds if they're in seconds."""
        if v < 1_000_000_000:  # Likely in seconds
            return v * 1000
        return v

    @property
    def created_at_dt(self) -> datetime:
        """Get the creation time as a datetime object."""
        return datetime.fromtimestamp(self.created_at / 1000)

    @property
    def updated_at_dt(self) -> datetime:
        """Get the update time as a datetime object."""
        return datetime.fromtimestamp(self.updated_at / 1000)

    @property
    def video_url(self) -> str | None:
        """Get the URL of the first video if available."""
        if self.task_result and self.task_result.videos:
            return self.task_result.videos[0].url
        return None


class TaskListResponse(BaseModel):
    """Response model for listing text-to-video tasks."""
    code: int = Field(..., description="API status code")
    message: str = Field(..., description="API status message")
    request_id: str = Field(..., description="Unique request identifier")
    data: list[TaskResponse] = Field(..., description="List of tasks")


class TaskCreateResponse(BaseModel):
    """Response model for creating a text-to-video task."""
    code: int = Field(..., description="API status code")
    message: str = Field(..., description="API status message")
    request_id: str = Field(..., description="Unique request identifier")
    data: TaskResponse = Field(..., description="Created task details")


class TaskGetResponse(BaseModel):
    """Response model for getting a text-to-video task."""
    code: int = Field(..., description="API status code")
    message: str = Field(..., description="API status message")
    request_id: str = Field(..., description="Unique request identifier")
    data: TaskResponse = Field(..., description="Task details")
