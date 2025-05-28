"""
Kling AI API client implementation.
"""
from __future__ import annotations

import json
import logging
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, ValidationError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .api.image_to_video.image_to_video import ImageToVideoAPI
from .api.multi_image_to_video.multi_image_to_video import MultiImageToVideoAPI
from .api.text_to_video.text_to_video import TextToVideoAPI
from .api.video_extension.video_extension import VideoExtensionAPI
from .config import KlingConfig

# Type variable for generic model parsing
T = TypeVar("T", bound=BaseModel)

# Configure logging
logger = logging.getLogger(__name__)


class KlingSingletonAPIError(Exception):
    """Base exception for Kling API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


class KlingClient:
    """
    Singleton client for interacting with the Kling AI API.

    Attributes:
        text_to_video (TextToVideoAPI): API for text-to-video generation tasks.
        multi_image_to_video (MultiImageToVideoAPI): API for multi-image to video generation tasks.
        image_to_video (ImageToVideoAPI): API for image-to-video generation tasks.
        video_extension (VideoExtensionAPI): API for extending existing videos with AI.

    Usage:
        config = KlingConfig(...)
        client = KlingClient(config)
        # All subsequent instantiations return the same instance
    """
    _instance: KlingClient | None = None
    _initialized: bool = False

    def __new__(cls, config: KlingConfig) -> KlingClient:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config: KlingConfig):
        if self._initialized:
            return
        self.config = config
        self.base_url = config.base_url.rstrip("/")
        self.timeout = config.timeout
        self.max_retries = config.max_retries
        self._client = self._create_http_client()
        # Register API subclients here (add more as needed)
        try:
            self.text_to_video = TextToVideoAPI(self)
            self.multi_image_to_video = MultiImageToVideoAPI(self)
            self.image_to_video = ImageToVideoAPI(self)
            self.video_extension = VideoExtensionAPI(self._client)
        except ImportError as e:
            logger.warning(f"Failed to import one or more API modules: {e}")
            self.text_to_video = None  # Could not import TextToVideoAPI
            self.multi_image_to_video = None  # Could not import MultiImageToVideoAPI
            self.image_to_video = None  # Could not import ImageToVideoAPI
            self.video_extension = None  # Could not import VideoExtensionAPI
        # todo: Register additional subclients
        self._initialized = True

    def _create_http_client(self) -> httpx.AsyncClient:
        """Create and configure an HTTP client.

        Returns:
            Configured httpx.AsyncClient instance
        """
        return httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        if hasattr(self, "_client") and self._client:
            await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - ensure client is closed."""
        await self.close()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(
            (httpx.NetworkError, httpx.TimeoutException, httpx.HTTPStatusError)
        ),
    )
    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> dict[str, Any]:
        """Make an HTTP request to the Kling API with retries.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path (e.g., "/v1/videos/text2video")
            **kwargs: Additional arguments to pass to the request

        Returns:
            Parsed JSON response as a dictionary

        Raises:
            KlingAPIError: If the API returns an error response
            httpx.HTTPStatusError: For HTTP errors
            httpx.RequestError: For request errors
        """
        url = f"{self.base_url}{endpoint}"
        logger.debug("Making %s request to %s", method, url)

        try:
            response = await self._client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}"
            try:
                error_data = e.response.json()
                error_msg = error_data.get("message", error_msg)
            except (json.JSONDecodeError, AttributeError):
                error_msg = f"{error_msg}: {e.response.text}"

            logger.error(
                "%s: %s",
                error_msg,
                str(e),
                extra={"status_code": e.response.status_code},
            )
            raise KlingSingletonAPIError(error_msg, status_code=e.response.status_code) from e

        except httpx.RequestError as e:
            logger.error("Request failed: %s", str(e))
            raise KlingSingletonAPIError(f"Request failed: {str(e)}") from e

    async def _get_paginated(
        self,
        endpoint: str,
        model: type[T],
        page_num: int = 1,
        page_size: int = 30,
        **params,
    ) -> list[T]:
        """Get paginated results from the API.

        Args:
            endpoint: API endpoint path
            model: Pydantic model to parse the response data
            page_num: Page number to fetch
            page_size: Number of items per page
            **params: Additional query parameters

        Returns:
            List of parsed model instances
        """
        params.update({"pageNum": page_num, "pageSize": page_size})
        response = await self._request("GET", endpoint, params=params)

        if not isinstance(response.get("data"), list):
            return []

        return [model.model_validate(item) for item in response["data"]]

    async def _handle_response(
        self,
        response: dict[str, Any],
        model: type[T],
    ) -> T:
        """Handle API response and parse it using the provided model.

        Args:
            response: Raw API response
            model: Pydantic model to parse the response data

        Returns:
            Parsed model instance

        Raises:
            KlingAPIError: If the response indicates an error
            ValidationError: If response data doesn't match the model
        """
        if response.get("code") != 0:
            raise KlingSingletonAPIError(
                response.get("message", "Unknown error"),
                status_code=response.get("code"),
            )

        try:
            return model.parse_obj(response.get("data", {}))
        except ValidationError as e:
            logger.error("Failed to validate response: %s", str(e))
            raise

