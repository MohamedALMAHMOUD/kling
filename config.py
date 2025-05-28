"""
Kling AI API configuration and constants.
"""
from enum import Enum

from pydantic import BaseModel, Field, validator


class KlingModelName(str, Enum):
    """Available Kling AI model names."""
    KLING_V1 = "kling-v1"
    KLING_V1_6 = "kling-v1-6"
    KLING_V2_MASTER = "kling-v2-master"


class VideoMode(str, Enum):
    """Video generation modes."""
    STANDARD = "std"
    PROFESSIONAL = "pro"


class AspectRatio(str, Enum):
    """Video aspect ratios."""
    SIXTEEN_NINE = "16:9"
    NINE_SIXTEEN = "9:16"
    ONE_ONE = "1:1"


class CameraMovementType(str, Enum):
    """Predefined camera movement types."""
    SIMPLE = "simple"
    DOWN_BACK = "down_back"
    FORWARD_UP = "forward_up"
    RIGHT_TURN_FORWARD = "right_turn_forward"
    LEFT_TURN_FORWARD = "left_turn_forward"


class CameraConfig(BaseModel):
    """Camera configuration for video generation."""
    horizontal: float | None = Field(
        None,
        ge=-10,
        le=10,
        description="Horizontal movement (-10 to 10), negative for left, positive for right",
    )
    vertical: float | None = Field(
        None,
        ge=-10,
        le=10,
        description="Vertical movement (-10 to 10), negative for down, positive for up",
    )
    pan: float | None = Field(
        None,
        ge=-10,
        le=10,
        description="Pan movement (-10 to 10), rotation around x-axis",
    )
    tilt: float | None = Field(
        None,
        ge=-10,
        le=10,
        description="Tilt movement (-10 to 10), rotation around y-axis",
    )
    roll: float | None = Field(
        None,
        ge=-10,
        le=10,
        description="Roll movement (-10 to 10), rotation around z-axis",
    )
    zoom: float | None = Field(
        None,
        ge=-10,
        le=10,
        description="Zoom level (-10 to 10), negative for zoom in, positive for zoom out",
    )

    @validator('*', pre=True)
    def check_single_value_set(cls, v, values, field, **kwargs):
        """Ensure only one camera movement parameter is set when type is simple."""
        if field.name == 'type' and v == CameraMovementType.SIMPLE:
            non_none = [k for k, v in values.items() if v is not None and k != 'type']
            if len(non_none) > 1:
                raise ValueError("Only one camera movement parameter can be set when type is 'simple'")
        return v


class CameraControl(BaseModel):
    """Camera control settings for video generation."""
    type: CameraMovementType | None = Field(
        None,
        description="Predefined camera movement type",
    )
    config: CameraConfig | None = Field(
        None,
        description="Camera movement configuration",
    )


class KlingConfig(BaseModel):
    """Main configuration for Kling AI API client."""
    api_key: str = Field(..., description="API key for authentication")
    base_url: str = Field(
        "https://api.klingai.com",
        description="Base URL for the Kling AI API"
    )
    timeout: int = Field(
        30,
        ge=10,
        le=120,
        description="Request timeout in seconds"
    )
    max_retries: int = Field(
        3,
        ge=0,
        le=5,
        description="Maximum number of retries for failed requests"
    )
