"""
Response models for the Virtual Try-On API.
"""
from __future__ import annotations

from typing import Generic, TypeAlias, TypeVar

from pydantic import BaseModel, Field

from .._response import BaseResponse, TaskInfo
from ._requests import ModelName

T = TypeVar('T')

class TaskResponse(BaseResponse):
    """Response model for task creation and status check."""
    data: TaskInfo = Field(..., description="Task information")


class TaskListResponse(BaseResponse):
    """Response model for listing tasks."""
    data: list[TaskInfo] = Field(..., description="List of task information")


class VirtualTryOnTaskResponse(TaskResponse):
    """Response model for virtual try-on task creation."""
    model_name: ModelName = Field(
        ...,
        description="Model used for this task"
    )


class TaskListQuery(BaseModel):
    """Query parameters for listing tasks."""
    page_num: int = Field(
        default=1,
        ge=1,
        le=1000,
        description="Page number (1-based)",
        alias="pageNum"
    )
    page_size: int = Field(
        default=30,
        ge=1,
        le=500,
        description="Number of items per page",
        alias="pageSize"
    )


class PaginatedResponse(BaseModel):
    """Base model for paginated responses."""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    has_more: bool = Field(..., description="Whether there are more items")


class TaskListPaginatedResponse(PaginatedResponse):
    """Paginated response for task listing."""
    items: list[TaskInfo] = Field(..., description="List of tasks")
