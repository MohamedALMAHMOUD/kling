"""Tests for account information inquiry client."""
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import ValidationError

from kling.api.account_information_inquiry import get_account_costs
from kling.client import KlingAPIClient


@pytest.mark.asyncio
async def test_get_account_costs():
    """Test get_account_costs client function."""
    # Setup test data
    now = int(datetime.utcnow().timestamp() * 1000)
    start_time = now - 86400000  # 1 day ago
    end_time = now
    
    # Mock response data
    mock_response = {
        "code": 0,
        "message": "success",
        "request_id": "req-123",
        "data": {
            "code": 0,
            "msg": "success",
            "resource_pack_subscribe_infos": [
                {
                    "resource_pack_name": "Video Generation - 10,000 entries",
                    "resource_pack_id": "509f3fd3d4ab4a3f9eec5db27aa44f27",
                    "resource_pack_type": "decreasing_total",
                    "total_quantity": 200.0,
                    "remaining_quantity": 118.0,
                    "purchase_time": now,
                    "effective_time": now,
                    "invalid_time": now + 86400000,
                    "status": "online"
                }
            ]
        }
    }
    
    # Create a mock client
    mock_client = AsyncMock(spec=KlingAPIClient)
    mock_client.get.return_value = mock_response
    
    # Call the function
    response = await get_account_costs(
        client=mock_client,
        start_time=start_time,
        end_time=end_time,
        resource_pack_name="Video Generation"
    )
    
    # Assert the client was called with the correct parameters
    mock_client.get.assert_awaited_once()
    args, kwargs = mock_client.get.await_args
    assert args[0] == "/account/costs"
    assert kwargs["params"]["start_time"] == start_time
    assert kwargs["params"]["end_time"] == end_time
    assert kwargs["params"]["resource_pack_name"] == "Video Generation"
    
    # Assert the response was parsed correctly
    assert response.code == 0
    assert len(response.data.resource_pack_subscribe_infos) == 1
    assert response.data.resource_pack_subscribe_infos[0].resource_pack_name == "Video Generation - 10,000 entries"


@pytest.mark.asyncio
async def test_get_account_costs_with_datetime():
    """Test get_account_costs with datetime objects."""
    # Setup test data with datetime objects
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=1)
    
    # Mock response data
    mock_response = {"code": 0, "message": "success", "request_id": "req-123", "data": {"code": 0, "msg": "success", "resource_pack_subscribe_infos": []}}
    
    # Create a mock client
    mock_client = AsyncMock(spec=KlingAPIClient)
    mock_client.get.return_value = mock_response
    
    # Call the function with datetime objects
    await get_account_costs(
        client=mock_client,
        start_time=start_time,
        end_time=end_time
    )
    
    # Assert the timestamps were converted correctly
    args, kwargs = mock_client.get.await_args
    assert isinstance(kwargs["params"]["start_time"], int)
    assert isinstance(kwargs["params"]["end_time"], int)
    assert kwargs["params"]["start_time"] < kwargs["params"]["end_time"]
