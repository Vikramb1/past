# Automatic Face Detection & Saving Feature

## Overview

The face recognition system now automatically detects and saves all unique faces with duplicate prevention. This allows you to identify people after the fact by reviewing the saved face images.

## How It Works

### Detection & Saving Process

1. **Face Detection**: System detects all faces in video stream
2. **Encoding Comparison**: Compares face encoding to previously saved faces
3. **Duplicate Check**: If distance > threshold (0.6), it's a new person
4. **Auto-Save**: Saves face image with incremental ID (person_001, person_002, etc.)
5. **Registry Update**: Updates JSON registry with metadata

### Storage Structure

```
face_recognition/
├── detected_faces/          # Saved face images
│   ├── person_001.jpg
│   ├── person_002.jpg
│   ├── person_003.jpg
│   └── ...
└── data/
    └── face_registry.json   # Metadata tracking
```

### Registry Format

```json
{
  "person_001": {
    "id": "person_001",
    "first_seen": "2025-10-25T14:30:22.123456",
    "last_seen": "2025-10-25T14:35:10.987654",
    "image_path": "detected_faces/person_001.jpg",
    "encoding_hash": "abc123def456...",
    "detection_count": 15
  }
}
```

## Key Features

✓ **Automatic Saving**: No manual intervention required  
✓ **Duplicate Prevention**: Face encoding comparison prevents re-saving same person  
✓ **Persistent Tracking**: Survives application restarts  
✓ **Incremental IDs**: person_001, person_002, person_003, ...  
✓ **Metadata Tracking**: Timestamps, detection counts, encoding hashes  
✓ **Configurable Threshold**: Adjust duplicate detection sensitivity  

## Configuration

Edit `config.py` to customize:

```python
# Enable/disable auto-save
AUTO_SAVE_DETECTED_FACES = True

# Duplicate detection threshold (0.0 - 1.0)
# Lower = stricter (more likely to save duplicates)
# Higher = more lenient (might miss some unique faces)
DUPLICATE_THRESHOLD = 0.6
```

## Usage Workflow

### 1. Run the Application

```bash
cd face_recognition
python main.py
```

Faces are automatically saved as they're detected.

### 2. Review Detected Faces

```bash
ls detected_faces/
# person_001.jpg  person_002.jpg  person_003.jpg ...

# View registry
cat data/face_registry.json
```

### 3. Identify People

Open `detected_faces/` and review the saved images to identify who people are.

### 4. Add to Known Faces (Optional)

Once identified, add to known faces for future recognition:

```bash
# Create directory for identified person
mkdir -p known_faces/john_doe

# Copy or move detected face
cp detected_faces/person_001.jpg known_faces/john_doe/

# Add more photos if available
cp ~/photos/john_*.jpg known_faces/john_doe/

# Restart app - john_doe will now be recognized
python main.py
```

## On-Screen Display

When auto-save is enabled, you'll see tracked IDs on screen:

- **Unknown Faces**: Shows "person_001", "person_002", etc.
- **Known Faces**: Shows "John Doe (person_001)" if also recognized

## Performance Impact

Minimal impact on performance:
- Face encoding comparison: ~1ms per detected face
- Image saving: Asynchronous, doesn't block processing
- Memory: Tracks encodings in RAM for fast comparison

## Persistence

The system maintains state across restarts:

1. **On Startup**: Loads existing registry and face encodings
2. **During Runtime**: Updates registry as new faces detected
3. **On Shutdown**: Final registry save with statistics

**Example Statistics:**
```
=== Face Tracker Statistics ===
Unique faces detected: 12
Total detections: 456
Faces saved to: face_recognition/detected_faces
```

## Technical Details

### Duplicate Detection Algorithm

```python
1. Extract face encoding (128-dimensional vector)
2. Compare to all tracked encodings using Euclidean distance
3. Find minimum distance
4. If distance <= 0.6: Duplicate (don't save)
5. If distance > 0.6: New person (save)
```

### Threshold Selection

| Threshold | Behavior |
|-----------|----------|
| 0.4 | Very strict - may save same person multiple times |
| 0.6 | Balanced (default) - good for most use cases |
| 0.8 | Lenient - might miss some unique faces |

### Edge Cases Handled

- **Same person, different angles**: Saved as one person (usually)
- **Similar-looking people**: Saved separately if distance > threshold
- **Poor lighting/occlusion**: May save as new person (false negative)
- **Application restart**: Reloads previous detections, continues tracking

## Troubleshooting

### Same Person Saved Multiple Times

**Problem**: Multiple entries for same person  
**Solution**: Increase `DUPLICATE_THRESHOLD` to 0.7 or 0.8

### Missing Some Unique People

**Problem**: Different people not being saved  
**Solution**: Decrease `DUPLICATE_THRESHOLD` to 0.5 or 0.4

### Slow Performance

**Problem**: Frame rate drops with many tracked faces  
**Solution**: System is already optimized, but you can:
- Reduce `PROCESS_EVERY_N_FRAMES` processing
- Clear old detections periodically
- Use faster detection model

### Clear All Detected Faces

To start fresh:

```bash
# Backup if needed
cp -r detected_faces detected_faces_backup

# Clear detected faces and registry
rm detected_faces/*.jpg
rm data/face_registry.json

# Restart application
python main.py
```

## Integration with Your Workflow

The saved faces can be used for:

1. **Manual Identification**: Review images, identify people
2. **Database Population**: Build recognition database
3. **Analytics**: Track unique visitors over time
4. **External Systems**: Export for use in other applications
5. **Training Data**: Use for ML model training

## File Locations

- **Detected Faces**: `face_recognition/detected_faces/person_XXX.jpg`
- **Registry**: `face_recognition/data/face_registry.json`
- **Configuration**: `face_recognition/config.py`
- **Logs**: `face_recognition/logs/events_*.csv`

## Next Steps

After collecting detected faces:

1. Review and identify people
2. Organize into `known_faces/` directories
3. System will recognize them in future sessions
4. Use tracking IDs to link detections across sessions

---

**Note**: Face detection is automatic and runs whenever the application is active. All detected faces are saved with metadata for later identification.
