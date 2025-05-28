"""
Text-to-Video API client for Kling AI.

This module provides an asynchronous client for interacting with the Kling AI
Text-to-Video API, enabling video generation from text prompts with various
customization options.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

from pydantic import HttpUrl

from ...client import KlingClient
from ...config import KlingConfig
from ...models.text_to_video import TextToVideoTask
from ._exceptions import TaskFailedError, handle_api_error
from ._requests import KlingAPITextToVideoClient
from ._response import TaskResponse, TaskStatus


class TextToVideoAPI:
    """
    API route client for Kling AI Text-to-Video endpoints.

    This class should be instantiated by the main KlingClient singleton and accessed via `client.text_to_video`.
    """
    def __init__(self, client: KlingClient) -> None:
        """
        Args:
            client: The singleton KlingClient instance
        """
        self._client = client
        self._http = client._client  # httpx.AsyncClient
        self.base_url = client.base_url

    async def create_video(self, prompt: str, duration: int = 5, **kwargs) -> TaskResponse:
        """Create a new video generation task.

        Args:
            prompt: Text prompt for video generation
            duration: Duration of the video in seconds (default: 5)
            **kwargs: Additional API parameters

        Returns:
            TaskResponse: The created video task response
        """
        data = {"prompt": prompt, "duration": duration, **kwargs}
        try:
            resp = await self._http.post(f"{self.base_url}/v1/videos/text2video", json=data)
            resp.raise_for_status()
            return TaskResponse.model_validate(resp.json())
        except Exception as e:
            raise handle_api_error(e)

    async def get_status(self, task_id: str) -> TaskResponse:
        """Get the status of a video generation task.

        Args:
            task_id: The ID of the video generation task

        Returns:
            TaskResponse: The task status response
        """
        try:
            resp = await self._http.get(f"{self.base_url}/v1/videos/text2video/{task_id}")
            resp.raise_for_status()
            return TaskResponse.model_validate(resp.json())
        except Exception as e:
            raise handle_api_error(e)

# Export for main client registration
__all__ = ["TextToVideoAPI"]

logger = logging.getLogger(__name__)

# Re-export commonly used types and models
__all__ = [
    'TextToVideoAPI',
    'TaskResponse',
    'TaskStatus',
    'TextToVideoTask',
]


class TextToVideoAPI:
    """
    Client for interacting with the Kling AI Text-to-Video API.
    
    This client provides methods to create, monitor, and manage text-to-video
    generation tasks with the Kling AI API.
    """

    def __init__(self, config: KlingConfig) -> None:
        """Initialize the Text-to-Video API client.
        
        Args:
            config: KlingConfig instance with API configuration
        """
        self.config = config
        self._client: Optional[KlingAPITextToVideoClient] = None

    async def __aenter__(self) -> "TextToVideoAPI":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    @property
    def client(self) -> KlingAPITextToVideoClient:
        """Lazy initialization of the HTTP client."""
        if self._client is None:
            self._client = KlingAPITextToVideoClient(self.config)
        return self._client

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client:
            await self._client.close()
            self._client = None

    async def create(
        self,
        prompt: str,
        negative_prompt: str | None = None,
        model_name: str = "kling-v1",
        cfg_scale: float = 0.5,
        mode: str = "standard",
        camera_control: dict | None = None,
        aspect_ratio: str = "16:9",
        duration: int = 5,
        callback_url: HttpUrl | str | None = None,
        external_task_id: str | None = None,
    ) -> TaskResponse:
        """Create a new text-to-video generation task.
        
        Args:
            prompt: Text prompt describing the desired video
            negative_prompt: Text describing what to avoid in the video
            model_name: Name of the model to use (default: "kling-v1")
            cfg_scale: Controls how closely to follow the prompt (0.0 to 1.0)
            mode: Video generation mode ("standard" or "professional")
            camera_control: Camera movement configuration
            aspect_ratio: Aspect ratio of the generated video (e.g., "16:9")
            duration: Duration of the video in seconds (5 or 10)
            callback_url: URL to receive task status updates
            external_task_id: Custom ID for tracking the task
            
        Returns:
            TaskResponse containing task information
            
        Raises:
            TaskFailedError: If the task fails
            Exception: For other API errors
        """
        try:
            response = await self.client.create_task(
                prompt=prompt,
                negative_prompt=negative_prompt,
                model_name=model_name,
                cfg_scale=cfg_scale,
                mode=mode,
                camera_control=camera_control,
                aspect_ratio=aspect_ratio,
                duration=duration,
                callback_url=callback_url,
                external_task_id=external_task_id,
            )
            return TaskResponse(**response)
        except Exception as exc:
            logger.error("Failed to create text-to-video task: %s", exc)
            raise handle_api_error(exc) from exc

    async def get_status(self, task_id: str) -> TaskResponse:
        """Get the status of a text-to-video task.
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            TaskResponse with current status and results
            
        Raises:
            TaskFailedError: If the task fails
            Exception: For other API errors
        """
        try:
            response = await self.client.get_task_status(task_id)
            return TaskResponse(**response)
        except Exception as exc:
            logger.error("Failed to get task status for %s: %s", task_id, exc)
            raise handle_api_error(exc) from exc

    async def wait_for_completion(
        self,
        task_id: str,
        poll_interval: float = 5.0,
        timeout: float | None = 300.0,
    ) -> TaskResponse:
        """Wait for a task to complete by polling its status.
        
        Args:
            task_id: ID of the task to monitor
            poll_interval: Time between status checks in seconds
            timeout: Maximum time to wait in seconds (None for no timeout)
            
        Returns:
            TaskResponse with the final status and results
            
        Raises:
            TimeoutError: If the task doesn't complete before timeout
            TaskFailedError: If the task fails
            Exception: For other API errors
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            status = await self.get_status(task_id)
            
            if status.task_status in (TaskStatus.SUCCEEDED, TaskStatus.FAILED):
                if status.task_status == TaskStatus.FAILED:
                    error_msg = status.task_status_msg or "Task failed without details"
                    raise TaskFailedError(
                        f"Task {task_id} failed: {error_msg}",
                        task_id=task_id,
                        status=status,
                    )
                return status
                
            if timeout is not None and (asyncio.get_event_loop().time() - start_time) > timeout:
                raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")
                
            await asyncio.sleep(poll_interval)

    async def download_video(self, url: str) -> bytes:
        """Download a generated video from a URL.
        
        Args:
            url: URL of the video to download
            
        Returns:
            Video content as bytes
            
        Raises:
            Exception: If the download fails
        """
        try:
            async with self.client.client.stream("GET", url) as response:
                response.raise_for_status()
                return await response.aread()
        except Exception as exc:
            logger.error("Failed to download video from %s: %s", url, exc)
            raise Exception(f"Failed to download video: {exc}") from exc

    async def list_tasks(
        self,
        page: int = 1,
        page_size: int = 30,
    ) -> list[TaskResponse]:
        """List all text-to-video tasks with pagination.
        
        Args:
            page: Page number (1-based)
            page_size: Number of tasks per page (1-500)
            
        Returns:
            List of TaskResponse objects
            
        Raises:
            Exception: If the request fails
        """
        try:
            response = await self.client.list_tasks(page=page, page_size=page_size)
            return [TaskResponse(**task) for task in response.get("data", [])]
        except Exception as exc:
            logger.error("Failed to list tasks: %s", exc)
            raise handle_api_error(exc) from exc

    async def generate(
        self,
        prompt: str,
        negative_prompt: str | None = None,
        model_name: str = "kling-v1",
        cfg_scale: float = 0.5,
        mode: str = "standard",
        camera_control: dict | None = None,
        aspect_ratio: str = "16:9",
        duration: int = 5,
        wait: bool = True,
        poll_interval: float = 5.0,
        timeout: float | None = 300.0,
    ) -> tuple[TaskResponse, bytes | None]:
        """Generate a video from text and optionally wait for completion.
        
        This is a convenience method that combines create() and wait_for_completion()
        into a single call.
        
        Args:
            prompt: Text prompt describing the desired video
            negative_prompt: Text describing what to avoid in the video
            model_name: Name of the model to use (default: "kling-v1")
            cfg_scale: Controls how closely to follow the prompt (0.0 to 1.0)
            mode: Video generation mode ("standard" or "professional")
            camera_control: Camera movement configuration
            aspect_ratio: Aspect ratio of the generated video (e.g., "16:9")
            duration: Duration of the video in seconds (5 or 10)
            wait: Whether to wait for video generation to complete
            poll_interval: Time between status checks in seconds (if waiting)
            timeout: Maximum time to wait in seconds (if waiting, None for no timeout)
            
        Returns:
            Tuple of (TaskResponse, video_bytes if wait=True else None)
            
        Raises:
            TimeoutError: If waiting and the task doesn't complete before timeout
            TaskFailedError: If the task fails
            Exception: For other API errors
        """
        # Create the task
        task = await self.create(
            prompt=prompt,
            negative_prompt=negative_prompt,
            model_name=model_name,
            cfg_scale=cfg_scale,
            mode=mode,
            camera_control=camera_control,
            aspect_ratio=aspect_ratio,
            duration=duration,
        )
        
        if not wait:
            return task, None
            
        # Wait for completion
        status = await self.wait_for_completion(
            task_id=task.task_id,
            poll_interval=poll_interval,
            timeout=timeout,
        )
        
        # Download the video if successful
        video_bytes = None
        if status.task_status == TaskStatus.SUCCEEDED and status.video_url:
            video_bytes = await self.download_video(status.video_url)
            
        return status, video_bytes


