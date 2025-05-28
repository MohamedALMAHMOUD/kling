"""Request models for the Kling AI Video Effects API."""
from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class EffectType(str, Enum):
    """Available video effect types."""
    STYLE_TRANSFER = "style_transfer"
    FILTER = "filter"
    ENHANCE = "enhance"
    STABILIZE = "stabilize"


class VideoQuality(str, Enum):
    """Available video quality presets."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"


class CreateVideoEffectRequest(BaseModel):
    """Request model for creating a new video effect task.
    
    Attributes:
        video_url: The URL of the source video to apply effects to.
        effect_type: The type of effect to apply.
        intensity: Intensity of the effect (0.0 to 1.0).
        quality: Output video quality preset.
        style_reference: Optional reference image URL for style transfer.
        callback_url: Optional URL to receive webhook callbacks.
        metadata: Optional metadata to associate with the task.
    """
    video_url: HttpUrl = Field(..., description="Source video URL")
    effect_type: EffectType = Field(..., description="Type of effect to apply")
    intensity: float = Field(0.5, ge=0.0, le=1.0, description="Effect intensity (0.0 to 1.0)")
    quality: VideoQuality = Field(VideoQuality.HIGH, description="Output video quality")
    style_reference: HttpUrl | None = Field(
        None,
        description="Reference image URL for style transfer (required for style_transfer effect)"
    )
    callback_url: HttpUrl | None = Field(
        None,
        description="URL to receive webhook callbacks when processing is complete"
    )
    metadata: dict[str, str] | None = Field(
        None,
        description="Optional metadata to associate with the task"
    )


class TaskStatus(str, Enum):
    """Possible task status values."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ListTasksRequest(BaseModel):
    """Request model for listing tasks with optional filtering.
    
    Attributes:
        status: Filter tasks by status.
        limit: Maximum number of tasks to return.
        cursor: Pagination cursor for the next page of results.
    """
    status: TaskStatus | None = Field(None, description="Filter tasks by status")
    limit: int = Field(10, ge=1, le=100, description="Number of tasks to return (1-100)")
    cursor: str | None = Field(None, description="Pagination cursor for the next page of results")
