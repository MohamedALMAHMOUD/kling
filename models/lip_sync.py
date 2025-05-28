"""Pydantic models for the Kling AI Lip Sync API."""
from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


class LipSyncStatus(str, Enum):
    """Status of a lip sync task."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class LipSyncRequest(BaseModel):
    """Request model for creating a lip sync task."""
    video_url: str = Field(..., description="URL of the video to lip sync")
    audio_url: str = Field(..., description="URL of the audio to sync to")
    output_format: Literal["mp4", "gif"] = Field(
        default="mp4",
        description="Output format of the generated video"
    )
    resolution: str = Field(
        default="720p",
        description="Output resolution (e.g., 480p, 720p, 1080p)",
        pattern=r"^\d{3,4}p$"
    )
    fps: int = Field(
        default=30,
        ge=1,
        le=60,
        description="Frames per second of the output video"
    )

    @field_validator('video_url', 'audio_url')
    @classmethod
    def validate_urls(cls, v: str) -> str:
        """Validate that URLs are properly formatted."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v


class LipSyncResponse(BaseModel):
    """Response model for a lip sync task."""
    task_id: str = Field(..., description="Unique identifier for the task")
    status: LipSyncStatus = Field(..., description="Current status of the task")
    result_url: HttpUrl | None = Field(
        None,
        description="URL to download the result, if completed"
    )
    progress: float = Field(
        0.0,
        ge=0.0,
        le=100.0,
        description="Progress percentage (0-100)"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the task"
    )
