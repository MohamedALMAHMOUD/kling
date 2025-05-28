"""
Request models for the Virtual Try-On API.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator, HttpUrl


class ModelName(str, Enum):
    """Available virtual try-on models."""
    KOLORS_V1 = "kolors-virtual-try-on-v1"
    KOLORS_V1_5 = "kolors-virtual-try-on-v1-5"


class ImageSource(BaseModel):
    """Base model for image sources (URL or Base64)."""
    url: HttpUrl | None = Field(
        None,
        description="URL of the image (must be accessible)"
    )
    base64: str | None = Field(
        None,
        description="Base64-encoded image data (without data: prefix)",
        min_length=100,  # Minimum length for a valid base64 image
        max_length=15_000_000,  # ~10MB of base64 data
        pattern=r"^[A-Za-z0-9+/=]+$"  # Basic base64 pattern
    )

    @field_validator('base64')
    @classmethod
    def validate_base64(cls, v: str | None) -> str | None:
        """Validate base64 string format."""
        if v is None:
            return None
        
        # Remove data: prefix if present
        if v.startswith(('data:image/png;base64,', 'data:image/jpeg;base64,')):
            v = v.split(',', 1)[1]
        
        # Validate base64 characters
        import base64
        import binascii
        
        try:
            # Try to decode to verify it's valid base64
            base64.b64decode(v, validate=True)
            return v
        except (binascii.Error, ValueError) as e:
            raise ValueError("Invalid base64 image data") from e

    def model_dump(self, **kwargs) -> dict:
        """Override dump to return only the non-None value."""
        data = super().model_dump(**kwargs)
        if self.url is not None:
            return {"url": str(self.url)}
        if self.base64 is not None:
            return {"base64": self.base64}
        raise ValueError("Either url or base64 must be provided")


class VirtualTryOnRequest(BaseModel):
    """Request model for creating a virtual try-on task."""
    model_name: ModelName = Field(
        default=ModelName.KOLORS_V1_5,
        description="Model to use for virtual try-on"
    )
    human_image: ImageSource = Field(
        ...,
        description="Reference human image (Base64 or URL)"
    )
    cloth_image: ImageSource | None = Field(
        None,
        description="Reference clothing image (Base64 or URL). "
                  "Not required for v1.5 model if using human with clothing."
    )
    callback_url: HttpUrl | None = Field(
        None,
        description="Callback URL for task completion notification"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "kolors-virtual-try-on-v1-5",
                "human_image": {
                    "url": "https://example.com/human.jpg"
                },
                "cloth_image": {
                    "url": "https://example.com/cloth.jpg"
                },
                "callback_url": "https://example.com/callback"
            }
        }


class TaskListQuery(BaseModel):
    """Query parameters for listing virtual try-on tasks.
    
    Attributes:
        page_num: Page number (1-based)
        page_size: Number of items per page (1-100)
    """
    page_num: int = Field(
        default=1,
        ge=1,
        le=1000,
        description="Page number (1-based)",
        alias="pageNum"
    )
    page_size: int = Field(
        default=30,
        ge=1,
        le=100,
        description="Number of items per page (1-100)",
        alias="pageSize"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "pageNum": 1,
                "pageSize": 30
            }
        }
