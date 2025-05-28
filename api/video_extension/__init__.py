"""
Kling AI Video Extension API client.

This module provides an async client for interacting with the Kling AI Video Extension API,
allowing you to extend the duration of existing videos with AI-generated content.

Example:
    ```python
    from kling import KlingClient
    from kling.api.video_extension import VideoExtensionRequest
    
    async with KlingClient(api_key="your-api-key") as client:
        # Create a video extension task
        request = VideoExtensionRequest(
            video_id="video_123",
            prompt="A beautiful sunset over mountains",
            cfg_scale=0.7
        )
        response = await client.video_extension.create_task(request)
        print(f"Created task: {response.data.task_id}")
        
        # Check task status
        status = await client.video_extension.get_task(response.data.task_id)
        print(f"Task status: {status.data.task_status}")
    ```
"""
from ._exceptions import (
    VideoExtensionError,
    VideoExtensionValidationError,
    VideoExtensionRateLimitError,
    VideoExtensionNotFoundError,
    VideoExtensionServerError,
    VideoExtensionTimeoutError,
    VideoExtensionAuthenticationError,
    handle_video_extension_error,
)
from ._requests import VideoExtensionRequest, TaskListQueryParams, TaskStatus
from ._responses import (
    VideoExtensionResponse,
    TaskStatusResponse,
    TaskStatusData,
    VideoInfo,
    VideoResult,
    TaskResult,
    TaskInfo,
)
from .video_extension import VideoExtensionAPI

__all__ = [
    # Main client
    "VideoExtensionAPI",
    
    # Requests
    "VideoExtensionRequest",
    "TaskListQueryParams",
    "TaskStatus",
    
    # Responses
    "VideoExtensionResponse",
    "TaskStatusResponse",
    "TaskStatusData",
    "VideoInfo",
    "VideoResult",
    "TaskResult",
    "TaskInfo",
    
    # Exceptions
    "VideoExtensionError",
    "VideoExtensionValidationError",
    "VideoExtensionRateLimitError",
    "VideoExtensionNotFoundError",
    "VideoExtensionServerError",
    "VideoExtensionTimeoutError",
    "VideoExtensionAuthenticationError",
    "handle_video_extension_error",
]
