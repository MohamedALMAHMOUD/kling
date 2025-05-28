"""Tests for the Kling AI Image Generation API client."""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch
import pytest
import httpx
import respx

from .. import (
    KlingAIClient,
    ImageGenerationRequest,
    ModelName,
    AspectRatio,
    TaskStatus,
    TaskResponse,
    TaskListResponse,
    TaskCreateResponse,
    APIError,
    RateLimitError,
)
from .._requests import ImageReferenceType


@pytest.fixture
def mock_client() -> KlingAIClient:
    """Create a KlingAIClient instance with a mock HTTP client."""
    return KlingAIClient(api_key="test-api-key", base_url="https://api.test.kling.ai")


@pytest.fixture
def task_response() -> dict:
    """Sample task response data."""
    return {
        "code": 0,
        "message": "success",
        "request_id": "req_1234567890",
        "data": {
            "task_id": "task_1234567890",
            "task_status": "submitted",
            "created_at": int(datetime.now().timestamp() * 1000),
            "updated_at": int(datetime.now().timestamp() * 1000),
        },
    }


@pytest.fixture
def completed_task_response() -> dict:
    """Sample completed task response data."""
    return {
        "code": 0,
        "message": "success",
        "request_id": "req_1234567890",
        "data": {
            "task_id": "task_1234567890",
            "task_status": "succeed",
            "created_at": int(datetime.now().timestamp() * 1000) - 10000,
            "updated_at": int(datetime.now().timestamp() * 1000),
            "task_result": {
                "images": [
                    {
                        "index": 0,
                        "url": "https://example.com/image1.jpg",
                    },
                    {
                        "index": 1,
                        "url": "https://example.com/image2.jpg",
                    },
                ]
            },
        },
    }


@pytest.fixture
def task_list_response() -> dict:
    """Sample task list response data."""
    now = int(datetime.now().timestamp() * 1000)
    return {
        "code": 0,
        "message": "success",
        "request_id": "req_list_1234567890",
        "data": [
            {
                "task_id": "task_1",
                "task_status": "succeed",
                "created_at": now - 20000,
                "updated_at": now - 10000,
                "task_result": {
                    "images": [{"index": 0, "url": "https://example.com/img1.jpg"}]
                },
            },
            {
                "task_id": "task_2",
                "task_status": "processing",
                "created_at": now - 5000,
                "updated_at": now - 1000,
                "task_result": None,
            },
        ],
    }


@pytest.mark.asyncio
async def test_create_image_generation_task(mock_client: KlingAIClient, task_response: dict):
    """Test creating an image generation task."""
    with respx.mock(base_url=mock_client.base_url) as respx_mock:
        # Mock the API response
        respx_mock.post("/v1/images/generations").mock(
            return_value=httpx.Response(200, json=task_response)
        )
        
        # Create a request
        request = ImageGenerationRequest(
            model_name=ModelName.KLING_V1_5,
            prompt="A beautiful sunset over mountains",
            aspect_ratio=AspectRatio.RATIO_16_9,
            n=2,
        )
        
        # Call the API
        response = await mock_client.create_image_generation_task(request)
        
        # Verify the response
        assert isinstance(response, TaskCreateResponse)
        assert response.code == 0
        assert response.message == "success"
        assert response.request_id == "req_1234567890"
        assert response.task_id == "task_1234567890"
        
        # Verify the request
        assert respx_mock.calls.call_count == 1
        request_data = json.loads(respx_mock.calls[0].request.content)
        assert request_data["model_name"] == "kling-v1-5"
        assert request_data["prompt"] == "A beautiful sunset over mountains"
        assert request_data["aspect_ratio"] == "16:9"
        assert request_data["n"] == 2


@pytest.mark.asyncio
async def test_get_task_status(mock_client: KlingAIClient, completed_task_response: dict):
    """Test getting task status."""
    with respx.mock(base_url=mock_client.base_url) as respx_mock:
        # Mock the API response
        task_id = "task_1234567890"
        respx_mock.get(f"/v1/images/generations/{task_id}").mock(
            return_value=httpx.Response(200, json=completed_task_response)
        )
        
        # Call the API
        response = await mock_client.get_task_status(task_id)
        
        # Verify the response
        assert isinstance(response, TaskResponse)
        assert response.task_id == task_id
        assert response.task_status == TaskStatus.SUCCEEDED
        assert len(response.task_result.images) == 2
        assert response.task_result.images[0].url == "https://example.com/image1.jpg"
        assert response.task_result.images[1].url == "https://example.com/image2.jpg"


