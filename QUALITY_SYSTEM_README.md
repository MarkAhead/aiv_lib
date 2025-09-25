# AI Image Generation Quality System

This document describes the quality-based image generation system implemented in the aiv_lib library.

## Overview

The quality system allows you to generate images at different quality levels depending on your use case:

- **LQ (Low Quality)**: Fast generation suitable for testing and prototyping
- **HQ (High Quality)**: Slower generation with production-quality results

## Quality Levels

### LQ (Low Quality) - Default
- **Purpose**: Testing, prototyping, rapid iteration
- **Remote Model**: Stable Diffusion 3.5 (`sd3.5-large`)
- **Local Settings**: 20 inference steps, noise fraction 0.7
- **Prompt**: Simple style additions (`"simple, basic quality"`)
- **Generation Speed**: Faster
- **Seed**: Fixed (42) for consistent testing results

### HQ (High Quality)
- **Purpose**: Production use, final assets
- **Remote Model**: Ultra model (`ultra`)
- **Local Settings**: 50 inference steps, noise fraction 0.8
- **Prompt**: Enhanced style additions (`"ultra real, dramatic lighting, photorealistic, 4k, high resolution, detailed"`)
- **Generation Speed**: Slower
- **Seed**: Random (0) for variety

## Usage Examples

### Basic Usage

```python
from aiv_lib.util_image_ai import generateImages
from aiv_lib.image_quality import ImageQuality

# Default quality (LQ)
generateImages(
    output_folder="./images",
    prompt="a beautiful landscape",
    num_images_to_generate=1
)

# Explicit LQ quality using enum
generateImages(
    output_folder="./images",
    prompt="a beautiful landscape",
    quality=ImageQuality.LQ
)

# HQ quality using enum
generateImages(
    output_folder="./images",
    prompt="a beautiful landscape",
    quality=ImageQuality.HQ
)

# Using string values (case insensitive)
generateImages(
    output_folder="./images",
    prompt="a beautiful landscape",
    quality="LQ"  # or "HQ"
)
```

### Visual Asset Generator Usage

```python
from aiv_lib.image_quality import ImageQuality

# In your asset generation code
visual_generator = VisualAssetGenerator()

# Generate with LQ quality (default)
result = visual_generator.generate_asset_sync(
    content="a majestic mountain",
    output_filename="mountain.jpg",
    local_output_path="/path/to/output.jpg"
)

# Generate with HQ quality
result = visual_generator.generate_asset_sync(
    content="a majestic mountain",
    output_filename="mountain.jpg",
    local_output_path="/path/to/output.jpg",
    quality=ImageQuality.HQ
)

# Using string quality
result = visual_generator.generate_asset_sync(
    content="a majestic mountain",
    output_filename="mountain.jpg",
    local_output_path="/path/to/output.jpg",
    quality="HQ"
)
```

## API Reference

### ImageQuality Enum

```python
from aiv_lib.image_quality import ImageQuality

# Available values
ImageQuality.LQ  # Low Quality
ImageQuality.HQ  # High Quality
```

### Function Signatures

#### generateImages()
```python
def generateImages(
    output_folder: str,
    prompt: str,
    num_images_to_generate: int = 1,
    art_type: Optional[str] = None,
    quality: ImageQuality = ImageQuality.LQ
) -> None
```

#### generateImageByPrompt() - Remote
```python
def generateImageByPrompt(
    output_file: str,
    prompt: str,
    quality: Optional[ImageQuality] = None
) -> None
```

#### generateImageByPrompt() - Local
```python
def generateImageByPrompt(
    output_file: str,
    prompt: str,
    quality: Optional[ImageQuality] = None
) -> None
```

## Model Mapping

### Remote Generation (Stability AI)

| Quality | Model | Endpoint |
|---------|-------|----------|
| LQ | Stable Diffusion 3.5 (`sd3.5-large`) | `/v2beta/stable-image/generate/sd3` |
| HQ | Ultra | `/v2beta/stable-image/generate/ultra` |

### Local Generation (Stable Diffusion XL)

| Quality | Inference Steps | Noise Fraction | Strength (Character Mode) |
|---------|----------------|----------------|---------------------------|
| LQ | 20 | 0.7 | 0.6 |
| HQ | 50 | 0.8 | 0.8 |

## Configuration

The quality system works with existing configuration:

- **Remote**: Requires `STABILITY_API_KEY` in environment variables
- **Local**: Requires `use_local_stable_diffusion_model=TRUE` in config

## Best Practices

### When to Use LQ
- Development and testing phases
- Rapid prototyping
- Content validation
- Batch processing where speed matters
- A/B testing different prompts

### When to Use HQ
- Final production assets
- Client deliverables
- Marketing materials
- High-resolution requirements
- Quality-critical applications

### Parameter Validation
The system automatically handles:
- String to enum conversion (`"LQ"` → `ImageQuality.LQ`)
- Case insensitive strings (`"lq"`, `"LQ"`, `"Lq"` all work)
- Invalid values default to LQ for safety
- None values default to LQ

## Error Handling

The system includes robust error handling:
- Invalid quality values default to LQ
- Missing API keys raise clear error messages
- Model loading failures are logged appropriately
- Generation failures are caught and reported

## Metadata

Generated images include quality metadata:
```python
{
    "quality": "LQ",  # or "HQ"
    "model": "sd3.5-large",  # or "ultra"
    "art_type": "digital art"
}
```

## Migration

Existing code continues to work without changes:
- Default quality is LQ (safe for testing)
- All existing function signatures remain compatible
- No breaking changes to existing workflows

## Testing

Run the test script to verify the quality system:
```bash
python -m aiv_lib.util_image_ai
```

This will generate test images with both quality levels and display the differences in generation parameters. 