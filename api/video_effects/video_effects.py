"""Kling AI Video Effects API client."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx
from pydantic import ValidationError

from app.core.third_party_integrations.kling.api.video_effects._exceptions import (
    VideoEffectsConnectionError,
    VideoEffectsError,
    VideoEffectsNotFoundError,
    VideoEffectsRateLimitError,
    VideoEffectsServerError,
    VideoEffectsTimeoutError,
    VideoEffectsUnauthorizedError,
    VideoEffectsValidationError,
)
from app.core.third_party_integrations.kling.api.video_effects._requests import (
    CreateVideoEffectRequest,
    ListTasksRequest,
    TaskStatus,
)
from app.core.third_party_integrations.kling.api.video_effects._responses import (
    CancelTaskResponse,
    CreateTaskResponse,
    GetTaskResponse,
    ListTasksResponse,
)

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30.0
DEFAULT_RETRIES = 3
DEFAULT_BASE_URL = "https://api.kling.ai/v1/video-effects"


class VideoEffectsAPI:
    """Client for the Kling AI Video Effects API.
    
    This class provides methods to interact with the Kling AI Video Effects API,
    including creating tasks, checking status, and listing tasks.
    
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
    
    def __init__(
        self,
        client: httpx.AsyncClient,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_RETRIES,
    ) -> None:
        """Initialize the VideoEffectsAPI client.
        
        Args:
            client: HTTPX async client to use for requests.
            api_key: Kling AI API key. If not provided, must be set via environment variable.
            base_url: Base URL for the API. Defaults to production API.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retries for failed requests.
        """
        self.client = client
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Set default headers
        self._headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.api_key:
            self._headers["Authorization"] = f"Bearer {self.api_key}"
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> dict[str, Any] | None:
        """Make an HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments to pass to httpx request
            
        Returns:
            Parsed JSON response as a dictionary
            
        Raises:
            VideoEffectsError: For request errors
            VideoEffectsValidationError: For invalid requests
            VideoEffectsRateLimitError: For rate limiting
            VideoEffectsUnauthorizedError: For authentication errors
            VideoEffectsNotFoundError: For 404 errors
            VideoEffectsServerError: For server errors
            VideoEffectsTimeoutError: For request timeouts
            VideoEffectsConnectionError: For connection errors
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {**self._headers, **kwargs.pop("headers", {})}
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.request(
                    method,
                    url,
                    headers=headers,
                    timeout=self.timeout,
                    **kwargs,
                )
                
                # Handle successful response
                if 200 <= response.status_code < 300:
                    if response.status_code == 204:  # No content
                        return None
                    return response.json()
                
                # Handle errors
                error_data = response.json() if response.content else {}
                
                # Rate limiting - check for Retry-After header
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", "1"))
                    if attempt < self.max_retries:
                        await asyncio.sleep(retry_after)
                        continue
                    
                    raise VideoEffectsRateLimitError(
                        retry_after=retry_after,
                        details={"message": "Rate limit exceeded", "retry_after": retry_after, **error_data},
                    )
                
                # Map other HTTP errors to specific exceptions
                if response.status_code == 400:
                    raise VideoEffectsValidationError("Invalid request", details=error_data)
                elif response.status_code == 401:
                    raise VideoEffectsUnauthorizedError("Authentication failed", details=error_data)
                elif response.status_code == 404:
                    raise VideoEffectsNotFoundError("Resource not found", details=error_data)
                elif 500 <= response.status_code < 600:
                    raise VideoEffectsServerError("Server error occurred", details=error_data)
                else:
                    raise VideoEffectsError("API request failed", details=error_data)
                
            except httpx.TimeoutException as e:
                last_exception = VideoEffectsTimeoutError(f"Request timed out: {e}")
                if attempt == self.max_retries:
                    raise last_exception
                    
            except httpx.RequestError as e:
                last_exception = VideoEffectsConnectionError(f"Connection error: {e}")
                if attempt == self.max_retries:
                    raise last_exception
                    
            except Exception as e:
                if isinstance(e, VideoEffectsError):
                    raise
                last_exception = VideoEffectsError(f"Unexpected error: {e}")
                if attempt == self.max_retries:
                    raise last_exception
            
            # Exponential backoff
            await asyncio.sleep(2 ** attempt * 0.1)
        
        # This should never be reached due to the raises above
        raise last_exception or VideoEffectsError("Unknown error occurred")
    
    async def create_task(self, **kwargs: Any) -> CreateTaskResponse:
        """Create a new video effect task.
        
        Args:
            **kwargs: Arguments to pass to CreateVideoEffectRequest
            
        Returns:
            CreateTaskResponse with task details
            
        Example:
            ```python
            task = await api.create_task(
                video_url="https://example.com/video.mp4",
                effect_type="style_transfer",
                style_reference="https://example.com/style.jpg"
            )
            ```
        """
        try:
            request = CreateVideoEffectRequest(**kwargs)
            data = await self._request("POST", "/tasks", json=request.model_dump(exclude_none=True))
            return CreateTaskResponse(**data)
        except ValidationError as e:
            raise VideoEffectsValidationError("Invalid request parameters", details={"errors": e.errors()}) from e
    
    async def get_task(self, task_id: str) -> GetTaskResponse:
        """Get the status of a video effect task.
        
        Args:
            task_id: ID of the task to retrieve
            
        Returns:
            GetTaskResponse with task details
            
        Raises:
            VideoEffectsNotFoundError: If the task is not found
        """
        data = await self._request("GET", f"/tasks/{task_id}")
        return GetTaskResponse(**data)
    
    async def list_tasks(
        self,
        status: TaskStatus | None = None,
        limit: int = 10,
        cursor: str | None = None,
    ) -> ListTasksResponse:
        """List video effect tasks with optional filtering.
        
        Args:
            status: Filter tasks by status
            limit: Maximum number of tasks to return (1-100)
            cursor: Pagination cursor for the next page of results
            
        Returns:
            ListTasksResponse with matching tasks and pagination info
        """
        try:
            request = ListTasksRequest(status=status, limit=limit, cursor=cursor)
            params = {k: v for k, v in request.model_dump().items() if v is not None}
            data = await self._request("GET", "/tasks", params=params)
            return ListTasksResponse(**data)
        except ValidationError as e:
            raise VideoEffectsValidationError("Invalid request parameters", details={"errors": e.errors()}) from e
    
    async def cancel_task(self, task_id: str) -> CancelTaskResponse:
        """Cancel a video effect task.
        
        Args:
            task_id: ID of the task to cancel
            
        Returns:
            CancelTaskResponse with cancellation details
            
        Raises:
            VideoEffectsNotFoundError: If the task is not found
            VideoEffectsValidationError: If the task cannot be cancelled
        """
        data = await self._request("POST", f"/tasks/{task_id}/cancel")
        return CancelTaskResponse(**data)