async def generate_text_to_video(
    prompt: str,
    api_key: str,
    negative_prompt: str | None = None,
    model_name: str = "kling-v1",
    cfg_scale: float = 0.5,
    mode: str = "standard",
    camera_control: dict | None = None,
    aspect_ratio: str = "16:9",
    duration: int = 5,
    wait: bool = True,
    poll_interval: float = 5.0,
    timeout: float | None = 300.0,
) -> tuple[TaskResponse, bytes | None]:
    """Convenience function to generate a video with minimal setup.
    
    This creates a new TextToVideoAPI client, generates a video, and returns
    the result, automatically cleaning up resources.
    
    Args:
        prompt: Text prompt describing the desired video
        api_key: Kling AI API key
        negative_prompt: Text describing what to avoid in the video
        model_name: Name of the model to use (default: "kling-v1")
        cfg_scale: Controls how closely to follow the prompt (0.0 to 1.0)
        mode: Video generation mode ("standard" or "professional")
        camera_control: Camera movement configuration
        aspect_ratio: Aspect ratio of the generated video (e.g., "16:9")
        duration: Duration of the video in seconds (5 or 10)
        wait: Whether to wait for video generation to complete
        poll_interval: Time between status checks in seconds (if waiting)
        timeout: Maximum time to wait in seconds (if waiting, None for no timeout)
        
    Returns:
        Tuple of (TaskResponse, video_bytes if wait=True else None)
        
    Raises:
        TimeoutError: If waiting and the task doesn't complete before timeout
        TaskFailedError: If the task fails
        Exception: For other API errors
    """
    config = KlingConfig(api_key=api_key)
    async with TextToVideoAPI(config) as client:
        return await client.generate(
            prompt=prompt,
            negative_prompt=negative_prompt,
            model_name=model_name,
            cfg_scale=cfg_scale,
            mode=mode,
            camera_control=camera_control,
            aspect_ratio=aspect_ratio,
            duration=duration,
            wait=wait,
            poll_interval=poll_interval,
            timeout=timeout,
        )
