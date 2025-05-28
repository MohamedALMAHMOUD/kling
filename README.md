# Kling AI Python SDK

A modern, type-safe Python SDK for interacting with the Kling AI API. This SDK provides a clean, intuitive interface for all Kling AI services including video generation, image processing, and account management.

## ✨ Features

- **Full API Coverage**: Support for all Kling AI endpoints
- **Type Safety**: Built with Pydantic v2 for runtime type checking
- **Async/Await**: Native async support with HTTPX
- **Automatic Retries**: Configurable retry logic for transient failures
- **Comprehensive Models**: Strongly-typed request/response models
- **Developer Experience**: Detailed error messages and logging

## 🚀 Installation

```bash
# Using Poetry (recommended)
poetry add kling-ai-sdk

# Using pip
pip install kling-ai-sdk
```

## 📚 Quick Start

### Basic Usage

```python
from kling.client import KlingClient
from kling.api.text_to_video import TextToVideoRequest

async def main():
    # Initialize client with your API key
    client = KlingClient(api_key="your-api-key")
    
    # Create a text-to-video request
    request = TextToVideoRequest(
        prompt="A beautiful sunset over mountains",
        duration=5.0,
        resolution="1920x1080"
    )
    
    # Submit the request
    response = await client.text_to_video(request)
    print(f"Video generation started with ID: {response.task_id}")

# Run the async function
import asyncio
asyncio.run(main())
```

## 📦 API Modules

### Account Information
- Query resource packages and usage
- Check account limits and quotas

```python
from kling.api.account_information_inquiry import get_account_costs

async def check_usage():
    client = KlingClient(api_key="your-api-key")
    response = await get_account_costs(
        client=client,
        start_time=start_timestamp,
        end_time=end_timestamp
    )
    return response
```

### Callback Protocol
- Handle asynchronous callbacks for long-running tasks
- Process task updates and completions

```python
from kling.api.callback_protocol import CallbackRequest, register_callback_handler

@register_callback_handler
def handle_callback(callback: CallbackRequest):
    print(f"Received callback for task {callback.task_id}")
    print(f"Status: {callback.task_status}")
    if callback.task_result:
        print(f"Result URL: {callback.task_result.video_url}")
```

### Media Generation
- Text-to-Video generation
- Image-to-Video conversion
- Multi-Image Video creation
- Video effects and enhancements
- Virtual Try-On functionality

```python
# Text to Video
from kling.api.text_to_video import TextToVideoRequest

# Image to Video
from kling.api.image_to_video import ImageToVideoRequest

# Video Effects
from kling.api.video_effects import apply_effect
```

## 🔧 Configuration

Configure the client with environment variables or directly:

```python
from kling.client import KlingClient

# Initialize with custom settings
client = KlingClient(
    api_key="your-api-key",
    base_url="https://api.kling.ai/v1",
    timeout=30.0,
    max_retries=3
)
```

### Environment Variables

```bash
export KLING_API_KEY="your-api-key"
export KLING_BASE_URL="https://api.kling.ai/v1"
export KLING_TIMEOUT=30
```

## 🤝 Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) before submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Error Handling

The SDK raises `KlingAPIError` for API-related errors and `ValidationError` for request/response validation issues.

```python
try:
    task = await video_api.create_task(request)
except KlingAPIError as e:
    print(f"API Error: {e}")
except ValidationError as e:
    print(f"Validation Error: {e}")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

MIT
