"""
Request models for Kling AI Multi-Image to Video API.
"""
from enum import Enum
from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, validator

from pydantic import BaseModel, Field, HttpUrl, validator


class MultiImageToVideoMode(str, Enum):
    """Video generation modes for multi-image to video."""
    STANDARD = "std"
    PROFESSIONAL = "pro"


class MultiImageToVideoAspectRatio(str, Enum):
    """Supported aspect ratios for multi-image to video."""
    SIXTEEN_NINE = "16:9"
    NINE_SIXTEEN = "9:16"
    ONE_ONE = "1:1"


class ImageItem(BaseModel):
    """Model representing a single image in the image list."""
    image: str = Field(..., description="Image URL or Base64 encoded string")


class MultiImageToVideoRequest(BaseModel):
    """Request model for multi-image to video generation."""
    model_name: str = Field(
        "kling-v1-6",
        description="Model to use for generation. Currently only 'kling-v1-6' is supported."
    )
    image_list: list[ImageItem] = Field(
        ...,
        min_items=1,
        max_items=4,
        description="List of reference images (1-4 images). Each item should contain an 'image' field with URL or Base64."
    )
    prompt: str | None = Field(
        None,
        max_length=2500,
        description="Positive text prompt for video generation. Max 2500 characters."
    )
    negative_prompt: str | None = Field(
        None,
        max_length=2500,
        description="Negative text prompt. Max 2500 characters."
    )
    mode: MultiImageToVideoMode = Field(
        MultiImageToVideoMode.STANDARD,
        description="Video generation mode. 'std' for Standard Mode (cost-effective), 'pro' for Professional Mode (higher quality)."
    )
    duration: Literal[5, 10] = Field(
        5,
        description="Video duration in seconds. Only 5 or 10 seconds are supported."
    )
    aspect_ratio: MultiImageToVideoAspectRatio = Field(
        MultiImageToVideoAspectRatio.SIXTEEN_NINE,
        description="Aspect ratio of the generated video."
    )
    callback_url: HttpUrl | None = Field(
        None,
        description="Callback URL for task status updates."
    )
    external_task_id: str | None = Field(
        None,
        description="Custom task ID for tracking purposes."
    )

    @validator('image_list')
    def validate_image_list(cls, v):
        if not 1 <= len(v) <= 4:
            raise ValueError("Image list must contain between 1 and 4 images")
        return v