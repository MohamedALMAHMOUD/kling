"""Test configuration and fixtures for the Kling AI Video Effects API client."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import httpx
import pytest

from app.core.third_party_integrations.kling.api.video_effects._requests import (
    CreateVideoEffectRequest,
    EffectType,
    TaskStatus,
    VideoQuality,
)
from app.core.third_party_integrations.kling.api.video_effects._responses import (
    CancelTaskResponse,
    CreateTaskResponse,
    GetTaskResponse,
    ListTasksResponse,
    TaskData,
)

# Test data
TEST_TASK_ID = "test_task_123"
TEST_VIDEO_URL = "https://example.com/video.mp4"
TEST_STYLE_URL = "https://example.com/style.jpg"
TEST_RESULT_URL = "https://example.com/result.mp4"


@pytest.fixture
def mock_client():
    """Create a mock httpx.AsyncClient."""
    return AsyncMock(spec=httpx.AsyncClient)


@pytest.fixture
def video_effects_api(mock_client):
    """Create a VideoEffectsAPI instance with a mock client."""
    from app.core.third_party_integrations.kling.api.video_effects import VideoEffectsAPI
    return VideoEffectsAPI(mock_client, api_key="test_api_key")


@pytest.fixture
def task_data():
    """Create sample task data."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "id": TEST_TASK_ID,
        "status": TaskStatus.PROCESSING,
        "effect_type": EffectType.STYLE_TRANSFER,
        "video_url": TEST_VIDEO_URL,
        "result_url": None,
        "progress": 50,
        "created_at": now,
        "updated_at": now,
        "error": None,
        "metadata": {"test": "value"},
    }


@pytest.fixture
def create_task_response(task_data):
    """Create a sample create task response."""
    return {
        "task_id": task_data["id"],
        "status": task_data["status"],
        "created_at": task_data["created_at"],
    }


@pytest.fixture
def list_tasks_response(task_data):
    """Create a sample list tasks response."""
    return {
        "tasks": [task_data],
        "next_cursor": "next_page_token",
        "has_more": True,
    }


@pytest.fixture
def cancel_task_response(task_data):
    """Create a sample cancel task response."""
    return {
        "task_id": task_data["id"],
        "status": TaskStatus.CANCELLED,
        "cancelled_at": datetime.now(timezone.utc).isoformat(),
    }
