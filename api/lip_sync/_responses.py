"""Response models for the Kling AI Lip Sync API."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl

from ._requests import TaskStatus


class TaskData(BaseModel):
    """Data model for a lip sync task."""
    task_id: str = Field(..., description="Unique identifier for the task")
    status: TaskStatus = Field(..., description="Current status of the task")
    created_at: datetime = Field(..., description="When the task was created")
    updated_at: datetime = Field(..., description="When the task was last updated")
    progress: float = Field(
        0.0,
        ge=0.0,
        le=100.0,
        description="Progress percentage (0-100)"
    )
    result_url: HttpUrl | None = Field(
        None,
        description="URL to download the result, if completed"
    )
    error: str | None = Field(
        None,
        description="Error message, if the task failed"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Custom metadata associated with the task"
    )


class TaskResponse(BaseModel):
    """Response model for a single task."""
    data: TaskData = Field(..., description="The task data")


class TaskListResponse(BaseModel):
    """Response model for a list of tasks."""
    data: list[TaskData] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks")
    limit: int = Field(..., description="Number of tasks per page")
    offset: int = Field(..., description="Number of tasks skipped")
