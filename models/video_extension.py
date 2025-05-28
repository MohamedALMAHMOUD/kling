"""
Pydantic models for the Kling AI Video Extension API.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.core.third_party_integrations.kling.config import KlingModelName


class VideoInfo(BaseModel):
    """Information about an extended video."""
    id: str = Field(..., description="Extended video ID; globally unique")
    url: HttpUrl = Field(..., description="URL for the extended video")
    duration: float = Field(..., description="Total video duration in seconds")


class TaskResult(BaseModel):
    """Result of a video extension task."""
    video: VideoInfo = Field(..., description="Extended video information")


class TaskInfo(BaseModel):
    """Information about a video extension task."""
    external_task_id: str | None = Field(None, description="Custom ID for tracking the task")


class VideoExtensionTask(BaseModel):
    """Video extension task details."""
    task_id: str = Field(..., description="Unique task ID")
    task_status: Literal["submitted", "processing", "succeed", "failed"] = Field(
        ..., description="Current status of the task"
    )
    task_status_msg: str | None = Field(
        None, description="Detailed status message or error description"
    )
    task_info: TaskInfo = Field(..., description="Task metadata")
    task_result: TaskResult | None = Field(None, description="Task result when completed")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def parse_timestamps(cls, v):
        """Parse Unix timestamp in milliseconds to datetime."""
        if isinstance(v, (int, float)):
            return datetime.fromtimestamp(v / 1000)
        return v


class VideoExtensionRequest(BaseModel):
    """Request model for video extension.
    
    Attributes:
        model_name: Model to use for generation
        video_id: ID of the video to extend
        prompt: Text prompt for the extension (max 2500 chars)
        negative_prompt: Negative text prompt (max 2500 chars)
        cfg_scale: Flexibility in video generation (0-1)
        callback_url: Webhook URL for task completion notifications
        external_task_id: Custom ID for tracking the task
    """
    model_name: KlingModelName = Field(
        KlingModelName.KLING_V1,
        description="Model to use for generation",
    )
    video_id: str = Field(..., description="ID of the video to extend")
    prompt: str | None = Field(
        None,
        max_length=2500,
        description="Text prompt for the video extension",
    )
    negative_prompt: str | None = Field(
        None,
        max_length=2500,
        description="Negative text prompt to avoid certain content",
    )
    cfg_scale: float = Field(
        0.5,
        ge=0,
        le=1,
        description=(
            "Flexibility in video generation; higher values make the output "
            "more closely follow the prompt"
        ),
    )
    callback_url: HttpUrl | None = Field(
        None, description="Webhook URL for task completion notifications"
    )
    external_task_id: str | None = Field(
        None, description="Custom ID for tracking the task"
    )

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True


class VideoExtensionResponse(BaseModel):
    """Response model for video extension task creation."""
    code: int = Field(..., description="Error code (0 for success)")
    message: str = Field(..., description="Error message")
    request_id: str = Field(..., description="Request ID for debugging")
    data: VideoExtensionTask = Field(..., description="Task details")


class VideoExtensionListResponse(BaseModel):
    """Response model for listing video extension tasks."""
    code: int = Field(..., description="Error code (0 for success)")
    message: str = Field(..., description="Error message")
    request_id: str = Field(..., description="Request ID for debugging")
    data: list[VideoExtensionTask] = Field(..., description="List of tasks")
