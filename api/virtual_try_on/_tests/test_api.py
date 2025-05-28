"""
Tests for the Virtual Try-On API client.
"""
from __future__ import annotations

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import Response

from app.core.third_party_integrations.kling.api.virtual_try_on.virtual_try_on import VirtualTryOnAPI
from app.core.third_party_integrations.kling.api.virtual_try_on._requests import (
    ImageSource,
    ModelName,
    TaskListQuery,
    VirtualTryOnRequest,
)
from app.core.third_party_integrations.kling.api.virtual_try_on._responses import (
    TaskResponse,
    TaskListResponse,
    VirtualTryOnTaskResponse,
)


class TestVirtualTryOnAPI:
    """Tests for the VirtualTryOnAPI class."""

    async def test_create_task_success(
        self, virtual_try_on_api: VirtualTryOnAPI, mock_http_client: AsyncMock
    ) -> None:
        """Test successful task creation."""
        # Setup mock response
        mock_response = {
            "code": 200,
            "message": "Success",
            "request_id": "req-123",
            "data": {
                "task_id": "task-123",
                "task_status": "submitted"
            }
        }
        mock_http_client.post.return_value = Response(
            status_code=200,
            content=json.dumps(mock_response),
        )

        # Call the method
        request = VirtualTryOnRequest(
            model_name=ModelName.KLING_1,
            image_source=ImageSource(url="http://example.com/image.jpg"),
        )
        response = await virtual_try_on_api.create_task(request)

        # Assertions
        assert isinstance(response, TaskResponse)
        assert response.data.task_id == "task-123"
        assert response.data.task_status == "submitted"
        mock_http_client.post.assert_awaited_once()

    async def test_get_task_status(
        self, virtual_try_on_api: VirtualTryOnAPI, mock_http_client: AsyncMock
    ) -> None:
        """Test getting task status."""
        # Setup mock response
        mock_response = {
            "code": 200,
            "message": "Success",
            "request_id": "req-123",
            "data": {
                "task_id": "task-123",
                "task_status": "processing",
                "created_at": int(datetime.now().timestamp() * 1000),
                "updated_at": int(datetime.now().timestamp() * 1000),
            }
        }
        mock_http_client.get.return_value = Response(
            status_code=200,
            content=json.dumps(mock_response),
        )

        # Call the method
        response = await virtual_try_on_api.get_task_status("task-123")

        # Assertions
        assert isinstance(response, TaskResponse)
        assert response.data.task_id == "task-123"
        assert response.data.task_status == "processing"
        mock_http_client.get.assert_awaited_once()

    async def test_list_tasks(
        self, virtual_try_on_api: VirtualTryOnAPI, mock_http_client: AsyncMock
    ) -> None:
        """Test listing tasks."""
        # Setup mock response
        mock_response = {
            "code": 200,
            "message": "Success",
            "request_id": "req-123",
            "data": [
                {
                    "task_id": "task-123",
                    "task_status": "succeed",
                    "created_at": int(datetime.now().timestamp() * 1000),
                    "updated_at": int(datetime.now().timestamp() * 1000),
                }
            ]
        }
        mock_http_client.get.return_value = Response(
            status_code=200,
            content=json.dumps(mock_response),
        )

        # Call the method
        query = TaskListQuery(page_num=1, page_size=10)
        response = await virtual_try_on_api.list_tasks(query)

        # Assertions
        assert isinstance(response, TaskListResponse)
        assert len(response.data) == 1
        assert response.data[0].task_id == "task-123"
        mock_http_client.get.assert_awaited_once()

    async def test_handle_callback(self) -> None:
        """Test handling a callback."""
        # This would test the callback handler logic
        # Implementation would depend on how callbacks are handled in your application
        pass  # TODO: Implement callback handling tests
