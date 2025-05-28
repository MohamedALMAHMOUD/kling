"""
Kling AI Video Extension API client.

This module provides an async client for interacting with the Kling AI Video Extension API.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx
from pydantic import ValidationError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.third_party_integrations.kling.client import KlingClient
from app.core.third_party_integrations.kling.models.video_extension import (
    VideoExtensionRequest,
    VideoExtensionResponse,
)

from ._exceptions import (
    VideoExtensionError,
    VideoExtensionRateLimitError,
    VideoExtensionServerError,
    VideoExtensionTimeoutError,
    VideoExtensionValidationError,
    handle_video_extension_error,
)
from ._requests import TaskListQueryParams, TaskStatus
from ._responses import TaskStatusData, TaskStatusResponse

logger = logging.getLogger(__name__)

# Default retry configuration
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_MULTIPLIER = 1
DEFAULT_RETRY_MIN = 1
DEFAULT_RETRY_MAX = 10


class VideoExtensionAPI:
    """Client for interacting with the Kling AI Video Extension API.

    This client provides methods to create and manage video extension tasks.
    It handles authentication, request/response validation, and error handling.
    """

    BASE_PATH = "/v1/videos/video-extend"

    def __init__(self, client: httpx.AsyncClient):
        """Initialize the VideoExtensionAPI client.

        Args:
            client: Authenticated httpx.AsyncClient instance from KlingClient
        """
        self._client = client
        self._base_url = str(client.base_url).rstrip("/")
    
    async def create_task(
        self,
        request: VideoExtensionRequest,
        **kwargs: Any,
    ) -> VideoExtensionResponse:
        """Create a new video extension task.

        Args:
            request: Video extension request parameters
            **kwargs: Additional arguments to pass to the request

        Returns:
            VideoExtensionResponse: Response containing task information

        Raises:
            VideoExtensionValidationError: If request validation fails
            VideoExtensionRateLimitError: If rate limit is exceeded
            VideoExtensionServerError: For server errors (5xx)
            VideoExtensionError: For other API errors
        """
        try:
            # Ensure request is properly validated
            if not isinstance(request, VideoExtensionRequest):
                request = VideoExtensionRequest.model_validate(request)
                
            response = await self._make_request(
                "POST",
                self.BASE_PATH,
                json=request.model_dump(exclude_none=True),
                **kwargs,
            )
            
            # Validate and parse the response
            if not isinstance(response, dict):
                raise VideoExtensionValidationError("Invalid response format: expected dictionary")
                
            return VideoExtensionResponse.model_validate(response)
            
        except ValidationError as e:
            logger.error(f"Request/Response validation error: {e}")
            raise VideoExtensionValidationError(f"Validation error: {e}") from e
            
        except VideoExtensionValidationError:
            raise
            
        except Exception as e:
            logger.error(f"Failed to create video extension task: {e}")
            raise VideoExtensionError(f"Failed to create task: {str(e)}") from e
    
    async def get_task(
        self,
        task_id: str,
        **kwargs: Any,
    ) -> TaskStatusResponse:
        """Get the status of a video extension task.

        Args:
            task_id: ID of the task to retrieve
            **kwargs: Additional arguments to pass to the request

        Returns:
            TaskStatusResponse: Response containing task status and data

        Raises:
            VideoExtensionValidationError: If task_id is invalid
            VideoExtensionError: If task is not found or other errors occur
        """
        try:
            # Validate task_id
            if not task_id or not isinstance(task_id, str):
                raise VideoExtensionValidationError("task_id must be a non-empty string")
                
            response = await self._make_request(
                "GET",
                f"{self.BASE_PATH}/{task_id}",
                **kwargs,
            )
            
            # Validate and parse the response
            if not isinstance(response, dict):
                raise VideoExtensionValidationError("Invalid response format: expected dictionary")
                
            status_response = TaskStatusResponse.model_validate(response)
            
            # Log status transition if available
            if hasattr(status_response, 'data') and hasattr(status_response.data, 'task_status'):
                task_status = status_response.data.task_status
                logger.info(
                    "Task %s status: %s",
                    task_id,
                    task_status.value if hasattr(task_status, 'value') else task_status
                )
                
                # Check for terminal states
                if task_status in (TaskStatus.SUCCEED, TaskStatus.FAILED):
                    logger.info(
                        "Task %s reached terminal state: %s",
                        task_id,
                        task_status.value
                    )
            
            return status_response
            
        except ValidationError as e:
            logger.error(f"Response validation error: {e}")
            raise VideoExtensionValidationError(f"Invalid response data: {e}") from e
            
        except VideoExtensionValidationError:
            raise
            
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            raise VideoExtensionError(f"Failed to retrieve task: {str(e)}") from e
    
    async def list_tasks(
        self,
        page_num: int = 1,
        page_size: int = 30,
        **kwargs: Any,
    ) -> list[TaskStatusData]:
        """List video extension tasks with pagination.

        Args:
            page_num: Page number (1-based)
            page_size: Number of items per page (1-500)
            **kwargs: Additional arguments to pass to the request

        Returns:
            List of task status data objects

        Raises:
            VideoExtensionValidationError: If pagination parameters are invalid
            VideoExtensionError: If request fails or response is invalid
        """
        try:
            # Create and validate query parameters
            try:
                query = TaskListQueryParams(
                    page_num=page_num,
                    page_size=page_size,
                )
                query_dict = query.model_dump(exclude_none=True)
            except ValidationError as e:
                raise VideoExtensionValidationError(
                    f"Invalid pagination parameters: {str(e)}"
                ) from e

            logger.debug(
                "Listing tasks with params: page_num=%s, page_size=%s",
                page_num,
                page_size,
            )
            
            # Make the request with query parameters
            response = await self._make_request(
                "GET",
                self.BASE_PATH,
                params=query_dict,
                **kwargs,
            )
            
            # Validate and parse the response
            if not isinstance(response, dict) or "data" not in response:
                raise VideoExtensionValidationError("Invalid response format: missing 'data' field")
                
            # Return a list of TaskStatusData objects
            return [TaskStatusData.model_validate(item) for item in response["data"]]
            
        except ValidationError as e:
            logger.error(f"Response validation error: {e}")
            raise VideoExtensionValidationError(f"Invalid response data: {e}") from e
            
        except VideoExtensionValidationError:
            raise
            
        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            raise VideoExtensionError(f"Failed to list tasks: {str(e)}") from e
    
    @retry(
        stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
        wait=wait_exponential(
            multiplier=DEFAULT_RETRY_MULTIPLIER,
            min=DEFAULT_RETRY_MIN,
            max=DEFAULT_RETRY_MAX,
        ),
        retry=retry_if_exception_type(
            (VideoExtensionRateLimitError, VideoExtensionServerError, httpx.RequestError)
        ),
        reraise=True,
    )
    async def _make_request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make an HTTP request to the Kling AI API with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: API endpoint URL
            **kwargs: Additional arguments to pass to the request
            
        Returns:
            Parsed JSON response
            
        Raises:
            VideoExtensionError: For request/response handling errors
            VideoExtensionRateLimitError: If rate limit is exceeded
            VideoExtensionServerError: For server errors (5xx)
            VideoExtensionTimeoutError: If request times out
        """
        try:
            # Ensure URL is absolute
            if not url.startswith("http"):
                url = f"{self._base_url}{url}"
            
            logger.debug(f"Making {method} request to {url}")
            
            async with self._client as client:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException as e:
            logger.error(f"Request timed out: {e}")
            raise VideoExtensionTimeoutError(f"Request timed out: {e}") from e
            
        except httpx.HTTPStatusError as e:
            error_data = {}
            try:
                error_data = e.response.json()
            except Exception:
                pass
                
            status_code = e.response.status_code
            logger.error(f"HTTP error {status_code} for {method} {url}: {error_data}")
            
            # Handle rate limiting
            if status_code == 429:
                retry_after = e.response.headers.get("Retry-After")
                raise VideoExtensionRateLimitError(
                    f"Rate limit exceeded. Retry after: {retry_after}s",
                    status_code=status_code,
                )
                
            # Handle validation errors
            if status_code == 400:
                handle_video_extension_error(error_data)
                
            # Handle server errors
            if 500 <= status_code < 600:
                raise VideoExtensionServerError(
                    f"Server error {status_code}: {e}",
                    status_code=status_code,
                )
                
            # For other errors, use the generic error handler
            handle_video_extension_error(error_data)
            
        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            raise VideoExtensionError(f"Request failed: {e}") from e
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise VideoExtensionError(f"Unexpected error: {e}") from e


# Singleton instance
video_extension_api = VideoExtensionAPI(KlingClient.get_instance()._client)
