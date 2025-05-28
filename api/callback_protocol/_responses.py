"""
Response models for the Kling AI Callback Protocol.
"""
import time

from pydantic import BaseModel, Field, HttpUrl


class CallbackAckResponse(BaseModel):
    """Standard acknowledgment response for callback requests."""
    status: str = Field("success", description="Status of the callback processing")
    message: str = Field(..., description="Human-readable message about the result")
    received_at: int = Field(
        default_factory=lambda: int(time.time() * 1000),
        description="Server timestamp when the callback was received (milliseconds since epoch)"
    )
    task_id: str = Field(..., description="The task ID this acknowledgment is for")


class CallbackValidationErrorResponse(BaseModel):
    """Response model for validation errors in callback processing."""
    status: str = Field("error", description="Error status")
    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Detailed error message")
    details: dict | None = Field(
        None,
        description="Additional error details or validation errors"
    )


class CallbackProcessingResponse(BaseModel):
    """Response indicating the callback is being processed asynchronously."""
    status: str = Field("processing", description="Indicates the request is being processed")
    message: str = Field("Callback received and queued for processing")
    task_id: str = Field(..., description="The task ID being processed")
    queue_position: int | None = Field(
        None,
        description="Optional position in processing queue if available"
    )
