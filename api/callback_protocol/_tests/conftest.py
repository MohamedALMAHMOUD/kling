"""Pytest configuration and fixtures for callback protocol tests."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ... import router as callback_router

# Create a test app with the router
@pytest.fixture
def app():
    """Create a test FastAPI app with the callback router."""
    app = FastAPI()
    app.include_router(callback_router)
    return app


@pytest.fixture
def client(app):
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_callback_data():
    """Sample valid callback data for testing."""
    return {
        "task_id": "task123",
        "task_status": "succeed",
        "task_status_msg": "Task completed successfully",
        "created_at": 1234567890000,
        "task_info": {
            "parent_video": {
                "id": "parent123",
                "url": "https://example.com/parent.mp4",
                "duration": "60"
            },
            "external_task_id": "user-ref-456"
        },
        "task_result": {
            "images": [
                {"index": 0, "url": "https://example.com/image1.jpg"},
                {"index": 1, "url": "https://example.com/image2.jpg"}
            ],
            "videos": [
                {
                    "id": "video123",
                    "url": "https://example.com/video.mp4",
                    "duration": "30"
                }
            ]
        }
    }


@pytest.fixture
def minimal_callback_data():
    """Minimal valid callback data for testing."""
    return {
        "task_id": "task123",
        "task_status": "submitted",
        "created_at": 1234567890000,
        "task_info": {}
    }