@pytest.mark.asyncio
async def test_list_tasks(mock_client: KlingAIClient, task_list_response: dict):
    """Test listing tasks with pagination."""
    with respx.mock(base_url=mock_client.base_url) as respx_mock:
        # Mock the API response
        respx_mock.get("/v1/images/generations").mock(
            return_value=httpx.Response(200, json=task_list_response)
        )
        
        # Call the API
        response = await mock_client.list_tasks()
        
        # Verify the response
        assert isinstance(response, TaskListResponse)
        assert len(response.__root__) == 2
        assert response.__root__[0].task_id == "task_1"
        assert response.__root__[0].task_status == TaskStatus.SUCCEEDED
        assert response.__root__[1].task_id == "task_2"
        assert response.__root__[1].task_status == TaskStatus.PROCESSING


@pytest.mark.asyncio
async def test_wait_for_task_completion(mock_client: KlingAIClient):
    """Test waiting for task completion with polling."""
    task_id = "task_1234567890"
    
    # Create responses for different polling attempts
    processing_response = {
        "code": 0,
        "message": "success",
        "request_id": "req_123",
        "data": {
            "task_id": task_id,
            "task_status": "processing",
            "created_at": int(datetime.now().timestamp() * 1000) - 10000,
            "updated_at": int(datetime.now().timestamp() * 1000) - 5000,
        },
    }
    
    completed_response = {
        "code": 0,
        "message": "success",
        "request_id": "req_456",
        "data": {
            "task_id": task_id,
            "task_status": "succeed",
            "created_at": int(datetime.now().timestamp() * 1000) - 10000,
            "updated_at": int(datetime.now().timestamp() * 1000),
            "task_result": {
                "images": [
                    {
                        "index": 0,
                        "url": "https://example.com/image.jpg",
                    }
                ]
            },
        },
    }
    
    with respx.mock(base_url=mock_client.base_url) as respx_mock:
        # First call: processing
        respx_mock.get(f"/v1/images/generations/{task_id}").mock(
            side_effect=[
                httpx.Response(200, json=processing_response),
                httpx.Response(200, json=completed_response),
            ]
        )
        
        # Call with short poll interval and timeout
        response = await mock_client.wait_for_task_completion(
            task_id, poll_interval=0.1, timeout=1.0
        )
        
        # Verify the response
        assert response.task_status == TaskStatus.SUCCEEDED
        assert len(response.task_result.images) == 1
        assert response.task_result.images[0].url == "https://example.com/image.jpg"
        
        # Should have made 2 API calls
        assert respx_mock.calls.call_count == 2


@pytest.mark.asyncio
async def test_rate_limit_handling(mock_client: KlingAIClient):
    """Test that rate limits are handled with retries."""
    task_id = "task_1234567890"
    
    # Rate limit response
    rate_limit_response = {
        "code": 429,
        "message": "Rate limit exceeded",
        "request_id": "req_rate_123",
    }
    
    # Success response after rate limit
    success_response = {
        "code": 0,
        "message": "success",
        "request_id": "req_456",
        "data": {
            "task_id": task_id,
            "task_status": "succeed",
            "created_at": int(datetime.now().timestamp() * 1000) - 10000,
            "updated_at": int(datetime.now().timestamp() * 1000),
            "task_result": {"images": [{"index": 0, "url": "https://example.com/image.jpg"}]},
        },
    }
    
    with respx.mock(base_url=mock_client.base_url) as respx_mock:
        # First call: rate limited, second call: success
        respx_mock.get(f"/v1/images/generations/{task_id}").mock(
            side_effect=[
                httpx.Response(429, json=rate_limit_response),
                httpx.Response(200, json=success_response),
            ]
        )
        
        # Call the API
        response = await mock_client.get_task_status(task_id)
        
        # Verify the response
        assert response.task_status == TaskStatus.SUCCEEDED
        assert len(response.task_result.images) == 1
        
        # Should have made 2 API calls (1 initial + 1 retry)
        assert respx_mock.calls.call_count == 2


@pytest.mark.asyncio
async def test_validation_error_handling(mock_client: KlingAIClient):
    """Test that validation errors are properly raised."""
    # Create an invalid request (missing required 'prompt' field)
    with pytest.raises(ValueError):
        ImageGenerationRequest()  # type: ignore
    
    # Test with invalid model name
    with pytest.raises(ValueError):
        ImageGenerationRequest(
            model_name="invalid-model",  # type: ignore
            prompt="test",
        )
    
    # Test with invalid aspect ratio
    with pytest.raises(ValueError):
        ImageGenerationRequest(
            prompt="test",
            aspect_ratio="invalid-ratio",  # type: ignore
        )


@pytest.mark.asyncio
async def test_singleton_pattern():
    """Test that the client follows the singleton pattern."""
    client1 = KlingAIClient(api_key="test-key-1")
    client2 = KlingAIClient(api_key="test-key-2")
    
    # Both instances should be the same object
    assert client1 is client2
    
    # The second initialization should not change the API key
    assert client1.api_key == "test-key-1"
    assert client2.api_key == "test-key-1"
