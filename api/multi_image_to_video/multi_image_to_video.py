"""
Multi-Image to Video API client for Kling AI.

This module provides an asynchronous client for interacting with the Kling AI
Multi-Image to Video API, enabling video generation from multiple input images
with various customization options.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from pydantic import HttpUrl

from ...client import KlingClient
from ...config import KlingConfig
from ...models.multi_image_to_video import MultiImageToVideoTask
from ._exceptions import (
    MultiImageToVideoTaskError,
    handle_api_error,
)
from ._requests import MultiImageToVideoRequest
from ._response import TaskResponse, TaskStatus

logger = logging.getLogger(__name__)


class MultiImageToVideoAPI:
    """
    API route client for Kling AI Multi-Image to Video endpoints.

    This class should be instantiated by the main KlingClient singleton and accessed via `client.multi_image_to_video`.
    Provides methods to create/manage multi-image-to-video tasks, check task status, and handle errors with strong typing and validation.
    """
    def __init__(self, client: KlingClient) -> None:
        """
        Args:
            client: The singleton KlingClient instance
        """
        self._client = client
        self._http = client._client  # httpx.AsyncClient
        self.base_url = client.base_url

    async def create_video(self, request: MultiImageToVideoRequest) -> MultiImageToVideoTask:
        """
        Create a new multi-image to video generation task.

        Args:
            request: MultiImageToVideoRequest instance with validated parameters

        Returns:
            MultiImageToVideoTask: The created video task response

        Raises:
            MultiImageToVideoAPIError: If the API request fails
        """
        try:
            payload = request.model_dump()
            resp = await self._http.post(f"{self.base_url}/v1/videos/multi-image-to-video", json=payload)
            resp.raise_for_status()
            return MultiImageToVideoTask.model_validate(resp.json())
        except Exception as e:
            raise handle_api_error(e) from e

    async def get_status(self, task_id: str) -> TaskResponse:
        """
        Get the status of a multi-image to video generation task.

        Args:
            task_id: The ID of the video generation task

        Returns:
            TaskResponse: The task status response

        Raises:
            MultiImageToVideoAPIError: If the API request fails
        """
        try:
            resp = await self._http.get(f"{self.base_url}/v1/videos/multi-image-to-video/{task_id}")
            resp.raise_for_status()
            return TaskResponse.model_validate(resp.json())
        except Exception as e:
            raise handle_api_error(e) from e

    async def wait_for_completion(
        self,
        task_id: str,
        poll_interval: float = 5.0,
        timeout: float | None = 300.0,
    ) -> TaskResponse:
        """
        Wait for a multi-image to video task to complete.

        Args:
            task_id: ID of the task to wait for
            poll_interval: Time between status checks in seconds
            timeout: Maximum time to wait in seconds (None for no timeout)

        Returns:
            TaskResponse with the final status and results

        Raises:
            TimeoutError: If the task doesn't complete before timeout
            MultiImageToVideoTaskError: If the task fails
            MultiImageToVideoAPIError: For other API errors
        """
        import asyncio
        start_time = asyncio.get_event_loop().time()
        while True:
            try:
                status = await self.get_status(task_id)
            except Exception as e:
                raise handle_api_error(e) from e
            if status.task_status in (TaskStatus.SUCCEED, TaskStatus.FAILED):
                if status.task_status == TaskStatus.FAILED:
                    raise MultiImageToVideoTaskError(
                        f"Task {task_id} failed: {getattr(status, 'task_status_msg', 'No details')}"
                    )
                return status
            if timeout is not None and (asyncio.get_event_loop().time() - start_time) > timeout:
                raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")
            await asyncio.sleep(poll_interval)

# Export for main client registration
__all__ = ["MultiImageToVideoAPI"]

# Re-export commonly used types and models
__all__ = [
    'MultiImageToVideoAPI',
    'TaskResponse',
    'TaskStatus',
    'MultiImageToVideoTask',
]


async def generate_multi_image_video(
    image_list: list[dict[str, str]],
    api_key: str,
    prompt: str | None = None,
    negative_prompt: str | None = None,
    model_name: str = "kling-v1-6",
    mode: str = "std",
    duration: int = 5,
    aspect_ratio: str = "16:9",
    wait: bool = True,
    poll_interval: float = 5.0,
    timeout: float | None = 300.0,
) -> tuple[TaskResponse, bytes | None]:
    """Convenience function to generate a video from multiple images with minimal setup.

    This creates a new MultiImageToVideoAPI client, generates a video, and returns
    the result, automatically cleaning up resources.

    Args:
        image_list: List of image items, each containing 'url' or 'base64' key
        api_key: Kling AI API key
        prompt: Text prompt describing the desired video (optional)
        negative_prompt: Text describing what to avoid in the video (optional)
        model_name: Name of the model to use (default: "kling-v1-6")
        mode: Video generation mode ("std" or "pro")
        duration: Duration of the video in seconds (5 or 10)
        aspect_ratio: Aspect ratio of the generated video ("16:9", "9:16", or "1:1")
        wait: Whether to wait for video generation to complete
        poll_interval: Time between status checks in seconds (if waiting)
        timeout: Maximum time to wait in seconds (if waiting, None for no timeout)
        
    Returns:
        Tuple of (TaskResponse, video_bytes if wait=True else None)

    Raises:
        TimeoutError: If waiting and the task doesn't complete before timeout
        MultiImageToVideoTaskError: If the task fails
        MultiImageToVideoAPIError: For other API errors
    """
    config = KlingConfig(api_key=api_key)
    async with MultiImageToVideoAPI(config) as client:
        response = await client.create(
            image_list=image_list,
            prompt=prompt,
            negative_prompt=negative_prompt,
            model_name=model_name,
            mode=mode,
            duration=duration,
            aspect_ratio=aspect_ratio,
        )
        
        if not wait:
            return response, None
            
        final_status = await client.wait_for_completion(
            task_id=response.task_id,
            poll_interval=poll_interval,
            timeout=timeout,
        )
        
        if final_status.task_result and final_status.task_result.videos:
            video_url = final_status.task_result.videos[0].url
            video_data = await client.download_video(video_url)
            return final_status, video_data
            
        return final_status, None
