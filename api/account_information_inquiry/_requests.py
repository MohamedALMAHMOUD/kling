"""
Request models for the Kling AI Account Information Inquiry API.
"""
from enum import Enum
from typing import Literal, Optional

from pydantic import Field, field_validator

from ..base import KlingAPIBaseModel


class ResourcePackType(str, Enum):
    """Resource package types."""
    DECREASING_TOTAL = "decreasing_total"
    CONSTANT_PERIOD = "constant_period"


class ResourcePackStatus(str, Enum):
    """Resource package statuses."""
    TO_BE_ONLINE = "toBeOnline"
    ONLINE = "online"
    EXPIRED = "expired"
    RUN_OUT = "runOut"


class AccountCostsRequest(KlingAPIBaseModel):
    """Request model for querying account costs and resource packages."""
    start_time: int = Field(..., ge=0, description="Start time for the query, Unix timestamp in ms")
    end_time: int = Field(..., ge=0, description="End time for the query, Unix timestamp in ms")
    resource_pack_name: Optional[str] = Field(
        None,
        description="Resource package name for precise querying of a specific package"
    )

    @field_validator('end_time')
    @classmethod
    def validate_times(cls, v, values):
        """Validate that end_time is after start_time."""
        if 'start_time' in values and v < values['start_time']:
            raise ValueError("end_time must be after start_time")
        return v
