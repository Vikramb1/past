# Quick Start: Face Quality Detection

## TL;DR

Your system now **collects 5 frames** and **saves the sharpest one** automatically. 📸✨

## Quick Test

```bash
cd /Users/vikra/past/face_recognition
python main.py
```

Look for:
```
📸 Starting quality collection (0/5 frames)
📸 Collecting frames: 1/5
...
✨ Best frame selected: Sharpness = 156.3 (Very Good)
```

## Configuration (in `config.py`)

```python
# Default settings (already configured)
ENABLE_QUALITY_CHECK = True
QUALITY_FRAMES_TO_COLLECT = 5
QUALITY_SHARPNESS_THRESHOLD = 100.0  # Balanced
```

## Quick Adjustments

### Strict Quality (only very sharp images)
```python
QUALITY_SHARPNESS_THRESHOLD = 150.0
```

### Lenient Quality (accept softer images)
```python
QUALITY_SHARPNESS_THRESHOLD = 50.0
```

### Faster Collection
```python
QUALITY_FRAMES_TO_COLLECT = 3
```

### More Thorough
```python
QUALITY_FRAMES_TO_COLLECT = 10
```

### Disable Feature
```python
ENABLE_QUALITY_CHECK = False
```

## How It Works

1. **New face detected** → Start collecting
2. **Collect 5 frames** → ~0.5 seconds
3. **Measure sharpness** → Find best
4. **Save sharpest only** → Done!

## Quality Ratings

| Score | Rating | Description |
|-------|--------|-------------|
| 200+ | Excellent | Perfect! |
| 150-199 | Very Good | Great quality |
| 100-149 | Good | Acceptable (default threshold) |
| 50-99 | Fair | Slightly soft |
| <50 | Poor | Blurry |

## Check Results

### View saved images
```bash
ls -lh face_recognition/detected_faces/
```

### View quality scores
```bash
cat data/face_registry.json | python -m json.tool | grep sharpness
```

## Troubleshooting

### No images saved?
→ Lower threshold: `QUALITY_SHARPNESS_THRESHOLD = 50.0`

### Images still blurry?
→ Raise threshold: `QUALITY_SHARPNESS_THRESHOLD = 150.0`

### Too slow?
→ Fewer frames: `QUALITY_FRAMES_TO_COLLECT = 3`

## Documentation

- **Full guide**: See `FACE_QUALITY_GUIDE.md`
- **Summary**: See `QUALITY_UPDATE_SUMMARY.md`
- **Code**: See `face_quality.py`

That's it! The system is ready to go with balanced defaults. 🚀

