"""
Request models for the Kling AI Video Extension API.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class TaskStatus(str, Enum):
    """Status of a video extension task."""
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    SUCCEED = "succeed"
    FAILED = "failed"


class VideoExtensionRequest(BaseModel):
    """
    Request model for creating a video extension task.

    Attributes:
        video_id: The ID of the video to extend
        prompt: Optional text prompt for the extension (max 2500 chars)
        negative_prompt: Optional negative text prompt (max 2500 chars)
        cfg_scale: Flexibility in video generation (0-1)
        callback_url: Optional callback URL for task status updates
    """
    video_id: str = Field(..., description="Video ID to extend")
    prompt: str | None = Field(
        None,
        max_length=2500,
        description="Text prompt for the video extension"
    )
    negative_prompt: str | None = Field(
        None,
        max_length=2500,
        description="Negative text prompt"
    )
    cfg_scale: float = Field(
        0.5,
        ge=0,
        le=1,
        description="Flexibility in video generation (0-1)"
    )
    callback_url: HttpUrl | None = Field(
        None,
        description="Callback URL for task status updates"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "video_id": "video_123",
                "prompt": "A beautiful sunset over mountains",
                "negative_prompt": "blurry, low quality, distorted",
                "cfg_scale": 0.7,
                "callback_url": "https://example.com/callback"
            }
        }
    }


class TaskListQueryParams(BaseModel):
    """Query parameters for listing video extension tasks.

    Attributes:
        page_num: Page number (1-1000)
        page_size: Number of items per page (1-500)
    """
    page_num: int = Field(
        1,
        ge=1,
        le=1000,
        description="Page number"
    )
    page_size: int = Field(
        30,
        ge=1,
        le=500,
        description="Number of items per page"
    )

    def to_query_string(self) -> str:
        """Convert query parameters to URL query string."""
        return f"pageNum={self.page_num}&pageSize={self.page_size}"
