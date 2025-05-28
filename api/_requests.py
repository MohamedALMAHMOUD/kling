"""
Global models for the Virtual Try-On API.

This module contains base models that are shared across multiple endpoints.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, Field, HttpUrl, field_validator


class TaskStatus(str, Enum):
    """Status of a virtual try-on task."""
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    SUCCEED = "succeed"
    FAILED = "failed"




class ImageInfo(BaseModel):
    """Model representing an image in the API response."""
    index: int = Field(..., description="Image index")
    url: HttpUrl = Field(..., description="URL of the generated image")


class TaskResult(BaseModel):
    """Model containing the result of a task."""
    images: list[ImageInfo] = Field(..., description="List of generated images")


class TaskInfo(BaseModel):
    """Model containing information about a task."""
    task_id: str = Field(..., description="Unique task identifier")
    task_status: TaskStatus = Field(..., description="Current status of the task")
    task_status_msg: str | None = Field(
        None,
        description="Additional status message, especially for failures"
    )
    created_at: int = Field(
        ...,
        description="Unix timestamp in milliseconds when the task was created"
    )
    updated_at: int = Field(
        ...,
        description="Unix timestamp in milliseconds when the task was last updated"
    )
    task_result: TaskResult | None = Field(
        None,
        description="Task result, available when status is 'succeed'"
    )

    @field_validator('task_status', mode='before')
    @classmethod
    def validate_task_status(cls, v: Any) -> TaskStatus:
        """Convert string status to TaskStatus enum."""
        if isinstance(v, str):
            return TaskStatus(v.lower())
        return v
