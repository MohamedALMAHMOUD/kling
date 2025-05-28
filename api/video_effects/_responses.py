"""Response models for the Kling AI Video Effects API."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

from app.core.third_party_integrations.kling.api.video_effects._requests import (
    EffectType,
    TaskStatus,
    VideoQuality,
)


class TaskData(BaseModel):
    """Data model for a video effect task.
    
    Attributes:
        id: Unique identifier for the task.
        status: Current status of the task.
        effect_type: Type of effect being applied.
        video_url: URL of the source video.
        result_url: URL of the processed video (if completed).
        progress: Processing progress (0-100).
        created_at: When the task was created.
        updated_at: When the task was last updated.
        error: Error message if the task failed.
        metadata: Optional metadata associated with the task.
    """
    id: str = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(..., description="Current task status")
    effect_type: EffectType = Field(..., description="Type of effect applied")
    video_url: str = Field(..., description="Source video URL")
    result_url: str | None = Field(None, description="URL of the processed video")
    progress: int = Field(0, ge=0, le=100, description="Processing progress (0-100)")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    error: str | None = Field(None, description="Error message if task failed")
    metadata: dict[str, str] | None = Field(None, description="Task metadata")


class CreateTaskResponse(BaseModel):
    """Response model for task creation.
    
    Attributes:
        task_id: ID of the created task.
        status: Initial status of the task.
        created_at: When the task was created.
    """
    task_id: str = Field(..., description="ID of the created task")
    status: TaskStatus = Field(..., description="Initial task status")
    created_at: datetime = Field(..., description="Task creation timestamp")


class GetTaskResponse(TaskData):
    """Response model for getting a single task.
    
    Extends TaskData with additional fields.
    """
    pass


class ListTasksResponse(BaseModel):
    """Response model for listing tasks.
    
    Attributes:
        tasks: List of tasks matching the query.
        next_cursor: Pagination cursor for the next page of results.
        has_more: Whether there are more results available.
    """
    tasks: list[TaskData] = Field(default_factory=list, description="List of tasks")
    next_cursor: str | None = Field(None, description="Pagination cursor for next page")
    has_more: bool = Field(False, description="Whether more results are available")


class CancelTaskResponse(BaseModel):
    """Response model for task cancellation.
    
    Attributes:
        task_id: ID of the cancelled task.
        status: New status of the task (should be 'cancelled').
        cancelled_at: When the task was cancelled.
    """
    task_id: str = Field(..., description="ID of the cancelled task")
    status: Literal[TaskStatus.CANCELLED] = Field(..., description="Task status after cancellation")
    cancelled_at: datetime = Field(..., description="Cancellation timestamp")
