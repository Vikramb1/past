# Quick Start Guide

## Installation (5 minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

If you encounter issues with `face_recognition` or `dlib`:

**macOS:**
```bash
brew install cmake
pip install dlib
pip install face_recognition
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install build-essential cmake
pip install dlib
pip install face_recognition
```

### 2. Test Your Camera

Make sure your camera works:
```bash
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera Error')"
```

## First Run (No Known Faces)

Start with an empty database to test detection:

```bash
python main.py
```

You should see:
- A window showing your camera feed
- Red boxes around detected faces (marked as "Unknown")
- FPS counter in the top-left
- Console output showing detections

**Controls:**
- Press **s** to save detected faces
- Press **q** to quit

## Adding Known Faces

### Method 1: From Photos

1. Create a directory for yourself:
```bash
mkdir -p known_faces/your_name
```

2. Add 3-5 clear face photos (JPG, PNG):
```bash
# Copy your photos
cp ~/path/to/your/photo1.jpg known_faces/your_name/
cp ~/path/to/your/photo2.jpg known_faces/your_name/
```

3. Run the application again:
```bash
python main.py
```

The system will automatically encode your faces on startup. When you appear in the camera, you should see:
- Green box (instead of red)
- Your name label
- Confidence score

### Method 2: Capture from Camera

1. Run the application:
```bash
python main.py
```

2. Position yourself in front of the camera

3. Press **s** to save your face
   - Faces are saved to `saved_faces/unknown_XXXX/`

4. Move saved faces to your directory:
```bash
mkdir -p known_faces/your_name
mv saved_faces/unknown_0001/*.jpg known_faces/your_name/
```

5. Press **r** to rebuild the database (or restart the app)

## Testing with Multiple People

1. Add photos for each person:
```bash
mkdir -p known_faces/alice
mkdir -p known_faces/bob
cp alice_photos/*.jpg known_faces/alice/
cp bob_photos/*.jpg known_faces/bob/
```

2. Run and test:
```bash
python main.py
```

## Using External Camera

List available cameras:
```bash
# Linux
ls /dev/video*

# macOS - try different indices
python main.py --source 0  # Usually built-in
python main.py --source 1  # Usually external
```

Use external camera:
```bash
python main.py --type external --source 1
```

## Performance Tuning

### For Slower Computers

Edit `config.py`:
```python
PROCESS_EVERY_N_FRAMES = 5  # Process every 5th frame
DETECTION_SCALE = 0.2       # Lower resolution detection
STREAM_WIDTH = 320          # Lower input resolution
STREAM_HEIGHT = 240
```

### For Better Accuracy

Edit `config.py`:
```python
DETECTION_MODEL = "cnn"           # More accurate (needs GPU)
RECOGNITION_TOLERANCE = 0.5       # Stricter matching
NUMBER_OF_TIMES_TO_UPSAMPLE = 2  # Better small face detection
```

## Checking Logs

View logged events:
```bash
# CSV format
cat logs/events_*.csv

# Or open in Excel/Sheets
open logs/events_*.csv
```

Log format:
- timestamp: When the event occurred
- event_type: "detection" or "recognition"
- name: Person name or "Unknown"
- confidence: Match confidence (0-1)
- recognized: True/False
- face_location: Bounding box coordinates

## Common Issues

### "No module named 'face_recognition'"
```bash
pip install face_recognition
```

### "Camera not found"
- Check camera index: try `--source 0`, `--source 1`, etc.
- Make sure no other app is using the camera
- Grant camera permissions (macOS: System Preferences > Security & Privacy)

### "Faces not recognized"
- Add more photos (3-5 per person)
- Use clear, well-lit photos
- Increase `RECOGNITION_TOLERANCE` in config.py (try 0.7)
- Press **r** to rebuild database

### "Too slow / Low FPS"
- Increase `PROCESS_EVERY_N_FRAMES` (try 5)
- Lower `DETECTION_SCALE` (try 0.2)
- Use `DETECTION_MODEL = "hog"` instead of "cnn"
- Reduce camera resolution in config.py

## Next Steps

1. **Build your database**: Add more people to `known_faces/`
2. **Customize settings**: Edit `config.py` for your needs
3. **Review logs**: Check `logs/` for detection/recognition history
4. **Network streaming**: Try streaming from external sources

For more details, see [README.md](README.md).

---

## Example Commands

```bash
# Basic usage (webcam)
python main.py

# External USB camera
python main.py --type external --source 1

# Custom display size
python main.py --width 1920 --height 1080

# Network stream (future Snap glasses)
python main.py --type network --source "rtsp://192.168.1.100:8554/stream"

# Help
python main.py --help
```

## Testing Without Installation

Want to test before installing? Try this minimal test:

```bash
pip install opencv-python
python -c "import cv2; cap = cv2.VideoCapture(0); ret, frame = cap.read(); print(f'Camera: {'OK' if ret else 'ERROR'}, Frame: {frame.shape if ret else 'None'}'); cap.release()"
```

This verifies OpenCV and camera access work before installing the full system.

