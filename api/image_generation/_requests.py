"""Request models for Kling AI Image Generation API."""

from enum import Enum
from typing import TypeAlias

from pydantic import BaseModel, Field, HttpUrl, field_validator


class ModelName(str, Enum):
    """Available Kling AI models for image generation."""
    KLING_V1 = "kling-v1"
    KLING_V1_5 = "kling-v1-5"
    KLING_V2 = "kling-v2"


class ImageReferenceType(str, Enum):
    """Image reference types for image-to-image generation."""
    SUBJECT = "subject"
    FACE = "face"


class AspectRatio(str, Enum):
    """Supported aspect ratios for generated images."""
    RATIO_16_9 = "16:9"
    RATIO_9_16 = "9:16"
    RATIO_1_1 = "1:1"
    RATIO_4_3 = "4:3"
    RATIO_3_4 = "3:4"
    RATIO_3_2 = "3:2"
    RATIO_2_3 = "2:3"
    RATIO_21_9 = "21:9"


# Type aliases for better type hints
Base64Image: TypeAlias = str
ImageUrl: TypeAlias = str
ImageInput: TypeAlias = Base64Image | HttpUrl | None


class ImageGenerationRequest(BaseModel):
    """Request model for creating an image generation task.
    
    Attributes:
        model_name: The model version to use for generation.
        prompt: The text prompt describing the desired image.
        negative_prompt: Optional text describing what to avoid in the image.
        image: Optional reference image as Base64 or URL for image-to-image generation.
        image_reference: Type of reference when using an image.
        image_fidelity: Strength of image reference (0-1).
        human_fidelity: Strength of facial features reference (0-1).
        n: Number of images to generate (1-9).
        aspect_ratio: Desired aspect ratio of the generated images.
        callback_url: Optional URL for task completion callback.
    """
    model_name: ModelName = Field(
        default=ModelName.KLING_V1,
        description="Model version to use for generation.",
    )
    prompt: str = Field(
        ...,
        max_length=2500,
        description="Positive text prompt describing the desired image.",
    )
    negative_prompt: str | None = Field(
        default=None,
        max_length=2500,
        description="Negative text prompt describing what to avoid in the image.",
    )
    image: ImageInput = Field(
        default=None,
        description="Reference image as Base64 or URL for image-to-image generation.",
    )
    image_reference: ImageReferenceType | None = Field(
        default=None,
        description="Type of reference when using an image.",
    )
    image_fidelity: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Face reference intensity for user-uploaded images (0-1).",
    )
    human_fidelity: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Facial reference intensity (0-1), only used when image_reference is 'subject'.",
    )
    n: int = Field(
        default=1,
        ge=1,
        le=9,
        description="Number of images to generate.",
    )
    aspect_ratio: AspectRatio = Field(
        default=AspectRatio.RATIO_16_9,
        description="Aspect ratio of the generated images.",
    )
    callback_url: HttpUrl | None = Field(
        default=None,
        description="Callback URL for task completion notifications.",
    )

    @field_validator("human_fidelity")
    @classmethod
    def validate_human_fidelity(
        cls,
        v: float | None,
        values: dict[str, object],
    ) -> float | None:
        """Validate human_fidelity is only provided when image_reference is 'subject'."""
        if v is not None and values.get("image_reference") != ImageReferenceType.SUBJECT:
            raise ValueError(
                "human_fidelity can only be set when image_reference is 'subject'"
            )
        return v

    @field_validator("image")
    @classmethod
    def validate_image_reference(
        cls,
        v: ImageInput,
        values: dict[str, object],
    ) -> ImageInput:
        """Validate image and image_reference relationship."""
        if v is not None and values.get("model_name") == ModelName.KLING_V1_5:
            if values.get("image_reference") is None:
                raise ValueError(
                    "image_reference is required when image is provided with kling-v1-5 model"
                )
        return v


class TaskListRequest(BaseModel):
    """Request model for listing tasks with pagination.
    
    Attributes:
        page_num: Page number to retrieve (1-1000).
        page_size: Number of items per page (1-500).
    """
    page_num: int = Field(
        default=1,
        ge=1,
        le=1000,
        description="Page number to retrieve.",
    )
    page_size: int = Field(
        default=30,
        ge=1,
        le=500,
        description="Number of items per page.",
    )
