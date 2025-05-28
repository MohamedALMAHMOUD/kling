"""Tests for the callback protocol API endpoints."""
import json
from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from ...client import router as client_router
from ...config import KlingConfig
from .. import router as callback_router
from .._requests import CallbackRequest, TaskStatus, TaskInfo, TaskResult
from .._responses import CallbackAckResponse
from .._exceptions import CallbackValidationError, CallbackProcessingError

# Test client setup
client = TestClient(callback_router)

# Fixtures
@pytest.fixture
def sample_callback_data():
    """Sample valid callback data for testing."""
    return {
        "task_id": "task123",
        "task_status": "succeed",
        "task_status_msg": "Task completed successfully",
        "created_at": 1234567890000,
        "task_info": {},
        "task_result": {
            "images": [{"index": 0, "url": "https://example.com/image.jpg"}],
            "videos": [{"id": "vid1", "url": "https://example.com/video.mp4", "duration": "30"}]
        }
    }

# Test cases
@pytest.mark.asyncio
async def test_handle_kling_callback_success(sample_callback_data):
    """Test successful callback handling."""
    # Mock the callback handler
    mock_handler = AsyncMock()
    callback_router.register_callback_handler(mock_handler)
    
    # Make the request
    response = client.post("/kling", json=sample_callback_data)
    
    # Check response
    assert response.status_code == status.HTTP_202_ACCEPTED
    response_data = response.json()
    assert response_data["status"] == "success"
    assert response_data["task_id"] == "task123"
    
    # Verify the handler was called with the correct data
    mock_handler.assert_called_once()
    callback = mock_handler.call_args[0][0]
    assert isinstance(callback, CallbackRequest)
    assert callback.task_id == "task123"
    assert callback.task_status == TaskStatus.SUCCEED

@pytest.mark.asyncio
async def test_handle_kling_callback_validation_error():
    """Test callback with invalid data."""
    # Invalid data (missing required fields)
    response = client.post("/kling", json={"invalid": "data"})
    
    # Should return 422 Unprocessable Entity
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    error_data = response.json()
    assert error_data["status"] == "error"
    assert "validation_error" in error_data["error"]
    assert "validation_errors" in error_data["details"]

@pytest.mark.asyncio
async def test_handle_kling_callback_processing_error(sample_callback_data):
    """Test callback that fails during processing."""
    # Mock the callback handler to raise an exception
    async def failing_handler(_):
        raise CallbackProcessingError("Processing failed")
    
    callback_router.register_callback_handler(failing_handler)
    
    # Make the request
    response = client.post("/kling", json=sample_callback_data)
    
    # Should return 500 Internal Server Error
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    error_data = response.json()
    assert error_data["status"] == "error"
    assert "CallbackProcessingError" in error_data["error"]

@pytest.mark.asyncio
async def test_verify_callback_signature():
    """Test callback signature verification."""
    # This is a simple test since we're not implementing actual signature verification yet
    assert callback_router.verify_callback_signature(
        request=MagicMock(),
        secret="test-secret"
    ) is True

def test_register_callback_handler():
    """Test registering a callback handler."""
    # Reset the handler
    callback_router.register_callback_handler(None)
    
    # Register a test handler
    test_handler = lambda x: x
    callback_router.register_callback_handler(test_handler)
    
    # The handler should be registered
    assert callback_router._callback_handler is test_handler
    
    # Clean up
    callback_router.register_callback_handler(None)
