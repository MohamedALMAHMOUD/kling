"""
Client for interacting with the Kling AI Virtual Try-On API.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from pydantic import ValidationError

from ...client import KlingClient
from ._exceptions import (
    APIError,
    AuthenticationError,
    RateLimitError,
    TaskFailedError,
    TimeoutError,
)
from ._exceptions import (
    ValidationError as ClientValidationError,
)
from ._requests import TaskListQuery, VirtualTryOnRequest
from ._responses import TaskListResponse, TaskResponse, VirtualTryOnTaskResponse

logger = logging.getLogger(__name__)

class VirtualTryOnAPI:
    """Client for Kling AI Virtual Try-On API.
    
    This client provides methods to interact with the Kling AI Virtual Try-On API,
    including creating virtual try-on tasks, checking task status, and listing tasks.
    """
    
    def __init__(self, client: KlingClient):
        """Initialize the virtual try-on client with a Kling client.
        
        Args:
            client: An instance of KlingClient for making API requests.
        """
        self._client = client
        self._base_path = "/v1/images/kolors-virtual-try-on"
    
    async def create_task(
        self,
        *,
        human_image: str | dict[str, str],
        cloth_image: str | dict[str, str] | None = None,
        model_name: str = "kolors-virtual-try-on-v1-5",
        callback_url: str | None = None,
        **kwargs: Any,
    ) -> VirtualTryOnTaskResponse:
        """Create a new virtual try-on task.

        Args:
            human_image: Reference human image as a URL or a dict with 'url' or 'base64' key.
            cloth_image: Optional reference clothing image as a URL or a dict with 'url' or 'base64' key.
            model_name: Model to use for virtual try-on. Defaults to "kolors-virtual-try-on-v1-5".
            callback_url: Optional URL to receive task completion notifications.
            **kwargs: Additional parameters to pass to the API.

        Returns:
            VirtualTryOnTaskResponse containing task information.

        Raises:
            ValidationError: If input validation fails.
            APIError: If the API returns an error.
        """
        try:
            # Create request model
            request_data = VirtualTryOnRequest(
                human_image=human_image,
                cloth_image=cloth_image,
                model_name=model_name,
                callback_url=callback_url,
                **kwargs,
            )
            
            # Make API request
            response = await self._client._request(
                "POST",
                self._base_path,
                json=request_data.model_dump(exclude_none=True),
            )
            
            # Parse and return response
            task_response = VirtualTryOnTaskResponse(**response)
            if task_response.code != 0:
                raise APIError(
                    message=task_response.message or "API returned an error",
                    code=task_response.code,
                    request_id=task_response.request_id,
                )
            
            return task_response
            
        except ValidationError as e:
            logger.error("Validation error creating virtual try-on task: %s", str(e))
            raise ClientValidationError(f"Invalid request parameters: {str(e)}") from e
        except Exception as e:
            logger.error("Error creating virtual try-on task: %s", str(e))
            if isinstance(e, (AuthenticationError, RateLimitError, TimeoutError, APIError)):
                raise
            raise APIError(f"Failed to create virtual try-on task: {str(e)}") from e
    
    async def get_task_status(self, task_id: str) -> TaskResponse:
        """Get the status of a virtual try-on task.

        Args:
            task_id: The ID of the task to check.

        Returns:
            TaskResponse containing the task status and results if available.

        Raises:
            APIError: If the API returns an error.
        """
        try:
            response = await self._client._request(
                "GET",
                f"{self._base_path}/{task_id}",
            )
            
            task_response = TaskResponse(**response)
            if task_response.code != 0:
                raise APIError(
                    message=task_response.message or "API returned an error",
                    code=task_response.code,
                    request_id=task_response.request_id,
                )
            
            return task_response
            
        except Exception as e:
            logger.error("Error getting task status for %s: %s", task_id, str(e))
            if isinstance(e, (AuthenticationError, RateLimitError, TimeoutError, APIError)):
                raise
            raise APIError(f"Failed to get task status: {str(e)}") from e
    
    async def list_tasks(
        self,
        *,
        page_num: int = 1,
        page_size: int = 30,
    ) -> TaskListResponse:
        """List virtual try-on tasks with pagination.

        Args:
            page_num: Page number (1-based).
            page_size: Number of items per page.

        Returns:
            TaskListResponse containing a list of tasks.

        Raises:
            APIError: If the API returns an error.
        """
        try:
            query = TaskListQuery(page_num=page_num, page_size=page_size)
            
            response = await self._client._request(
                "GET",
                self._base_path,
                params=query.model_dump(exclude_none=True, by_alias=True),
            )
            
            task_list_response = TaskListResponse(**response)
            if task_list_response.code != 0:
                raise APIError(
                    message=task_list_response.message or "API returned an error",
                    code=task_list_response.code,
                    request_id=task_list_response.request_id,
                )
            
            return task_list_response
            
        except Exception as e:
            logger.error("Error listing tasks: %s", str(e))
            if isinstance(e, (AuthenticationError, RateLimitError, TimeoutError, APIError)):
                raise
            raise APIError(f"Failed to list tasks: {str(e)}") from e
    
    async def wait_for_completion(
        self,
        task_id: str,
        *,
        poll_interval: float = 5.0,
        timeout: float | None = 300.0,
    ) -> TaskResponse:
        """Wait for a virtual try-on task to complete.

        Args:
            task_id: The ID of the task to wait for.
            poll_interval: Time in seconds between status checks.
            timeout: Maximum time in seconds to wait for completion.

        Returns:
            TaskResponse with the final status and results.

        Raises:
            TimeoutError: If the task doesn't complete before the timeout.
            TaskFailedError: If the task fails.
            APIError: For other API errors.
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            status = await self.get_task_status(task_id)
            
            # Check if task is complete
            if status.data.task_status in ("succeed", "failed"):
                if status.data.task_status == "failed":
                    raise TaskFailedError(
                        f"Task {task_id} failed",
                        task_id=task_id,
                        status=status.data.task_status,
                        status_message=status.data.task_status_msg,
                    )
                return status
            
            # Check timeout
            if timeout is not None:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > timeout:
                    raise TimeoutError(
                        f"Task {task_id} did not complete within {timeout} seconds"
                    )
            
            # Wait before polling again
            await asyncio.sleep(poll_interval)


# For backward compatibility
VirtualTryOnClient = VirtualTryOnAPI
