"""
Tests for the Virtual Try-On API models.
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.third_party_integrations.kling.api.virtual_try_on._requests import (
    ImageSource,
    ModelName,
    TaskListQuery,
    VirtualTryOnRequest,
)
from app.core.third_party_integrations.kling.api.virtual_try_on._responses import (
    TaskListResponse,
    TaskResponse,
    VirtualTryOnTaskResponse,
    PaginatedResponse,
    TaskListPaginatedResponse,
)


class TestTaskListQuery:
    """Tests for the TaskListQuery model."""

    def test_default_values(self) -> None:
        """Test that default values are set correctly."""
        query = TaskListQuery()
        assert query.page_num == 1
        assert query.page_size == 30

    def test_validation(self) -> None:
        """Test field validation."""
        with pytest.raises(ValidationError):
            TaskListQuery(page_num=0)
        
        with pytest.raises(ValidationError):
            TaskListQuery(page_size=0)
        
        with pytest.raises(ValidationError):
            TaskListQuery(page_size=101)  # Max is 100

    def test_aliases(self) -> None:
        """Test that field aliases work correctly."""
        query = TaskListQuery(pageNum=2, pageSize=50)
        assert query.page_num == 2
        assert query.page_size == 50


class TestVirtualTryOnRequest:
    """Tests for the VirtualTryOnRequest model."""

    def test_required_fields(self) -> None:
        """Test that required fields are enforced."""
        with pytest.raises(ValidationError):
            VirtualTryOnRequest()

    def test_model_name_validation(self) -> None:
        """Test that model name is validated against enum values."""
        with pytest.raises(ValidationError):
            VirtualTryOnRequest(
                model_name="invalid-model",
                image_source=ImageSource(url="http://example.com/image.jpg"),
            )

    def test_valid_request(self) -> None:
        """Test a valid request."""
        request = VirtualTryOnRequest(
            model_name=ModelName.KLING_1,
            image_source=ImageSource(url="http://example.com/image.jpg"),
        )
        assert request.model_name == ModelName.KLING_1
        assert request.image_source.url == "http://example.com/image.jpg"


class TestResponseModels:
    """Tests for response models."""

    def test_task_response(self) -> None:
        """Test TaskResponse model."""
        response = TaskResponse(
            code=200,
            message="Success",
            request_id="req-123",
            data={"task_id": "task-123", "task_status": "processing"},
        )
        assert response.code == 200
        assert response.data.task_id == "task-123"

    def test_task_list_response(self) -> None:
        """Test TaskListResponse model."""
        response = TaskListResponse(
            code=200,
            message="Success",
            request_id="req-123",
            data=[{"task_id": "task-123", "task_status": "processing"}],
        )
        assert len(response.data) == 1
        assert response.data[0].task_id == "task-123"

    def test_paginated_response(self) -> None:
        """Test PaginatedResponse model."""
        response = PaginatedResponse[str](
            code=200,
            message="Success",
            request_id="req-123",
            data=["item1", "item2"],
            total=2,
            page=1,
            page_size=10,
        )
        assert response.total == 2
        assert response.data == ["item1", "item2"]
        assert response.page == 1
        assert response.page_size == 10
