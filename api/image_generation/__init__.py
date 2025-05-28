"""Kling AI Image Generation API client.

This module provides a Python client for interacting with the Kling AI Image Generation API.
It handles authentication, request/response serialization, error handling, and retries.

Example:
    ```python
    from kling.api.image_to_generation import (
        KlingAIClient,
        ImageGenerationRequest,
        ModelName,
        AspectRatio,
    )

    async def generate_image():
        # Initialize client
        client = KlingAIClient(api_key="your-api-key")
        
        # Create a request
        request = ImageGenerationRequest(
            model_name=ModelName.KLING_V1_5,
            prompt="A beautiful sunset over mountains",
            aspect_ratio=AspectRatio.RATIO_16_9,
            n=2,
        )
        
        # Create task
        response = await client.create_image_generation_task(request)
        task_id = response.task_id
        
        # Wait for completion
        task = await client.wait_for_task_completion(task_id)
        
        # Get results
        if task.task_status == "succeed" and task.task_result:
            for image in task.task_result.images:
                print(f"Generated image URL: {image.url}")
    ```
"""

from .client import KlingAIClient, get_client
from ._requests import (
    ImageGenerationRequest,
    TaskListRequest,
    ModelName,
    ImageReferenceType,
    AspectRatio,
)
from ._responses import (
    TaskResponse,
    TaskListResponse,
    TaskCreateResponse,
    TaskStatus,
    GeneratedImage,
)
from ._exceptions import (
    KlingAIError,
    APIError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    TimeoutError,
    ServiceUnavailableError,
    handle_api_error,
)

# Re-export public API
__all__ = [
    # Client
    "KlingAIClient",
    "get_client",
    # Requests
    "ImageGenerationRequest",
    "TaskListRequest",
    "ModelName",
    "ImageReferenceType",
    "AspectRatio",
    # Responses
    "TaskResponse",
    "TaskListResponse",
    "TaskCreateResponse",
    "TaskStatus",
    "GeneratedImage",
    # Exceptions
    "KlingAIError",
    "APIError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "TimeoutError",
    "ServiceUnavailableError",
    "handle_api_error",
]
