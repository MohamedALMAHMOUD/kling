"""
Test configuration and fixtures for Virtual Try-On API tests.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from app.core.third_party_integrations.kling.api.virtual_try_on.virtual_try_on import VirtualTryOnAPI


@pytest.fixture
def mock_http_client() -> AsyncMock:
    """Create a mock HTTP client for testing."""
    return AsyncMock()


@pytest.fixture
def virtual_try_on_api(mock_http_client: AsyncMock) -> VirtualTryOnAPI:
    """Create a VirtualTryOnAPI instance with a mock HTTP client for testing."""
    return VirtualTryOnAPI("test-api-key", http_client=mock_http_client)
