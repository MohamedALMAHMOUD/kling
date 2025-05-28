"""Response models for Kling AI Image Generation API."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class TaskStatus(str, Enum):
    """Possible status values for an image generation task."""
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    SUCCEEDED = "succeed"
    FAILED = "failed"


class GeneratedImage(BaseModel):
    """Model representing a single generated image.
    
    Attributes:
        index: The index of the image (0-9).
        url: URL to access the generated image.
    """
    index: int = Field(..., ge=0, le=9, description="Index of the generated image.")
    url: HttpUrl = Field(..., description="URL to access the generated image.")


class TaskResult(BaseModel):
    """Model containing the results of a completed task.
    
    Attributes:
        images: List of generated images.
    """
    images: list[GeneratedImage] = Field(
        default_factory=list,
        description="List of generated images.",
    )


class BaseResponse(BaseModel):
    """Base response model for all API responses.
    
    Attributes:
        code: Error code (0 for success).
        message: Human-readable error message.
        request_id: Unique identifier for the request.
    """
    code: int = Field(..., description="Error code (0 for success).")
    message: str = Field(..., description="Human-readable error message.")
    request_id: str = Field(..., alias="request_id", description="Unique request identifier.")


class TaskResponse(BaseResponse):
    """Response model for task operations.
    
    Attributes:
        task_id: Unique identifier for the task.
        task_status: Current status of the task.
        task_status_msg: Optional message with additional status information.
        created_at: Timestamp when the task was created.
        updated_at: Timestamp when the task was last updated.
        task_result: Optional result data when the task is complete.
    """
    task_id: str = Field(..., description="Unique identifier for the task.")
    task_status: TaskStatus = Field(..., description="Current status of the task.")
    task_status_msg: str | None = Field(
        default=None,
        description="Additional status information, especially for failures.",
    )
    created_at: int = Field(
        ...,
        description="Unix timestamp (ms) when the task was created.",
    )
    updated_at: int = Field(
        ...,
        description="Unix timestamp (ms) when the task was last updated.",
    )
    task_result: TaskResult | None = Field(
        default=None,
        description="Task result data, available when task is complete.",
    )

    @property
    def created_dt(self) -> datetime:
        """Return created_at as a datetime object."""
        return datetime.fromtimestamp(self.created_at / 1000)

    @property
    def updated_dt(self) -> datetime:
        """Return updated_at as a datetime object."""
        return datetime.fromtimestamp(self.updated_at / 1000)


class TaskListResponse(BaseResponse):
    """Response model for listing tasks.
    
    Attributes:
        __root__: List of task responses.
    """
    __root__: list[TaskResponse] = Field(
        default_factory=list,
        description="List of task responses.",
    )


class TaskCreateResponse(BaseResponse):
    """Response model for task creation.
    
    This is a simplified version of TaskResponse used specifically for task creation.
    """
    data: dict[str, str | int] = Field(
        ...,
        description="Task creation response data.",
    )
    
    @property
    def task_id(self) -> str:
        """Get the task ID from the response data."""
        return str(self.data.get("task_id", ""))
