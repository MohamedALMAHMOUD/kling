"""
Response models for the Kling AI Account Information Inquiry API.
"""
from datetime import datetime
from typing import Optional

from pydantic import Field, field_serializer

from ..base import KlingAPIBaseModel
from ._requests import ResourcePackStatus, ResourcePackType


class ResourcePackInfo(KlingAPIBaseModel):
    """Information about a resource package."""
    resource_pack_name: str = Field(..., description="Resource package name")
    resource_pack_id: str = Field(..., description="Resource package ID")
    resource_pack_type: ResourcePackType = Field(..., description="Resource package type")
    total_quantity: float = Field(..., description="Total quantity in the package")
    remaining_quantity: float = Field(..., description="Remaining quantity (updated with a 12-hour delay)")
    purchase_time: int = Field(..., description="Purchase time, Unix timestamp in ms")
    effective_time: int = Field(..., description="Effective time, Unix timestamp in ms")
    invalid_time: int = Field(..., description="Expiration time, Unix timestamp in ms")
    status: ResourcePackStatus = Field(..., description="Resource package status")

    @field_serializer('purchase_time', 'effective_time', 'invalid_time')
    def serialize_timestamps(self, v: int) -> str:
        """Convert timestamp to ISO format for better readability."""
        return datetime.fromtimestamp(v / 1000).isoformat()


class AccountCostsResponseData(KlingAPIBaseModel):
    """Response data for account costs query."""
    code: int = Field(..., description="Error code")
    msg: str = Field(..., description="Error message")
    resource_pack_subscribe_infos: list[ResourcePackInfo] = Field(
        default_factory=list,
        description="List of resource packages"
    )


class AccountCostsResponse(KlingAPIBaseModel):
    """Response model for account costs query."""
    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    request_id: str = Field(..., description="Request ID for tracking and troubleshooting")
    data: AccountCostsResponseData = Field(..., description="Response data")
