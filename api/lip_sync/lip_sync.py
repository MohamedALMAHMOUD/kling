"""Kling AI Lip Sync API client.

This module provides an async client for interacting with the Kling AI Lip Sync API.
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
from app.core.third_party_integrations.kling.models.lip_sync import (
    LipSyncRequest,
    LipSyncResponse,
)

from ._exceptions import (
    LipSyncError,
    LipSyncRateLimitError,
    LipSyncServerError,
    LipSyncTimeoutError,
    LipSyncValidationError,
    handle_lip_sync_error,
)
from ._requests import CreateTaskRequest, TaskListQueryParams, TaskStatus
from ._responses import TaskData, TaskListResponse, TaskResponse

logger = logging.getLogger(__name__)

# Default retry configuration
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_MULTIPLIER = 1
DEFAULT_RETRY_MIN = 1
DEFAULT_RETRY_MAX = 10


class LipSyncAPI:
    """Client for interacting with the Kling AI Lip Sync API.

    This client provides methods to create and manage lip sync tasks.
    It handles authentication, request/response validation, and error handling.
    """

    def __init__(self, client: httpx.AsyncClient):
        """Initialize the Lip Sync API client.

        Args:
            client: An authenticated httpx.AsyncClient instance
        """
        self._client = client
        self._base_url = "https://api.klingai.com/v1/lip-sync"

    @retry(
        stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
        wait=wait_exponential(
            multiplier=DEFAULT_RETRY_MULTIPLIER,
            min=DEFAULT_RETRY_MIN,
            max=DEFAULT_RETRY_MAX,
        ),
        retry=retry_if_exception_type(
            (LipSyncRateLimitError, LipSyncServerError, LipSyncTimeoutError)
        ),
        reraise=True,
    )
    async def create_task(self, request: LipSyncRequest | dict[str, Any]) -> LipSyncResponse:
        """Create a new lip sync task.

        Args:
            request: Either a LipSyncRequest instance or a dict with the request parameters

        Returns:
            LipSyncResponse: The created task

        Raises:
            LipSyncValidationError: If the request is invalid
            LipSyncError: For other API errors
        """
        try:
            if not isinstance(request, LipSyncRequest):
                request = LipSyncRequest.model_validate(request)
            create_request = CreateTaskRequest.model_validate(request.model_dump())
            response = await self._client.post(
                f"{self._base_url}/tasks",
                json=create_request.model_dump(exclude_none=True),
                timeout=30.0,
            )
            response.raise_for_status()
            return LipSyncResponse.model_validate(response.json()["data"])
        except ValidationError as e:
            logger.error("Validation error in create_task: %s", e)
            raise LipSyncValidationError(str(e)) from e
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get("Retry-After", 5))
                raise LipSyncRateLimitError(
                    "Rate limit exceeded",
                    status_code=429,
                    details={"retry_after": retry_after},
                ) from e
            if e.response.status_code >= 500:
                raise LipSyncServerError(
                    "Server error", status_code=e.response.status_code
                ) from e
            try:
                handle_lip_sync_error(e.response.json())
            except Exception as json_err:
                logger.error("Error parsing error response: %s", json_err)
                raise LipSyncError("Unknown error occurred") from e
        except httpx.TimeoutException as e:
            raise LipSyncTimeoutError("Request timed out") from e
        except Exception as e:
            logger.error("Unexpected error in create_task: %s", e)
            raise LipSyncError("An unexpected error occurred") from e

    @retry(
        stop=stop_after_attempt(DEFAULT_RETRY_ATTEMPTS),
        wait=wait_exponential(
            multiplier=DEFAULT_RETRY_MULTIPLIER,
            min=DEFAULT_RETRY_MIN,
            max=DEFAULT_RETRY_MAX,
        ),
        retry=retry_if_exception_type(LipSyncRateLimitError),
    )
    async def get_task(self, task_id: str) -> TaskData:
        """Get the status of a lip sync task.

        Args:
            task_id: The ID of the task to retrieve

        Returns:
            TaskData: The task data

        Raises:
            LipSyncNotFoundError: If the task is not found
            LipSyncError: For other API errors
        """
        try:
            response = await self._client.get(
                f"{self._base_url}/tasks/{task_id}",
                timeout=10.0,
            )
            response.raise_for_status()
            
            # Parse and return the response
            task_response = TaskResponse.model_validate(response.json())
            return task_response.data

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get("Retry-After", 5))
                raise LipSyncRateLimitError(
                    "Rate limit exceeded",
                    status_code=429,
                    details={"retry_after": retry_after},
                ) from e
            if e.response.status_code == 404:
                raise LipSyncError("Task not found", status_code=404) from e
            raise LipSyncError(
                f"Failed to get task: {e}", status_code=e.response.status_code
            ) from e
        except Exception as e:
            logger.error("Error getting task %s: %s", task_id, e)
            raise LipSyncError("Failed to get task") from e

    async def list_tasks(
        self,
        query_params: TaskListQueryParams | None = None,
        status: TaskStatus | None = None,
    ) -> TaskListResponse:
        """List all lip sync tasks.

        Args:
            query_params: Optional query parameters for filtering and pagination
            status: Optional status to filter tasks by

        Returns:
            TaskListResponse: A paginated list of tasks

        Raises:
            LipSyncError: If the request fails
        """
        try:
            if query_params is None:
                query_params = TaskListQueryParams()

            # Prepare query parameters
            params = query_params.model_dump(exclude_none=True)
            if status is not None:
                params["status"] = status.value

            response = await self._client.get(
                f"{self._base_url}/tasks",
                params=params,
                timeout=10.0,
            )
            response.raise_for_status()

            # Parse and return the response
            return TaskListResponse.model_validate(response.json())

        except Exception as e:
            logger.error("Error listing tasks: %s", e)
            raise LipSyncError("Failed to list tasks") from e

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running lip sync task.

        Args:
            task_id: The ID of the task to cancel

        Returns:
            bool: True if the task was cancelled successfully

        Raises:
            LipSyncError: If the cancellation fails
        """
        try:
            response = await self._client.post(
                f"{self._base_url}/tasks/{task_id}/cancel",
                timeout=10.0,
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error("Error cancelling task %s: %s", task_id, e)
            raise LipSyncError("Failed to cancel task") from e


# Singleton instance
lip_sync_api = LipSyncAPI(KlingClient.get_instance()._client)
