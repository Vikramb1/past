# OBS Camera Stream Implementation

## Overview
Added support for external camera stream (like OBS Virtual Camera) with automatic camera detection and fallback to MacBook camera.

## Changes Made

### 1. Config (`config.py`)
Added new stream type constant:
```python
STREAM_TYPE_CAMERA = "camera"  # External camera (skips 0,1)
```

### 2. Stream Handler (`stream_handler.py`)

#### New Method: `_find_camera()`
Searches for available cameras, skipping indices 0 and 1 (MacBook and external USB):
- Searches camera indices 0-5
- Skips indices [0, 1] by default
- Uses `cv2.CAP_ANY` flag for compatibility
- Returns first available camera index or None

#### Updated `__init__` Method
- Added handling for `STREAM_TYPE_CAMERA`
- Allows `source=None` for camera type (will be determined by search)
- Only raises ValueError for network streams without source

#### Updated `_initialize_stream()` Method
Added camera search and fallback logic:
1. If stream type is "camera", calls `_find_camera()`
2. If camera found (index 2-5), uses that camera
3. If no camera found, falls back to MacBook camera (index 0)
4. Prints clear messages about which camera is being used

### 3. Main Application (`main.py`)
Updated argument parser to include new stream type:
- Added `config.STREAM_TYPE_CAMERA` to choices list
- Now accepts `--type camera` command line argument

## Usage

### Run with External Camera (OBS Virtual Camera)
```bash
python main.py --type camera
```

This will:
1. Search for cameras at indices 2-5
2. Use the first available external camera found
3. If none found, automatically fall back to MacBook camera (index 0)

### Default Behavior (MacBook Camera)
```bash
python main.py
# or
python main.py --type webcam
```

### Other Stream Types
```bash
# External USB camera (index 1)
python main.py --type external

# Network stream
python main.py --type network --source rtsp://example.com/stream
```

## Camera Search Strategy

Based on `test.py`, the search:
- Checks indices 0-5
- Skips index 0 (MacBook built-in camera)
- Skips index 1 (typical external USB camera)
- Returns first camera that successfully opens at indices 2-5

## Fallback Behavior

If no external camera is found (indices 2-5):
- Automatically falls back to MacBook camera (index 0)
- Prints: "No external camera found, falling back to MacBook camera (index 0)"
- Application continues running normally

## Technical Details

### Camera Detection
```python
def _find_camera(self, max_idx: int = 6, skip_indices: list = [0, 1]) -> Optional[int]:
    for i in range(max_idx):
        if i in skip_indices:
            continue
        cap = cv2.VideoCapture(i, cv2.CAP_ANY)
        if cap.isOpened():
            cap.release()
            print(f"Found camera at index {i}")
            return i
    return None
```

### Initialization Logic
```python
if self.stream_type == config.STREAM_TYPE_CAMERA:
    camera_idx = self._find_camera()
    if camera_idx is not None:
        self.source = camera_idx
        print(f"Using external camera at index {camera_idx}")
    else:
        self.source = config.DEFAULT_CAMERA_INDEX
        print(f"No external camera found, falling back to MacBook camera (index {self.source})")
```

## Files Modified
- `face_recognition/config.py` - Added STREAM_TYPE_CAMERA constant
- `face_recognition/stream_handler.py` - Added camera search and fallback logic
- `face_recognition/main.py` - Updated argument parser choices

## Testing

1. **With OBS Virtual Camera running:**
   ```bash
   python main.py --type camera
   # Should detect and use OBS camera
   ```

2. **Without OBS Virtual Camera:**
   ```bash
   python main.py --type camera
   # Should fall back to MacBook camera
   ```

3. **Default behavior unchanged:**
   ```bash
   python main.py
   # Should use MacBook camera as before
   ```

