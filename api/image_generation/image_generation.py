"""Client for interacting with the Kling AI Image Generation API."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from pydantic import HttpUrl

from ...client import KlingClient
from ._requests import ImageGenerationRequest, TaskListRequest
from ._responses import TaskListResponse, TaskResponse, TaskStatus

logger = logging.getLogger(__name__)


class KlingImageGenerator:
    """Client for Kling AI Image Generation API.
    
    This client provides methods to interact with the Kling AI Image Generation API,
    including creating image generation tasks, checking task status, and listing tasks.
    """
    
    def __init__(self, client: KlingClient):
        """Initialize the image generator with a Kling client.
        
        Args:
            client: An instance of KlingClient for making API requests.
        """
        self._client = client
        self._base_path = "/v1/images/generations"
    
    async def create_task(
        self,
        *,
        prompt: str,
        model_name: str = "kling-1",
        negative_prompt: str | None = None,
        image: str | bytes | None = None,
        image_reference: str | None = None,
        image_fidelity: float = 0.3,
        human_fidelity: float | None = None,
        n: int = 1,
        aspect_ratio: str = "1:1",
        callback_url: HttpUrl | None = None,
    ) -> TaskResponse:
        """Create a new image generation task.

        Args:
            prompt: Text prompt for image generation
            model_name: Name of the model to use (default: 'kling-1')
            negative_prompt: Text describing what to avoid in the generated image
            image: Reference image as base64 string or bytes
            image_reference: URL of a reference image
            image_fidelity: Fidelity of the generated image to the reference (0.0-1.0)
            human_fidelity: Human-like generation fidelity (0.0-1.0)
            n: Number of images to generate (1-4)
            aspect_ratio: Aspect ratio of the generated image (e.g., '1:1', '16:9')
            callback_url: URL to receive a callback when generation is complete

        Returns:
            TaskResponse containing task ID and status
        """
        request = ImageGenerationRequest(
            model_name=model_name,
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=image if isinstance(image, str) else None,
            image_reference=image_reference,
            image_fidelity=image_fidelity,
            human_fidelity=human_fidelity,
            n=n,
            aspect_ratio=aspect_ratio,
            callback_url=callback_url,
        )
        
        response = await self._client.post(
            self._base_path,
            json=request.model_dump(exclude_none=True, by_alias=True),
        )
        
        return TaskResponse.model_validate(response)
    
    async def get_task(self, task_id: str) -> TaskResponse:
        """Get the status of a specific task.
        
        Args:
            task_id: The ID of the task to retrieve.
            
        Returns:
            TaskResponse with current status and results if available.
            
        Raises:
            KlingAPIError: If the API request fails.
            KlingAuthenticationError: If authentication fails.
            KlingRateLimitError: If rate limited.
        """
        response = await self._client.get(f"{self._base_path}/{task_id}")
        return TaskResponse.model_validate(response)
    
    async def list_tasks(
        self,
        *,
        status: TaskStatus | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> TaskListResponse:
        """List image generation tasks with pagination.
        
        Args:
            status: Filter tasks by status.
            limit: Number of items per page (1-500).
            offset: Offset for pagination.
            
        Returns:
            TaskListResponse containing a list of tasks.
            
        Raises:
            KlingAPIError: If the API request fails.
            KlingAuthenticationError: If authentication fails.
            KlingRateLimitError: If rate limited.
        """
        request = TaskListRequest(
            status=status,
            limit=limit,
            offset=offset,
        )
        
        response = await self._client.get(
            self._base_path,
            params=request.model_dump(exclude_none=True, by_alias=True),
        )
        
        return TaskListResponse.model_validate(response)
    
    async def wait_for_task_completion(
        self,
        task_id: str,
        poll_interval: int = 2,
        timeout: int | None = 300,
    ) -> TaskResponse:
        """Wait for a task to complete by polling its status.
        
        Args:
            task_id: The ID of the task to monitor.
            poll_interval: Seconds between status checks.
            timeout: Maximum seconds to wait before timing out.
            
        Returns:
            The final task status and results.
            
        Raises:
            TimeoutError: If the task doesn't complete within the timeout.
            KlingAPIError: If the API request fails.
        """
        start_time = datetime.now().timestamp()
        
        while True:
            task = await self.get_task(task_id)
            
            if task.data.task_status in (TaskStatus.SUCCEEDED, TaskStatus.FAILED):
                return task
                
            if datetime.now().timestamp() - start_time > timeout:
                raise TimeoutError(
                    f"Task {task_id} did not complete within {timeout} seconds"
                )
            
            await asyncio.sleep(poll_interval)



# For backward compatibility
ImageGenerationClient = KlingImageGenerator