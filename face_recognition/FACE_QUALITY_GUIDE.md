# Face Quality Detection Guide

## Overview

The face quality detection system ensures that only **sharp, clear face images** are saved to the registry. Instead of saving the first detected frame, the system now:

1. 📸 **Collects 5 frames** when a new face is detected
2. 📊 **Measures sharpness** for each frame using Laplacian variance
3. ⭐ **Selects the best** (sharpest) frame
4. 💾 **Saves only the highest quality** image

## How It Works

### Sharpness Detection

The system uses **Laplacian variance** to measure image sharpness:
- **Higher values** = sharper, clearer image
- **Lower values** = blurrier, out-of-focus image

### Quality Ratings

| Sharpness Score | Rating | Description |
|----------------|---------|-------------|
| 200+ | Excellent | Very sharp, perfect focus |
| 150-199 | Very Good | Sharp with good detail |
| 100-149 | Good | Acceptable clarity (default threshold) |
| 50-99 | Fair | Slightly soft, may be usable |
| <50 | Poor | Blurry, out of focus |

## Configuration

### In `config.py`:

```python
# Face quality settings (prevent blurry faces)
ENABLE_QUALITY_CHECK = True  # Enable/disable quality detection
QUALITY_FRAMES_TO_COLLECT = 5  # Number of frames to collect (1-10)
QUALITY_SHARPNESS_THRESHOLD = 100.0  # Minimum quality score
```

### Tuning Options

#### Number of Frames to Collect

```python
QUALITY_FRAMES_TO_COLLECT = 3  # Fast, fewer samples
QUALITY_FRAMES_TO_COLLECT = 5  # Balanced (recommended)
QUALITY_FRAMES_TO_COLLECT = 10  # Thorough, more samples
```

**Trade-offs:**
- **More frames** = Better chance of getting sharp image, but slower
- **Fewer frames** = Faster detection, but may miss best shot

#### Sharpness Threshold

```python
# Strict - only very sharp images
QUALITY_SHARPNESS_THRESHOLD = 150.0

# Balanced - good quality (recommended)
QUALITY_SHARPNESS_THRESHOLD = 100.0

# Lenient - accept softer images
QUALITY_SHARPNESS_THRESHOLD = 50.0

# No threshold - save best available
QUALITY_SHARPNESS_THRESHOLD = 0.0
```

**Use Cases:**
- **Security/ID verification**: Use strict (150+)
- **General use**: Use balanced (100)
- **Low-light/difficult conditions**: Use lenient (50)

## What You'll See

### Console Output

When a new face is detected:

```bash
📸 Starting quality collection (0/5 frames)
📸 Collecting frames: 1/5
📸 Collecting frames: 2/5
📸 Collecting frames: 3/5
📸 Collecting frames: 4/5
📸 Collecting frames: 5/5
✨ Best frame selected: Sharpness = 156.3 (Very Good)
New face detected and saved: person_006_1729901234.png
   Supabase URL: https://...
```

### Registry Data

Each saved face now includes quality metrics:

```json
{
  "person_006": {
    "id": "person_006",
    "image_filename": "person_006_1729901234.png",
    "sharpness_score": 156.3,
    "quality_rating": "Very Good",
    ...
  }
}
```

## Testing the Feature

### 1. Test with Different Conditions

**Sharp Conditions:**
- Good lighting
- Steady camera
- Face in focus
- Person not moving

**Expected:** High sharpness scores (150-300+)

**Challenging Conditions:**
- Low light
- Moving person
- Camera shake
- Out of focus

**Expected:** Lower scores, system selects best available

### 2. View Quality Metrics

After detection, check the registry:

```bash
cat data/face_registry.json | python -m json.tool
```

Look for `sharpness_score` and `quality_rating` fields.

### 3. Compare Images

Before and after enabling quality check:

```bash
# Check detected_faces/ directory
ls -lh face_recognition/detected_faces/
```

Images should be noticeably sharper with quality check enabled.

## Disabling Quality Check

If you want immediate saving (no quality check):

```python
# In config.py
ENABLE_QUALITY_CHECK = False
```

The system will revert to saving the first detected frame immediately.

## Advanced: Custom Quality Thresholds

You can programmatically adjust thresholds:

```python
from face_quality import FaceQualityDetector

# Use preset thresholds
detector = FaceQualityDetector(
    threshold=FaceQualityDetector.STRICT_THRESHOLD  # 150
)

# Or custom threshold
detector = FaceQualityDetector(threshold=125.0)
```

## Performance Impact

