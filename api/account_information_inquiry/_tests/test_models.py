"""Tests for account information inquiry models."""
from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from ...base import KlingAPIBaseModel
from .._requests import AccountCostsRequest, ResourcePackStatus, ResourcePackType
from .._responses import AccountCostsResponse, AccountCostsResponseData, ResourcePackInfo


def test_resource_pack_info_serialization():
    """Test serialization of ResourcePackInfo timestamps."""
    now = int(datetime.now().timestamp() * 1000)
    pack_info = ResourcePackInfo(
        resource_pack_name="Test Pack",
        resource_pack_id="test-123",
        resource_pack_type=ResourcePackType.DECREASING_TOTAL,
        total_quantity=100.0,
        remaining_quantity=50.0,
        purchase_time=now,
        effective_time=now,
        invalid_time=now + 86400000,  # 1 day later
        status=ResourcePackStatus.ONLINE
    )
    
    # Test that timestamps are serialized to ISO format
    data = pack_info.model_dump()
    assert isinstance(data["purchase_time"], str)
    assert "T" in data["purchase_time"]


def test_account_costs_request_validation():
    """Test validation of AccountCostsRequest."""
    now = int(datetime.now().timestamp() * 1000)
    
    # Valid request
    request = AccountCostsRequest(
        start_time=now - 86400000,  # 1 day ago
        end_time=now,
        resource_pack_name="Test Pack"
    )
    assert request.start_time < request.end_time
    
    # Test with datetime objects
    request = AccountCostsRequest(
        start_time=datetime.utcnow() - timedelta(days=1),
        end_time=datetime.utcnow()
    )
    assert isinstance(request.start_time, int)
    assert isinstance(request.end_time, int)
    
    # Test invalid time range
    with pytest.raises(ValueError, match="end_time must be after start_time"):
        AccountCostsRequest(
            start_time=now,
            end_time=now - 86400000  # 1 day before start_time
        )


def test_account_costs_response_parsing():
    """Test parsing of AccountCostsResponse."""
    now = int(datetime.now().timestamp() * 1000)
    
    response_data = {
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
    
    # Test parsing from dict
    response = AccountCostsResponse.model_validate(response_data)
    assert response.code == 0
    assert len(response.data.resource_pack_subscribe_infos) == 1
    assert response.data.resource_pack_subscribe_infos[0].resource_pack_name == "Video Generation - 10,000 entries"
