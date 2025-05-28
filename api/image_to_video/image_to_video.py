"""
Image-to-Video API client for Kling AI.

This module provides an asynchronous client for interacting with the Kling AI
Image-to-Video API, enabling video generation from images with various
customization options.
"""
from __future__ import annotations

import asyncio
from datetime import datetime

from pydantic import ValidationError

from ...client import KlingClient
from ._exceptions import TaskFailedError, handle_api_error
from ._exceptions import ValidationError as KlingValidationError
from ._requests import ImageToVideoRequest
from ._response import (
    TaskListResponse,
    TaskStatus,
    VideoGenerationResponse,
)

__all__ = [
    'ImageToVideoAPI',
    'VideoGenerationResponse',
    'TaskListResponse',
    'TaskStatus',
]

class ImageToVideoAPI:
    """
    API route client for Kling AI Image-to-Video endpoints.

    This class should be instantiated by the main KlingClient singleton and accessed via `client.image_to_video`.
    Provides methods to create/manage image-to-video generation tasks, check task status, list tasks, wait for completion, and download videos.
    """
    def __init__(self, client: KlingClient) -> None:
        """
        Args:
            client: The singleton KlingClient instance
        """
        self._client = client
        self._http = client._client  # httpx.AsyncClient
        self.base_url = client.base_url

    async def create_task(self, request: ImageToVideoRequest) -> VideoGenerationResponse:
        """Create a new image-to-video generation task.

        Args:
            request: ImageToVideoRequest instance with task parameters
        Returns:
            VideoGenerationResponse containing task details
        Raises:
            KlingValidationError: If request validation fails
            APIRequestError: For other API request failures
        """
        try:
            resp = await self._http.post(f"{self.base_url}/v1/videos/image2video", json=request.model_dump())
            resp.raise_for_status()
            return VideoGenerationResponse(**resp.json())
        except ValidationError as exc:
            raise KlingValidationError(
                message="Invalid request data",
                errors=exc.errors(),
            ) from exc
        except Exception as exc:
            raise handle_api_error(exc) from exc

    async def get_task_status(self, task_id: str) -> VideoGenerationResponse:
        """Get the status of a video generation task.

        Args:
            task_id: ID of the task to check
        Returns:
            VideoGenerationResponse with current task status
        Raises:
            NotFoundError: If the task doesn't exist
            APIRequestError: For other API request failures
        """
        try:
            resp = await self._http.get(f"{self.base_url}/v1/videos/image2video/{task_id}")
            resp.raise_for_status()
            return VideoGenerationResponse(**resp.json())
        except Exception as exc:
            raise handle_api_error(exc) from exc

    async def list_tasks(self, limit: int = 10, offset: int = 0, status: TaskStatus | None = None) -> TaskListResponse:
        """List all image-to-video tasks with optional filtering.

        Args:
            limit: Max number of tasks to return
            offset: Pagination offset
            status: Filter tasks by status
        Returns:
            TaskListResponse: Paginated list of tasks
        """
        params = {"limit": limit, "offset": offset, "status": status}
        try:
            resp = await self._http.get(f"{self.base_url}/v1/videos/image2video", params=params)
            resp.raise_for_status()
            return TaskListResponse(**resp.json())
        except Exception as exc:
            raise handle_api_error(exc) from exc

    async def wait_for_task_completion(
        self,
        task_id: str,
        poll_interval: float = 5.0,
        timeout: float | None = 300.0,
    ) -> VideoGenerationResponse:
        """
        Wait for a task to complete by polling its status.

        Args:
            task_id: ID of the task to wait for
            poll_interval: How often to poll for updates (seconds)
            timeout: Maximum time to wait (seconds), or None for no timeout
        Returns:
            VideoGenerationResponse with final task status
        Raises:
            TimeoutError: If the task doesn't complete before timeout
            TaskFailedError: If the task fails or is cancelled
            APIRequestError: For other API request failures
        """
        start_time = datetime.utcnow()
        while True:
            task = await self.get_task_status(task_id)
            if task.status == TaskStatus.COMPLETED:
                return task
            if task.status == TaskStatus.FAILED:
                error_msg = f"Task {task_id} failed"
                if getattr(task, "error", None):
                    error_msg += f": {task.error.message}"
                raise TaskFailedError(error_msg, task_id=task_id)
            if task.status == TaskStatus.CANCELLED:
                raise TaskFailedError(f"Task {task_id} was cancelled", task_id=task_id)
            if timeout is not None:
                elapsed = (datetime.utcnow() - start_time).total_seconds()
                if elapsed > timeout:
                    raise TimeoutError(
                        f"Task {task_id} did not complete within {timeout} seconds"
                    )
            await asyncio.sleep(poll_interval)

    async def download_video(
        self,
        video_url: str,
        output_path: str,
        chunk_size: int = 8192,
    ) -> None:
        """
        Download a video from a URL to a local file.

        Args:
            video_url: URL of the video to download
            output_path: Local path to save the video
            chunk_size: Size of chunks to download at once
        Raises:
            IOError: If the download fails
        """
        url = str(video_url)
        try:
            async with self._http.stream('GET', url) as response:
                response.raise_for_status()
                with open(output_path, 'wb') as f:
                    async for chunk in response.aiter_bytes(chunk_size=chunk_size):
                        f.write(chunk)
        except Exception as exc:
            raise OSError(f"Failed to download video from {url}") from exc

