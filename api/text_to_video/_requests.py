"""
Request handling for the Kling AI Text-to-Video API.
"""
from __future__ import annotations

import json
import logging
from enum import Enum
from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field, HttpUrl, validator

from ...config import KlingConfig
from ._exceptions import (
    APIRequestError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError as KlingValidationError,
    handle_api_error,
)

logger = logging.getLogger(__name__)


class VideoMode(str, Enum):
    """Video generation modes."""
    STANDARD = "std"
    PROFESSIONAL = "pro"


class CameraControlType(str, Enum):
    """Predefined camera movement types."""
    SIMPLE = "simple"
    DOWN_BACK = "down_back"
    FORWARD_UP = "forward_up"
    RIGHT_TURN_FORWARD = "right_turn_forward"
    LEFT_TURN_FORWARD = "left_turn_forward"


class CameraConfig(BaseModel):
    """Camera movement configuration."""
    horizontal: float | None = Field(
        None,
        ge=-10,
        le=10,
        description="Horizontal movement (x-axis translation)"
    )
    vertical: float | None = Field(
        None,
        ge=-10,
        le=10,
        description="Vertical movement (y-axis translation)"
    )
    pan: float | None = Field(
        None,
        ge=-10,
        le=10,
        description="Rotation in vertical plane (x-axis rotation)"
    )
    tilt: float | None = Field(
        None,
        ge=-10,
        le=10,
        description="Rotation in horizontal plane (y-axis rotation)"
    )
    roll: float | None = Field(
        None,
        ge=-10,
        le=10,
        description="Roll amount (z-axis rotation)"
    )
    zoom: float | None = Field(
        None,
        ge=-10,
        le=10,
        description="Focal length change (field of view)"
    )

    @validator('*', pre=True)
    def validate_config(cls, v, field):
        """Ensure only one camera parameter is set when using simple type."""
        if v != 0 and field.name != 'horizontal':  # Skip validation for the current field
            if any(v != 0 for v in cls.__annotations__.values() if v != field.name):
                raise ValueError("Only one camera parameter should be non-zero")
        return v


class CameraControl(BaseModel):
    """Camera control parameters."""
    type: CameraControlType = Field(
        CameraControlType.SIMPLE,
        description="Predefined camera movement type"
    )
    config: CameraConfig | None = Field(
        None,
        description="Camera movement configuration"
    )

    @validator('config')
    def validate_config_type(cls, v, values):
        """Validate config based on camera control type."""
        if values.get('type') == CameraControlType.SIMPLE and v is None:
            raise ValueError("Config is required for simple camera control type")
        return v


class TextToVideoRequest(BaseModel):
    """Request model for creating a text-to-video task."""
    model_name: str = Field(
        "kling-v1",
        description="Model to use for generation"
    )
    prompt: str = Field(
        ...,
        max_length=2500,
        description="Positive text prompt"
    )
    negative_prompt: str | None = Field(
        None,
        max_length=2500,
        description="Negative text prompt"
    )
    cfg_scale: float = Field(
        0.5,
        ge=0,
        le=1,
        description="Flexibility in video generation"
    )
    mode: VideoMode = Field(
        VideoMode.STANDARD,
        description="Video generation mode"
    )
    camera_control: CameraControl | None = Field(
        None,
        description="Camera movement control"
    )
    aspect_ratio: Literal["16:9", "9:16", "1:1"] = Field(
        "16:9",
        description="Aspect ratio of the generated video"
    )
    duration: Literal[5, 10] = Field(
        5,
        description="Video length in seconds"
    )
    callback_url: HttpUrl | None = Field(
        None,
        description="Callback URL for task status updates"
    )
    external_task_id: str | None = Field(
        None,
        description="Custom task ID for tracking"
    )

    class Config:
        """Pydantic config."""
        use_enum_values = True
        json_encoders = {
            HttpUrl: str,
        }


def validate_task_id(task_id: str) -> None:
    """Validate task ID format."""
    if not task_id:
        raise ValueError("Task ID cannot be empty")


def validate_external_task_id(external_task_id: str) -> None:
    """Validate external task ID format."""
    if not external_task_id:
        raise ValueError("External task ID cannot be empty")


class KlingAPITextToVideoClient:
    """Client for interacting with the Kling AI Text-to-Video API."""

    def __init__(self, config: KlingConfig) -> None:
        """Initialize the client with configuration."""
        self.config = config
        self.base_url = config.base_url.rstrip("/")
        self.timeout = httpx.Timeout(timeout=config.timeout)
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.client = self._create_client()

    def _create_client(self) -> httpx.AsyncClient:
        """Create and configure the HTTP client."""
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20,
            ),
            http2=True,
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to the Kling AI API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = await self.client.request(
                method=method,
                url=url,
                json=data,
                params=params,
            )

            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "60"))
                raise RateLimitError(
                    "Rate limit exceeded",
                    status_code=response.status_code,
                    response=response.json(),
                    retry_after=retry_after,
                )

            # Handle authentication errors
            if response.status_code == 401:
                raise AuthenticationError(
                    "Invalid API key", status_code=response.status_code
                )

            # Handle not found errors
            if response.status_code == 404:
                raise NotFoundError(
                    "Resource not found", status_code=response.status_code
                )

            # Handle validation errors
            if response.status_code == 422:
                error_data = response.json()
                raise KlingValidationError(
                    message="Validation error",
                    status_code=response.status_code,
                    errors=error_data.get("errors", []),
                )

            # Handle server errors
            if response.status_code >= 500:
                raise ServerError("Server error", status_code=response.status_code)

            # Handle successful responses
            if 200 <= response.status_code < 300:
                return response.json()

            # Handle other error cases
            error_data = response.json()
            raise APIRequestError(
                error_data.get("message", "Unknown error"),
                status_code=response.status_code,
                response=error_data,
            )

        except httpx.TimeoutException as exc:
            raise TimeoutError("Request timed out") from exc

        except json.JSONDecodeError as exc:
            logger.error("Failed to decode JSON response: %s", exc)
            raise APIRequestError("Invalid JSON response") from exc

        except Exception as exc:
            logger.error("Request failed: %s", exc, exc_info=True)
            raise handle_api_error(exc) from exc

    async def create_task(self, request: TextToVideoRequest) -> dict[str, Any]:
        """Create a new text-to-video task."""
        try:
            data = request.dict(exclude_none=True)
            return await self._request("POST", "/v1/videos/text2video", data=data)
        except Exception as exc:
            logger.error("Failed to create task: %s", exc)
            raise

    async def get_task_status(self, task_id: str) -> dict[str, Any]:
        """Get the status of a task."""
        validate_task_id(task_id)
        return await self._request("GET", f"/v1/videos/text2video/{task_id}")

    async def list_tasks(
        self,
        page_num: int = 1,
        page_size: int = 30,
    ) -> dict[str, Any]:
        """List all tasks with pagination."""
        if page_num < 1 or page_num > 1000:
            raise ValueError("page_num must be between 1 and 1000")
        if page_size < 1 or page_size > 500:
            raise ValueError("page_size must be between 1 and 500")
            
        params = {"pageNum": page_num, "pageSize": page_size}
        return await self._request("GET", "/v1/videos/text2video", params=params)

    async def __aenter__(self) -> KlingAPITextToVideoClient:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
