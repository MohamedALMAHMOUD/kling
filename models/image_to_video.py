"""
Pydantic models for the Kling AI Image-to-Video API.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.core.third_party_integrations.kling.config import (
    CameraControl,
    KlingModelName,
    VideoMode,
)


class TrajectoryPoint(BaseModel):
    """A point in a motion trajectory."""
    x: int = Field(..., description="X-coordinate of the trajectory point")
    y: int = Field(..., description="Y-coordinate of the trajectory point")


class DynamicMask(BaseModel):
    """Configuration for dynamic mask and its motion trajectory."""
    mask: str = Field(..., description="URL or Base64 encoded mask image")
    trajectories: list[TrajectoryPoint] = Field(
        ...,
        min_length=2,
        max_length=77,
        description="Sequence of points defining the motion trajectory"
    )


class ImageToVideoRequest(BaseModel):
    """Request model for image-to-video generation."""
    model_name: KlingModelName = Field(
        KlingModelName.KLING_V1,
        alias="model_name",
        description="Model to use for generation"
    )
    image: str = Field(
        ...,
        description="Reference image as URL or Base64 encoded string"
    )
    image_tail: str | None = Field(
        None,
        description="Optional end frame control image as URL or Base64"
    )
    prompt: str | None = Field(
        None,
        max_length=2500,
        description="Positive text prompt"
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
    mode: VideoMode = Field(
        VideoMode.STANDARD,
        description="Generation mode (standard or professional)"
    )
    static_mask: str | None = Field(
        None,
        description="URL or Base64 encoded static mask image"
    )
    dynamic_masks: list[DynamicMask] | None = Field(
        None,
        max_items=6,
        description="List of dynamic mask configurations"
    )
    camera_control: CameraControl | None = Field(
        None,
        description="Camera movement configuration"
    )
    duration: Literal[5, 10] = Field(
        5,
        description="Video duration in seconds (5 or 10)"
    )
    callback_url: HttpUrl | None = Field(
        None,
        description="Webhook URL for task completion notifications"
    )
    external_task_id: str | None = Field(
        None,
        description="Custom ID for tracking the task"
    )

    class Config:
        """Pydantic config."""
        use_enum_values = True
        populate_by_name = True


class VideoInfo(BaseModel):
    """Information about a generated video."""
    id: str = Field(..., description="Generated video ID; globally unique")
    url: HttpUrl = Field(..., description="URL for the generated video")
    duration: float = Field(..., description="Total video duration in seconds")


class TaskResult(BaseModel):
    """Result of an image-to-video task."""
    videos: list[VideoInfo] = Field(
        default_factory=list,
        description="List of generated videos"
    )


class TaskInfo(BaseModel):
    """Information about an image-to-video task."""
    external_task_id: str | None = Field(None, alias="external_task_id")


class ImageToVideoTask(BaseModel):
    """Image-to-video task details."""
    task_id: str = Field(..., alias="task_id")
    task_status: Literal["submitted", "processing", "succeed", "failed"] = Field(
        ...,
        alias="task_status"
    )
    task_status_msg: str | None = Field(
        None,
        alias="task_status_msg",
        description="Error message if task failed"
    )
    task_info: TaskInfo = Field(..., alias="task_info")
    created_at: datetime = Field(..., alias="created_at")
    updated_at: datetime = Field(..., alias="updated_at")
    task_result: TaskResult | None = Field(None, alias="task_result")

    @field_validator("created_at", "updated_at", mode="before")
    def parse_timestamps(cls, v):
        """Parse Unix timestamp in milliseconds to datetime."""
        if isinstance(v, int | float):
            return datetime.fromtimestamp(v / 1000)
        return v


class ImageToVideoResponse(BaseModel):
    """Response model for image-to-video task creation."""
    code: int = Field(..., description="Error code (0 for success)")
    message: str = Field(..., description="Error message")
    request_id: str = Field(..., description="Request ID for debugging")
    data: ImageToVideoTask = Field(..., description="Task details")


class ImageToVideoListResponse(BaseModel):
    """Response model for listing image-to-video tasks."""
    code: int = Field(..., description="Error code (0 for success)")
    message: str = Field(..., description="Error message")
    request_id: str = Field(..., description="Request ID for debugging")
    data: list[ImageToVideoTask] = Field(..., description="List of tasks")

