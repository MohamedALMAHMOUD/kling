"""Request models for the Kling AI Lip Sync API."""
from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class TaskStatus(str, Enum):
    """Status of a lip sync task."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskListQueryParams(BaseModel):
    """Query parameters for listing tasks."""
    status: TaskStatus | None = Field(
        None,
        description="Filter tasks by status"
    )
    limit: int = Field(
        10,
        ge=1,
        le=100,
        description="Maximum number of tasks to return"
    )
    offset: int = Field(
        0,
        ge=0,
        description="Number of tasks to skip"
    )


class CreateTaskRequest(BaseModel):
    """Request model for creating a lip sync task."""
    video_url: HttpUrl = Field(..., description="URL of the video to lip sync")
    audio_url: HttpUrl = Field(..., description="URL of the audio to sync to")
    output_format: Literal["mp4", "gif"] = Field(
        "mp4",
        description="Output format of the generated video"
    )
    resolution: str = Field(
        "720p",
        description="Output resolution (e.g., 480p, 720p, 1080p)",
        pattern=r"^\d{3,4}p$",
    )
    fps: int = Field(
        30,
        ge=1,
        le=60,
        description="Frames per second of the output video"
    )
    callback_url: HttpUrl | None = Field(
        None,
        description="URL to receive a webhook when the task completes"
    )
    metadata: dict[str, str] | None = Field(
        None,
        description="Custom metadata to associate with the task"
    )