### Frame Collection

- **Additional delay**: ~0.5-1.0 seconds per new face
- **Memory**: Stores 5 frames temporarily (~5MB)
- **CPU**: Minimal (Laplacian calculation is fast)

### When to Disable

Disable quality check if:
- You need instant face saving
- Storage space is extremely limited
- Processing power is very constrained
- Frame rate is already slow

## Troubleshooting

### "No frames collected" Error

**Problem:** Collection didn't capture any frames

**Solutions:**
- Check camera is working
- Ensure face stays visible during collection
- Verify `QUALITY_FRAMES_TO_COLLECT` is reasonable (3-10)

### All Images Rated "Poor"

**Problem:** Sharpness scores consistently low

**Possible causes:**
- Camera out of focus → Adjust camera focus
- Low lighting → Improve lighting
- Camera shake → Stabilize camera
- Dirty lens → Clean camera lens

**Solutions:**
- Lower `QUALITY_SHARPNESS_THRESHOLD`
- Improve lighting conditions
- Use better camera
- Increase `QUALITY_FRAMES_TO_COLLECT` for more chances

### Frame Collection Too Slow

**Problem:** Takes too long to save faces

**Solutions:**
```python
# Reduce frames to collect
QUALITY_FRAMES_TO_COLLECT = 3

# Or disable quality check
ENABLE_QUALITY_CHECK = False
```

## Best Practices

### 1. Start with Defaults

```python
ENABLE_QUALITY_CHECK = True
QUALITY_FRAMES_TO_COLLECT = 5
QUALITY_SHARPNESS_THRESHOLD = 100.0
```

### 2. Tune Based on Results

- **Too many blurry images saved?** → Increase threshold to 150
- **No images being saved?** → Decrease threshold to 50
- **Takes too long?** → Reduce frames to 3
- **Not enough samples?** → Increase frames to 10

### 3. Match Threshold to Use Case

| Use Case | Recommended Threshold |
|----------|----------------------|
| Security/ID verification | 150 (strict) |
| Social media/fun app | 100 (balanced) |
| Low-light surveillance | 50 (lenient) |
| Research/documentation | 200+ (excellent only) |

### 4. Monitor Quality Metrics

Regularly check `face_registry.json` to see actual sharpness scores:

```bash
# View sharpness scores
grep "sharpness_score" data/face_registry.json
```

Adjust thresholds based on what scores you're seeing in practice.

## Technical Details

### Laplacian Variance Method

The system uses the **Laplacian operator** to detect edges in the image:

1. Convert image to grayscale
2. Apply Laplacian filter (detects edges)
3. Calculate variance of the result
4. Higher variance = more edges = sharper image

### Why It Works

- Sharp images have **distinct edges** → high variance
- Blurry images have **soft edges** → low variance
- Fast to compute (~1ms per image)
- Hardware-independent (no GPU needed)

### Alternative Methods

Other sharpness detection methods (not currently used):
- **FFT-based**: Analyzes frequency content
- **Gradient-based**: Measures edge intensity
- **Neural network**: Learned quality assessment

The Laplacian method is chosen for its **speed and reliability**.

## Examples

### Example 1: Good Lighting

```
Frame 1: Sharpness = 145.2
Frame 2: Sharpness = 178.6  ← Best
Frame 3: Sharpness = 162.1
Frame 4: Sharpness = 151.8
Frame 5: Sharpness = 169.3

✨ Selected Frame 2 (178.6 - Very Good)
```

### Example 2: Low Lighting

```
Frame 1: Sharpness = 45.8
Frame 2: Sharpness = 52.1
Frame 3: Sharpness = 68.9  ← Best
Frame 4: Sharpness = 47.2
Frame 5: Sharpness = 51.4

✨ Selected Frame 3 (68.9 - Fair)
⚠️  Quality below threshold (100), but saved best available
```

### Example 3: Motion Blur

```
Frame 1: Sharpness = 89.2
Frame 2: Sharpness = 32.1  (person moving)
Frame 3: Sharpness = 28.5  (person moving)
Frame 4: Sharpness = 134.7  ← Best (person stopped)
Frame 5: Sharpness = 91.3

✨ Selected Frame 4 (134.7 - Good)
```

## Summary

✅ **Enable quality check** for production use
✅ **Use balanced threshold (100)** as default
✅ **Collect 5 frames** for best results
✅ **Monitor quality metrics** in registry
✅ **Tune based on your environment**

The quality detection system ensures you save only the **best possible face images** without manual intervention! 🎯

