"""Tests for callback protocol models."""
import pytest
from datetime import datetime
from pydantic import ValidationError

from .._requests import (
    CallbackRequest,
    TaskStatus,
    ParentVideo,
    TaskInfo,
    ImageResult,
    VideoResult,
    TaskResult,
)


def test_task_status_enum():
    """Test that TaskStatus enum values are correct."""
    assert TaskStatus.SUBMITTED == "submitted"
    assert TaskStatus.PROCESSING == "processing"
    assert TaskStatus.SUCCEED == "succeed"
    assert TaskStatus.FAILED == "failed"


def test_parent_video_validation():
    """Test ParentVideo model validation."""
    # Valid data
    video = ParentVideo(
        id="video123",
        url="https://example.com/video.mp4",
        duration="120"
    )
    assert video.id == "video123"
    assert str(video.url) == "https://example.com/video.mp4"
    assert video.duration == "120"

    # Invalid URL
    with pytest.raises(ValidationError):
        ParentVideo(
            id="video123",
            url="not-a-url",
            duration="120"
        )


def test_callback_request_validation():
    """Test CallbackRequest model validation."""
    # Minimal valid request
    request_data = {
        "task_id": "task123",
        "task_status": "submitted",
        "created_at": 1234567890000,
        "task_info": {}
    }
    callback = CallbackRequest(**request_data)
    assert callback.task_id == "task123"
    assert callback.task_status == TaskStatus.SUBMITTED
    assert callback.created_at == 1234567890000
    assert callback.task_info is not None

    # Full request with all fields
    request_data = {
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
    callback = CallbackRequest(**request_data)
    assert len(callback.task_result.images) == 2
    assert len(callback.task_result.videos) == 1
    assert callback.task_result.videos[0].id == "video123"

    # Test invalid status
    with pytest.raises(ValidationError):
        request_data["task_status"] = "invalid_status"
        CallbackRequest(**request_data)


def test_task_result_validation():
    """Test TaskResult model validation."""
    # Empty result
    result = TaskResult()
    assert result.images is None
    assert result.videos is None

    # With images
    result = TaskResult(
        images=[
            {"index": 0, "url": "https://example.com/img1.jpg"},
            {"index": 1, "url": "https://example.com/img2.jpg"}
        ]
    )
    assert len(result.images) == 2
    assert result.images[0].index == 0
    assert str(result.images[1].url) == "https://example.com/img2.jpg"

    # With videos
    result = TaskResult(
        videos=[
            {
                "id": "vid1",
                "url": "https://example.com/vid1.mp4",
                "duration": "30"
            }
        ]
    )
    assert len(result.videos) == 1
    assert result.videos[0].id == "vid1"
    assert result.videos[0].duration == "30"


def test_task_info_validation():
    """Test TaskInfo model validation."""
    # Empty task info
    info = TaskInfo()
    assert info.parent_video is None
    assert info.external_task_id is None

    # With parent video
    info = TaskInfo(
        parent_video={
            "id": "parent123",
            "url": "https://example.com/parent.mp4",
            "duration": "60"
        },
        external_task_id="user-ref-456"
    )
    assert info.parent_video.id == "parent123"
    assert info.external_task_id == "user-ref-456"


def test_image_result_validation():
    """Test ImageResult model validation."""
    # Valid image result
    img = ImageResult(index=0, url="https://example.com/image.jpg")
    assert img.index == 0
    assert str(img.url) == "https://example.com/image.jpg"

    # Missing required fields
    with pytest.raises(ValidationError):
        ImageResult(index=0)  # Missing URL
    
    with pytest.raises(ValidationError):
        ImageResult(url="https://example.com/image.jpg")  # Missing index


def test_video_result_validation():
    """Test VideoResult model validation."""
    # Valid video result
    video = VideoResult(
        id="vid123",
        url="https://example.com/video.mp4",
        duration="30"
    )
    assert video.id == "vid123"
    assert str(video.url) == "https://example.com/video.mp4"
    assert video.duration == "30"

    # Missing required fields
    with pytest.raises(ValidationError):
        VideoResult(id="vid123", url="https://example.com/video.mp4")  # Missing duration
    
    with pytest.raises(ValidationError):
        VideoResult(id="vid123", duration="30")  # Missing URL
