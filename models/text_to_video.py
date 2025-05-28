"""
Pydantic models for the Kling AI Text-to-Video API.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.core.third_party_integrations.kling.config import (
    AspectRatio,
    CameraControl,
    KlingModelName,
    VideoMode,
)


class VideoInfo(BaseModel):
    """Information about a generated video."""
    id: str = Field(..., description="Generated video ID; globally unique")
    url: HttpUrl = Field(..., description="URL for the generated video")
    duration: float = Field(..., description="Total video duration in seconds")


class TaskResult(BaseModel):
    """Result of a text-to-video task."""
    videos: list[VideoInfo] = Field(default_factory=list, description="List of generated videos")


class TaskInfo(BaseModel):
    """Information about a text-to-video task."""
    external_task_id: str | None = Field(None, alias="external_task_id")


class TextToVideoTask(BaseModel):
    """Text-to-video task details."""
    task_id: str = Field(..., alias="task_id")
    task_status: Literal["submitted", "processing", "succeed", "failed"] = Field(
        ..., alias="task_status"
    )
    task_status_msg: str | None = Field(
        None, alias="task_status_msg", description="Error message if task failed"
    )
    task_info: TaskInfo = Field(..., alias="task_info")
    created_at: datetime = Field(..., alias="created_at")
    updated_at: datetime = Field(..., alias="updated_at")
    task_result: TaskResult | None = Field(None, alias="task_result")

    @field_validator("created_at", "updated_at", pre=True)
    def parse_timestamps(cls, v):
        """Parse Unix timestamp in milliseconds to datetime."""
        if isinstance(v, int | float):
            return datetime.fromtimestamp(v / 1000)
        return v


class TextToVideoRequest(BaseModel):
    """Request model for text-to-video generation."""
    model_name: KlingModelName = Field(
        KlingModelName.KLING_V1,
        alias="model_name",
        description="Model to use for generation",
    )
    prompt: str = Field(..., max_length=2500, description="Text prompt for video generation")
    negative_prompt: str | None = Field(
        None, max_length=2500, description="Negative prompt to avoid certain content"
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
    mode: VideoMode = Field(
        VideoMode.STANDARD,
        description="Generation mode (standard or professional)",
    )
    camera_control: CameraControl | None = Field(
        None, description="Camera movement configuration"
    )
    aspect_ratio: AspectRatio = Field(
        AspectRatio.SIXTEEN_NINE, description="Aspect ratio of the generated video"
    )
    duration: int = Field(
        5,
        ge=5,
        le=10,
        description="Duration of the video in seconds (5 or 10)",
    )
    callback_url: HttpUrl | None = Field(
        None, description="Webhook URL for task completion notifications"
    )
    external_task_id: str | None = Field(
        None, description="Custom ID for tracking the task"
    )

    class Config:
        """Pydantic config."""
        use_enum_values = True
        allow_population_by_field_name = True


class TextToVideoResponse(BaseModel):
    """Response model for text-to-video task creation."""
    code: int = Field(..., description="Error code (0 for success)")
    message: str = Field(..., description="Error message")
    request_id: str = Field(..., description="Request ID for debugging")
    data: TextToVideoTask = Field(..., description="Task details")


class TextToVideoListResponse(BaseModel):
    """Response model for listing text-to-video tasks."""
    code: int = Field(..., description="Error code (0 for success)")
    message: str = Field(..., description="Error message")
    request_id: str = Field(..., description="Request ID for debugging")
    data: list[TextToVideoTask] = Field(..., description="List of tasks")
