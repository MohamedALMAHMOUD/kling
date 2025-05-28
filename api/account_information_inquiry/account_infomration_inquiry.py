"""
Account Information Inquiry API for Kling AI.

This module provides functionality to query resource package lists and remaining quantities
under your Kling AI account.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from ...client import KlingClient
from ._requests import AccountCostsRequest
from ._responses import AccountCostsResponse

if TYPE_CHECKING:
    from datetime import datetime

__all__ = [
    # Models
    "AccountCostsRequest",
    "AccountCostsResponse",
    # Client methods
    "get_account_costs",
]

# API endpoint
ACCOUNT_COSTS_ENDPOINT = "/account/costs"


async def get_account_costs(
    client: KlingClient,
    start_time: int | datetime,
    end_time: int | datetime,
    resource_pack_name: str | None = None,
) -> AccountCostsResponse:
    """
    Query resource package list and remaining quantity under the account.

    Note: Please control the request rate (QPS <= 1).

    Args:
        client: Authenticated KlingAPIClient instance
        start_time: Start time for the query (Unix timestamp in ms or datetime object)
        end_time: End time for the query (Unix timestamp in ms or datetime object)
        resource_pack_name: Optional resource package name for filtering

    Returns:
        AccountCostsResponse containing the resource package information

    Example:
        ```python
        from datetime import datetime, timedelta
        from kling.client import KlingAPIClient
        from kling.api.account_information_inquiry import get_account_costs

        client = KlingAPIClient(api_key="your-api-key")
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=30)

        response = await get_account_costs(
            client=client,
            start_time=start_time,
            end_time=end_time
        )
        ```
    """
    # Convert datetime to timestamp if needed
    if hasattr(start_time, 'timestamp'):
        start_time = int(start_time.timestamp() * 1000)
    if hasattr(end_time, 'timestamp'):
        end_time = int(end_time.timestamp() * 1000)

    # Build request parameters
    params = {
        "start_time": start_time,
        "end_time": end_time,
    }
    if resource_pack_name is not None:
        params["resource_pack_name"] = resource_pack_name

    # Make the API request
    response = await client.get(
        ACCOUNT_COSTS_ENDPOINT,
        params=params,
        response_model=AccountCostsResponse,
    )

    return response
