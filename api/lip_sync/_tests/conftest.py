"""Pytest configuration for lip sync tests."""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
import httpx

from app.core.third_party_integrations.kling.api.lip_sync.lip_sync import LipSyncAPI


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client with common methods."""
    return AsyncMock(spec=httpx.AsyncClient)


@pytest_asyncio.fixture
async def lip_sync_api(mock_http_client):
    """Create a LipSyncAPI instance with a mock HTTP client."""
    return LipSyncAPI(mock_http_client)


@pytest.fixture
def sample_task_data():
    """Return sample task data for testing."""
    from datetime import datetime, timezone
    
    return {
        "task_id": "test_task_123",
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "progress": 0.0,
        "result_url": None,
        "error": None,
        "metadata": {},
    }
