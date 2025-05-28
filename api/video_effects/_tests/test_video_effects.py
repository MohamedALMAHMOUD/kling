"""Tests for the Kling AI Video Effects API client."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from pydantic import ValidationError

from app.core.third_party_integrations.kling.api.video_effects._exceptions import (
    VideoEffectsError,
    VideoEffectsRateLimitError,
    VideoEffectsValidationError,
)
from app.core.third_party_integrations.kling.api.video_effects._requests import (
    CreateVideoEffectRequest,
    TaskStatus,
    EffectType,
    VideoQuality,
)
from app.core.third_party_integrations.kling.api.video_effects._responses import (
    TaskData,
    CreateTaskResponse,
    GetTaskResponse,
    ListTasksResponse,
    CancelTaskResponse,
)


class TestCreateTask:
    """Test the create_task method."""
    
    async def test_create_task_success(
        self,
        video_effects_api,
        mock_client,
        create_task_response,
    ):
        """Test successful task creation."""
        # Mock the API response
        mock_client.request.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value=create_task_response),
        )
        
        # Call the method
        response = await video_effects_api.create_task(
            video_url="https://example.com/video.mp4",
            effect_type=EffectType.STYLE_TRANSFER,
            style_reference="https://example.com/style.jpg",
            intensity=0.8,
            quality=VideoQuality.HIGH,
            metadata={"test": "value"},
        )
        
        # Assert the response
        assert isinstance(response, CreateTaskResponse)
        assert response.task_id == create_task_response["task_id"]
        assert response.status == create_task_response["status"]
        
        # Verify the request
        mock_client.request.assert_awaited_once()
        args, kwargs = mock_client.request.await_args
        assert args[0] == "POST"
        assert args[1].endswith("/tasks")
        
        # Verify the request body
        request_body = json.loads(kwargs["content"])
        assert request_body["video_url"] == "https://example.com/video.mp4"
        assert request_body["effect_type"] == "style_transfer"
        assert request_body["style_reference"] == "https://example.com/style.jpg"
        assert request_body["intensity"] == 0.8
        assert request_body["quality"] == "high"
        assert request_body["metadata"] == {"test": "value"}
    
    async def test_create_task_validation_error(self, video_effects_api):
        """Test task creation with invalid data."""
        with pytest.raises(ValidationError):
            await video_effects_api.create_task(
                video_url="not-a-url",
                effect_type="invalid_effect",
            )
    
    async def test_create_task_rate_limit(
        self,
        video_effects_api,
        mock_client,
    ):
        """Test rate limiting."""
        # Mock rate limit response
        mock_client.request.return_value = AsyncMock(
            status_code=429,
            headers={"Retry-After": "1"},
            json=AsyncMock(return_value={"message": "Rate limit exceeded"}),
        )
        
        # Should raise rate limit error
        with pytest.raises(VideoEffectsRateLimitError):
            await video_effects_api.create_task(
                video_url="https://example.com/video.mp4",
                effect_type=EffectType.STYLE_TRANSFER,
            )


class TestGetTask:
    """Test the get_task method."""
    
    async def test_get_task_success(
        self,
        video_effects_api,
        mock_client,
        task_data,
    ):
        """Test successful task retrieval."""
        # Mock the API response
        mock_client.request.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value=task_data),
        )
        
        # Call the method
        task_id = "test_task_123"
        response = await video_effects_api.get_task(task_id)
        
        # Assert the response
        assert isinstance(response, GetTaskResponse)
        assert response.id == task_id
        assert response.status == TaskStatus.PROCESSING
        
        # Verify the request
        mock_client.request.assert_awaited_once_with(
            "GET",
            f"{video_effects_api.base_url}/tasks/{task_id}",
            headers=video_effects_api._headers,
            timeout=video_effects_api.timeout,
        )
    
    async def test_get_task_not_found(self, video_effects_api, mock_client):
        """Test task not found."""
        # Mock 404 response
        mock_client.request.return_value = AsyncMock(
            status_code=404,
            json=AsyncMock(return_value={"message": "Task not found"}),
        )
        
        # Should raise not found error
        with pytest.raises(VideoEffectsError) as exc_info:
            await video_effects_api.get_task("nonexistent_task")
        
        assert "not found" in str(exc_info.value).lower()


class TestListTasks:
    """Test the list_tasks method."""
    
    async def test_list_tasks_success(
        self,
        video_effects_api,
        mock_client,
        list_tasks_response,
    ):
        """Test successful task listing."""
        # Mock the API response
        mock_client.request.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value=list_tasks_response),
        )
        
        # Call the method with filters
        response = await video_effects_api.list_tasks(
            status=TaskStatus.PROCESSING,
            limit=10,
            cursor="next_page_token",
        )
        
        # Assert the response
        assert isinstance(response, ListTasksResponse)
        assert len(response.tasks) == 1
        assert response.tasks[0].id == list_tasks_response["tasks"][0]["id"]
        assert response.next_cursor == "next_page_token"
        assert response.has_more is True
        
        # Verify the request
        mock_client.request.assert_awaited_once()
        args, kwargs = mock_client.request.await_args
        assert args[0] == "GET"
        assert args[1].endswith("/tasks")
        assert kwargs["params"] == {
            "status": "processing",
            "limit": 10,
            "cursor": "next_page_token",
        }


class TestCancelTask:
    """Test the cancel_task method."""
    
    async def test_cancel_task_success(
        self,
        video_effects_api,
        mock_client,
        cancel_task_response,
    ):
        """Test successful task cancellation."""
        # Mock the API response
        mock_client.request.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value=cancel_task_response),
        )
        
        # Call the method
        task_id = "test_task_123"
        response = await video_effects_api.cancel_task(task_id)
        
        # Assert the response
        assert isinstance(response, CancelTaskResponse)
        assert response.task_id == task_id
        assert response.status == TaskStatus.CANCELLED
        
        # Verify the request
        mock_client.request.assert_awaited_once_with(
            "POST",
            f"{video_effects_api.base_url}/tasks/{task_id}/cancel",
            headers=video_effects_api._headers,
            timeout=video_effects_api.timeout,
        )


class TestRequestValidation:
    """Test request validation."""
    
    def test_create_task_request_validation(self):
        """Test CreateVideoEffectRequest validation."""
        # Valid request
        valid_request = CreateVideoEffectRequest(
            video_url="https://example.com/video.mp4",
            effect_type=EffectType.STYLE_TRANSFER,
            style_reference="https://example.com/style.jpg",
        )
        assert valid_request.video_url == "https://example.com/video.mp4"
        assert valid_request.effect_type == EffectType.STYLE_TRANSFER
        
        # Invalid intensity
        with pytest.raises(ValidationError):
            CreateVideoEffectRequest(
                video_url="https://example.com/video.mp4",
                effect_type=EffectType.STYLE_TRANSFER,
                intensity=1.5,  # Out of range
            )
        
        # Missing required field
        with pytest.raises(ValidationError):
            CreateVideoEffectRequest(
                effect_type=EffectType.STYLE_TRANSFER,
                # Missing video_url
            )
        
        # Invalid URL
        with pytest.raises(ValidationError):
            CreateVideoEffectRequest(
                video_url="not-a-url",
                effect_type=EffectType.STYLE_TRANSFER,
            )
