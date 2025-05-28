"""Tests for the Kling AI Lip Sync API client."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from pydantic import ValidationError

from app.core.third_party_integrations.kling.api.lip_sync._exceptions import (
    LipSyncError,
    LipSyncRateLimitError,
    LipSyncValidationError,
)
from app.core.third_party_integrations.kling.api.lip_sync._requests import (
    CreateTaskRequest,
    TaskStatus,
)
from app.core.third_party_integrations.kling.api.lip_sync._responses import (
    TaskData,
    TaskListResponse,
    TaskResponse,
)
from app.core.third_party_integrations.kling.api.lip_sync.lip_sync import LipSyncAPI

# Test data
TEST_TASK_ID = "test_task_123"
TEST_VIDEO_URL = "https://example.com/video.mp4"
TEST_AUDIO_URL = "https://example.com/audio.mp3"
TEST_RESULT_URL = "https://example.com/result.mp4"

# Fixtures
@pytest.fixture
def mock_client():
    """Create a mock httpx.AsyncClient."""
    return AsyncMock(spec=httpx.AsyncClient)


@pytest.fixture
def lip_sync_api(mock_client):
    """Create a LipSyncAPI instance with a mock client."""
    return LipSyncAPI(mock_client)


@pytest.fixture
def task_data():
    """Create sample task data."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "task_id": TEST_TASK_ID,
        "status": TaskStatus.PENDING,
        "created_at": now,
        "updated_at": now,
        "progress": 0.0,
        "result_url": None,
        "error": None,
        "metadata": {},
    }


# Test cases
class TestCreateTask:
    """Test the create_task method."""

    async def test_create_task_success(self, lip_sync_api, mock_client, task_data):
        """Test successful task creation."""
        # Mock the response
        mock_response = AsyncMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"data": task_data}
        mock_client.post.return_value = mock_response

        # Call the method
        request = {
            "video_url": TEST_VIDEO_URL,
            "audio_url": TEST_AUDIO_URL,
        }
        result = await lip_sync_api.create_task(request)

        # Verify the result
        assert isinstance(result, TaskData)
        assert result.task_id == TEST_TASK_ID
        mock_client.post.assert_called_once()

    async def test_create_task_validation_error(self, lip_sync_api):
        """Test task creation with invalid data."""
        with pytest.raises(LipSyncValidationError):
            await lip_sync_api.create_task({"invalid": "data"})

    async def test_create_task_rate_limit(self, lip_sync_api, mock_client):
        """Test rate limiting."""
        # Mock a rate limit response
        mock_response = AsyncMock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "5"}
        mock_response.json.return_value = {
            "code": "rate_limit_exceeded",
            "message": "Rate limit exceeded",
        }
        mock_client.post.return_value = mock_response

        # Should raise after retries
        with pytest.raises(LipSyncRateLimitError):
            await lip_sync_api.create_task(
                {"video_url": TEST_VIDEO_URL, "audio_url": TEST_AUDIO_URL}
            )


class TestGetTask:
    """Test the get_task method."""

    async def test_get_task_success(self, lip_sync_api, mock_client, task_data):
        """Test successful task retrieval."""
        # Mock the response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": task_data}
        mock_client.get.return_value = mock_response

        # Call the method
        result = await lip_sync_api.get_task(TEST_TASK_ID)

        # Verify the result
        assert isinstance(result, TaskData)
        assert result.task_id == TEST_TASK_ID
        mock_client.get.assert_called_once_with(
            f"https://api.klingai.com/v1/lip-sync/tasks/{TEST_TASK_ID}",
            timeout=10.0,
        )

    async def test_get_task_not_found(self, lip_sync_api, mock_client):
        """Test task not found."""
        # Mock a 404 response
        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "code": "not_found",
            "message": "Task not found",
        }
        mock_client.get.return_value = mock_response

        with pytest.raises(LipSyncError) as exc_info:
            await lip_sync_api.get_task("nonexistent_task")
        assert exc_info.value.status_code == 404


class TestListTasks:
    """Test the list_tasks method."""

    async def test_list_tasks_success(self, lip_sync_api, mock_client, task_data):
        """Test successful task listing."""
        # Mock the response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [task_data],
            "total": 1,
            "limit": 10,
            "offset": 0,
        }
        mock_client.get.return_value = mock_response

        # Call the method
        result = await lip_sync_api.list_tasks()

        # Verify the result
        assert isinstance(result, TaskListResponse)
        assert len(result.data) == 1
        assert result.data[0].task_id == TEST_TASK_ID
        mock_client.get.assert_called_once_with(
            "https://api.klingai.com/v1/lip-sync/tasks",
            params={"limit": 10, "offset": 0},
            timeout=10.0,
        )


class TestCancelTask:
    """Test the cancel_task method."""

    async def test_cancel_task_success(self, lip_sync_api, mock_client):
        """Test successful task cancellation."""
        # Mock the response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response

        # Call the method
        result = await lip_sync_api.cancel_task(TEST_TASK_ID)

        # Verify the result
        assert result is True
        mock_client.post.assert_called_once_with(
            f"https://api.klingai.com/v1/lip-sync/tasks/{TEST_TASK_ID}/cancel",
            timeout=10.0,
        )


class TestRequestValidation:
    """Test request validation."""

    def test_create_task_request_validation(self):
        """Test CreateTaskRequest validation."""
        # Valid request
        valid_request = {
            "video_url": TEST_VIDEO_URL,
            "audio_url": TEST_AUDIO_URL,
            "output_format": "mp4",
            "resolution": "720p",
            "fps": 30,
        }
        assert CreateTaskRequest.model_validate(valid_request)

        # Invalid URL
        with pytest.raises(ValidationError):
            CreateTaskRequest.model_validate(
                {"video_url": "not-a-url", "audio_url": TEST_AUDIO_URL}
            )

        # Invalid resolution format
        with pytest.raises(ValidationError):
            CreateTaskRequest.model_validate(
                {
                    "video_url": TEST_VIDEO_URL,
                    "audio_url": TEST_AUDIO_URL,
                    "resolution": "invalid",
                }
            )
