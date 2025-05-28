"""Kling AI Video Effects API client.

This module provides a client for interacting with the Kling AI Video Effects API.

Example:
    ```python
    import httpx
    from app.core.third_party_integrations.kling.api.video_effects import VideoEffectsAPI
    
    async with httpx.AsyncClient() as client:
        api = VideoEffectsAPI(client, api_key="your-api-key")
        
        # Create a new task
        task = await api.create_task(
            video_url="https://example.com/video.mp4",
            effect_type="style_transfer",
            style_reference="https://example.com/style.jpg"
        )
        
        # Check task status
        status = await api.get_task(task.task_id)
        print(f"Task status: {status.status}")
    ```
"""
from __future__ import annotations

from .video_effects import VideoEffectsAPI
from ._requests import CreateVideoEffectRequest, ListTasksRequest, TaskStatus, EffectType, VideoQuality
from ._responses import CreateTaskResponse, GetTaskResponse, ListTasksResponse, CancelTaskResponse
from ._exceptions import (
    VideoEffectsError,
    VideoEffectsValidationError,
    VideoEffectsRateLimitError,
    VideoEffectsNotFoundError,
    VideoEffectsUnauthorizedError,
    VideoEffectsServerError,
    VideoEffectsTimeoutError,
    VideoEffectsConnectionError,
)

__all__ = [
    # Main client
    "VideoEffectsAPI",
    
    # Request models
    "CreateVideoEffectRequest",
    "ListTasksRequest",
    "TaskStatus",
    "EffectType",
    "VideoQuality",
    
    # Response models
    "CreateTaskResponse",
    "GetTaskResponse",
    "ListTasksResponse",
    "CancelTaskResponse",
    
    # Exceptions
    "VideoEffectsError",
    "VideoEffectsValidationError",
    "VideoEffectsRateLimitError",
    "VideoEffectsNotFoundError",
    "VideoEffectsUnauthorizedError",
    "VideoEffectsServerError",
    "VideoEffectsTimeoutError",
    "VideoEffectsConnectionError",
]
