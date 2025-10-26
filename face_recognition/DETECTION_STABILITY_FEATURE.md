# Multi-Frame Detection Stability Feature

## Overview
Implemented a detection stability requirement that ensures faces are consistently detected across multiple consecutive frames before saving. This significantly reduces false positives and improves the quality of saved faces.

## Problem Solved
Previously, the system would start saving a face as soon as it was detected as "new" (not matching any existing person). This could lead to:
- **False positives** from momentary misdetections
- **Transient faces** (people walking by quickly) being saved
- **Unstable detections** polluting the detected_faces folder
- **Unnecessary Supabase uploads** for faces that were only briefly visible

## Solution: Two-Stage Filtering

### Stage 1: Detection Stability (NEW)
- Requires face to be detected consistently for **5 consecutive frames**
- Prevents saving faces that are only briefly or incorrectly detected
- Automatically cleans up stale candidates after 2 seconds

### Stage 2: Quality Selection (EXISTING)
- Once stability is confirmed, collects **5 more frames**
- Selects the best quality frame based on sharpness
- Only applies if `ENABLE_QUALITY_CHECK = True`

**Total pipeline**: ~10 frames (~0.3-0.5 seconds at 30fps) before saving

## Configuration

### New Setting (`config.py`)
```python
DETECTION_STABILITY_FRAMES = 5  # Require N consecutive frames before saving
```

**Recommendations:**
- `3 frames`: Fast detection, some risk of false positives
- `5 frames` (default): Good balance between speed and accuracy
- `10 frames`: Very conservative, minimal false positives

Set to `1` to disable stability checking (immediate save after detection).

## Implementation Details

### 1. Detection Candidate Tracking (`face_tracker.py`)

**New instance variables:**
```python
self.detection_candidates = {}  # Temporary tracking for new faces
self.detection_stability_threshold = config.DETECTION_STABILITY_FRAMES
```

**Candidate structure:**
```python
{
    'candidate_1234567890': {
        'encoding': np.array(...),  # Face encoding
        'count': 3,                  # Number of consecutive detections
        'last_seen': 1234567890.5    # Timestamp of last detection
    }
}
```

### 2. Updated `track_face()` Flow

**Old flow:**
```
Detect face → Check if duplicate → If new, save immediately (or start quality check)
```

**New flow:**
```
Detect face → Check if duplicate → If new, add to candidates (count=1)
Next frame: Same face? → Increment count (count=2)
...
After 5 frames: Stability reached → Proceed to save/quality check
```

### 3. New Helper Methods

#### `_check_detection_candidate(encoding)`
- Checks if face encoding matches an existing candidate
- Cleans up stale candidates (not seen for 2+ seconds)
- Returns candidate ID if match found, None otherwise

#### `_add_detection_candidate(encoding)`
- Creates a new candidate entry
- Generates unique candidate ID with timestamp
- Initializes count to 1

#### `_save_face_immediately(face_image, encoding, location)`
- Extracted from existing code for code reuse
- Handles immediate save without quality check
- Used when `ENABLE_QUALITY_CHECK = False`

### 4. Automatic Cleanup

Stale candidates are automatically removed:
- **Trigger**: If not detected for 2+ seconds
- **When**: During each `_check_detection_candidate()` call
- **Effect**: Prevents memory accumulation for briefly seen faces

## User Experience

### Console Output

**Stage 1: Detection Stability**
```
🔍 New face candidate detected (1/5 frames)
🔍 Face candidate stable (2/5 frames)
🔍 Face candidate stable (3/5 frames)
🔍 Face candidate stable (4/5 frames)
🔍 Face candidate stable (5/5 frames)
✅ Face stable for 5 frames - proceeding to save
```

**Stage 2: Quality Collection** (if enabled)
```
📸 Starting quality collection (0/5 frames)
📸 Collecting frames: 1/5
📸 Collecting frames: 2/5
📸 Collecting frames: 3/5
📸 Collecting frames: 4/5
📸 Collecting frames: 5/5
✨ Best frame selected: Sharpness = 142.3 (Good)
💾 Saved new face: person_027
```

**Cleanup Message:**
```
🧹 Cleaned up stale candidate: candidate_1234567890
```

## Benefits

### 1. **Reduced False Positives**
- Momentary misdetections don't trigger saves
- More reliable face tracking overall

### 2. **Better Resource Usage**
- Fewer unnecessary file saves
- Reduced Supabase API calls and storage
- Lower database query load

### 3. **Cleaner Data**
- Only faces with stable presence are saved
- Easier to review detected faces folder
- More meaningful person tracking

### 4. **Configurable Trade-offs**
- Adjust threshold based on use case
- High-traffic area? Use higher threshold (7-10 frames)
- Low-traffic area? Use lower threshold (3-5 frames)

## Performance Impact

**Minimal CPU/Memory Impact:**
- Lightweight dict operations
- Face encoding comparisons already optimized
- Automatic cleanup prevents memory accumulation

**Typical memory usage:**
- ~1 KB per candidate (encoding + metadata)
- Max ~5-10 candidates at a time in normal use
- Auto-cleanup after 2 seconds

**Latency:**
- Adds ~0.17 seconds at 30fps (5 frames)
- Adds ~0.33 seconds at 15fps (5 frames)
- Acceptable trade-off for better accuracy

## Edge Cases Handled

### 1. **Face Leaves Frame**
- Candidate not detected for 2+ seconds → Auto-cleanup
- No save occurs
- Memory released

### 2. **Multiple Faces**
- Each face tracked independently
- Separate candidate tracking per person
- No interference between candidates

### 3. **Rapid Face Changes**
- New face appears while collecting stability → New candidate created
- Both tracked independently
- Proper cleanup when faces leave

### 4. **Existing Person Re-appears**
- Immediately recognized (no stability check needed)
- Detection count incremented
- No new save triggered

## Testing Recommendations

### Test Case 1: Stable Face Detection
1. Stand in front of camera for 1-2 seconds
2. Should see 5 stability messages
3. Followed by quality collection (if enabled)
4. Face should be saved

### Test Case 2: Brief Appearance
1. Walk quickly past camera
2. May see 1-3 stability messages
3. No save should occur
4. Candidate should be cleaned up

### Test Case 3: Multiple People
1. Have 2-3 people in frame
2. Each should get independent stability tracking
3. All stable faces should be saved
4. No interference between people

### Test Case 4: Re-recognition
1. Get face saved (person_001)
2. Leave frame and return
3. Should be immediately recognized as person_001
4. No new save, no stability check

## Future Enhancements

Potential improvements:
1. **Adaptive thresholds**: Adjust based on scene complexity
2. **Motion detection**: Higher threshold for moving faces
3. **Confidence weighting**: Require higher confidence for fewer frames
4. **Distance consideration**: Closer faces need fewer stability frames
5. **Historical stability**: Track long-term stability patterns

## Backward Compatibility

Fully backward compatible:
- Set `DETECTION_STABILITY_FRAMES = 1` for old behavior
- No changes to database schema
- No changes to existing saved faces
- No changes to recognition logic

## Related Settings

Works in conjunction with:
- `AUTO_SAVE_DETECTED_FACES`: Must be `True` for feature to activate
- `ENABLE_QUALITY_CHECK`: Adds second stage of filtering
- `QUALITY_FRAMES_TO_COLLECT`: Number of quality frames to collect
- `DUPLICATE_THRESHOLD`: Used for both stability and duplicate detection

