# Real-Time Face Detection & Recognition System

A Python-based real-time face detection and recognition system that streams from laptop camera or external sources, logs events, and is optimized for speed. Designed with future support for Snap AR glasses streaming.

## Features

- **Multi-source video streaming**: Webcam, external USB camera, or network streams (RTSP/HTTP)
- **Real-time face detection**: Fast face detection using optimized models
- **Face recognition**: Identify known individuals from a database
- **Automatic face tracking**: Auto-saves unique detected faces (one per person) for later identification
- **Duplicate prevention**: Uses face encoding comparison to avoid saving the same person multiple times
- **Person information display**: API integration showing contact info and employment history next to faces
- **Hand gesture recognition**: Real-time snap/click detection with MediaPipe (NEW!)
- **Event logging**: Comprehensive logging of detections and recognitions to CSV/JSON
- **Persistent tracking**: Remembers detected faces across application restarts
- **Performance optimized**: Frame skipping, downscaling, and caching for real-time performance
- **Extensible**: Ready for future integration with Snap AR Spectacles

## Installation

### Prerequisites

- Python 3.8 or higher
- Webcam or external camera
- (Optional) CUDA-capable GPU for faster processing

### Install Dependencies

```bash
cd face_recognition
pip install -r requirements.txt
```

**Note**: The `face_recognition` library requires `dlib`, which may need additional setup on some systems:

- **macOS**: `brew install cmake`
- **Linux**: `sudo apt-get install cmake build-essential`
- **Windows**: Install Visual Studio Build Tools

## Quick Start

### 1. Prepare Known Faces

Create subdirectories in `known_faces/` for each person you want to recognize:

```bash
cd face_recognition
mkdir -p known_faces/john_doe
mkdir -p known_faces/jane_smith
```

Add face images (JPG, PNG, etc.) to each person's directory:

```
known_faces/
├── john_doe/
│   ├── photo1.jpg
│   ├── photo2.jpg
│   └── photo3.jpg
└── jane_smith/
    ├── photo1.jpg
    └── photo2.jpg
```

**Tips for best results**:
- Use clear, well-lit photos
- Include 3-5 photos per person from different angles
- Ensure only one face per image
- Use high-quality images

### 2. Run the Application

**Default (laptop webcam)**:
```bash
python main.py
```

**External USB camera**:
```bash
python main.py --type external --source 1
```

**Network stream** (for future Snap AR glasses):
```bash
python main.py --type network --source "rtsp://your-stream-url"
```

### 3. Controls

While the application is running:

- **q** or **ESC** - Quit application
- **s** - Save currently detected faces manually to `saved_faces/`
- **r** - Rebuild face database from `known_faces/`
- **SPACE** - Pause/Resume video

### 4. Automatic Face Tracking (NEW!)

The system automatically saves detected faces to help you identify people later:

**How it works:**
- Every unique face is automatically saved to `detected_faces/`
- Assigned incremental IDs: `person_001.jpg`, `person_002.jpg`, etc.
- Duplicate detection prevents saving the same person multiple times
- Tracking persists across application restarts
- Metadata saved in `data/face_registry.json`

**Viewing detected faces:**
```bash
ls detected_faces/
# person_001.jpg, person_002.jpg, person_003.jpg, ...
```

**Using detected faces for identification:**
After the system runs, review `detected_faces/` to identify who people are. You can then:
1. Add their photos to `known_faces/person_name/` for future recognition
2. Use the saved images for your own identification workflow

**Configuration:**
Edit `config.py` to customize:
- `AUTO_SAVE_DETECTED_FACES = True` - Enable/disable auto-save
- `DUPLICATE_THRESHOLD = 0.6` - Adjust duplicate detection sensitivity (lower = stricter)

### 5. Person Information Display (NEW!)

The system can fetch and display detailed person information next to detected faces:

**How it works:**
- When a new face is detected, API is called with person's image
- Person details (name, email, phone, employment history) are fetched
- Information is displayed in a box next to the person's face
- API responses are cached (no repeated calls for same person)

**What's displayed:**
- Full name
- Email address
- Phone number
- Employment history (role, company, years)

**Current Implementation:**
- Uses dummy/mock API responses for testing
- Ready for real API integration (just swap the endpoint)
- Configurable display position and styling

**Configuration:**
Edit `config.py` to customize:
- `ENABLE_PERSON_INFO_API = True` - Enable/disable feature
- `INFO_DISPLAY_POSITION = "right"` - Position: "right", "left", "top", "bottom"
- `API_CALL_DELAY = 0.5` - Simulated API latency (seconds)
- Customize colors, fonts, and box styling

### 6. Gesture Recognition (NEW!)

The system can detect hand gestures like snaps and clicks in real-time:

**How it works:**
- Uses MediaPipe for hand tracking (detects up to 2 hands)
- Monitors finger positions (21 landmarks per hand)
- Detects snap/click gestures by tracking thumb-to-middle-finger distance
- Rapid finger closure triggers detection
- Displays bounding box around hand with "SNAP!" label

**Gesture Detection:**
- **Snap**: Rapid closure of thumb and middle finger
- Threshold-based (configurable distance and velocity)
- Cooldown period prevents repeated triggers
- Works with both left and right hands

**Visual Feedback:**
- Green box around hand when snap detected
- Blue box for detected hand (no gesture)
- "SNAP!" label appears when gesture triggered
- Optional: Show all 21 hand landmarks for debugging

**Configuration:**
Edit `config.py` to customize:
- `ENABLE_GESTURE_DETECTION = True` - Enable/disable feature
- `GESTURE_DETECTION_CONFIDENCE = 0.7` - Detection sensitivity
- `GESTURE_COOLDOWN_SECONDS = 1.0` - Time between repeated detections
- `SNAP_DISTANCE_THRESHOLD = 25` - Pixel distance for snap trigger
- `SHOW_HAND_LANDMARKS = False` - Show debug landmarks

## Configuration

Edit `config.py` to customize settings:

### Video Settings
- `DEFAULT_CAMERA_INDEX`: Webcam index (default: 0)
- `STREAM_WIDTH/HEIGHT`: Capture resolution
- `DISPLAY_WIDTH/HEIGHT`: Display window size

### Detection Settings
- `DETECTION_MODEL`: "hog" (fast, CPU) or "cnn" (accurate, GPU)
- `DETECTION_SCALE`: Scale factor for detection (0.25 = 1/4 size, faster)
- `PROCESS_EVERY_N_FRAMES`: Process every Nth frame (higher = faster)

### Recognition Settings
- `RECOGNITION_TOLERANCE`: Match threshold (lower = stricter, default: 0.6)
- `MIN_CONFIDENCE`: Minimum confidence for recognition

### Logging Settings
- `LOG_DETECTIONS`: Enable detection logging
- `LOG_RECOGNITIONS`: Enable recognition logging
- `LOG_FORMAT`: "csv" or "json"
- `LOG_INTERVAL`: Minimum seconds between logging same face

## Project Structure

```
face_recognition/
├── __init__.py               # Package initialization
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── config.py                 # Configuration settings
├── main.py                   # Main application entry point
├── stream_handler.py         # Video stream management
├── face_engine.py            # Face detection & recognition
├── face_database.py          # Known faces database
├── face_tracker.py           # Face tracking & auto-save
├── person_info.py            # Person info API client
├── info_display.py           # Info box renderer
├── gesture_detector.py       # Hand gesture recognition (NEW!)
├── event_logger.py           # Event logging system
├── utils.py                  # Helper functions
├── add_person.py             # Add person utility
├── test_setup.py             # Setup verification
├── known_faces/              # Known face images (organized by person)
├── saved_faces/              # Manually saved faces
├── detected_faces/           # Auto-saved detected faces
├── logs/                     # Event logs (CSV/JSON)
└── data/                     # Cached data
    ├── encodings.pkl         # Face encodings cache
    └── face_registry.json    # Detected faces registry
```

## Performance Optimization

The system uses several techniques for real-time performance:

1. **Frame skipping**: Process recognition every Nth frame while detecting on all frames
2. **Downscaling**: Detect faces on scaled-down frames (1/4 size by default)
3. **Caching**: Face encodings are cached for fast startup
4. **Batch processing**: Multiple faces processed efficiently
5. **Model selection**: HOG model for CPU, CNN option for GPU

### Tips for Better Performance

- Use `DETECTION_MODEL = "hog"` for CPU-only systems (faster)
- Increase `PROCESS_EVERY_N_FRAMES` to 3-5 for slower systems
- Reduce `STREAM_WIDTH/HEIGHT` for lower resolution input
- Lower `DETECTION_SCALE` to 0.2 for even faster detection
- Enable `ENABLE_GPU = True` if you have CUDA-capable GPU

## Event Logging

All face detections and recognitions are logged with:

- Timestamp (ISO format)
- Event type (detection/recognition)
- Person name (or "Unknown")
- Confidence score (for recognitions)
- Face location coordinates
- Recognition status (recognized: True/False)

Logs are saved in `logs/` directory as:
- `events_TIMESTAMP.csv` (CSV format)
- `events_TIMESTAMP.json` (JSON format)

## Building Your Face Database

### Method 1: From Existing Photos

1. Create person directories in `known_faces/`
2. Add face photos to each directory
3. Run the application (encodings are generated automatically)

### Method 2: Capture from Video

1. Run the application
2. When a person appears, press **s** to save their face
3. Faces are saved to `saved_faces/`
4. Move saved faces to appropriate person directory in `known_faces/`
5. Press **r** to rebuild the database

### Method 3: Add Programmatically

```python
from face_database import FaceDatabase

db = FaceDatabase()
db.add_face("path/to/photo.jpg", "person_name", save_to_database=True)
```

## Future: Snap AR Glasses Integration

The system is designed to support streaming from Snap AR Spectacles when available:

1. Configure Spectacles to stream video via RTSP/HTTP
2. Run application with network stream:
   ```bash
   python main.py --type network --source "rtsp://spectacles-ip:port/stream"
   ```

The face recognition engine processes any video stream identically, making integration seamless.

## Troubleshooting

### Camera Not Found
- Check camera index with `ls /dev/video*` (Linux) or System Preferences (macOS)
- Try different indices: `--source 0`, `--source 1`, etc.

### Slow Performance
- Increase `PROCESS_EVERY_N_FRAMES` in `config.py`
- Use `DETECTION_MODEL = "hog"` instead of "cnn"
- Reduce `DETECTION_SCALE` to 0.2 or lower
- Lower input resolution in `config.py`

### No Faces Recognized
- Check that images are in `known_faces/person_name/` directories
- Ensure good quality photos (clear, well-lit)
- Increase `RECOGNITION_TOLERANCE` (try 0.7)
- Rebuild database with **r** key

### Installation Issues (dlib/face_recognition)
- **macOS**: `brew install cmake && pip install dlib`
- **Ubuntu**: `sudo apt-get install build-essential cmake && pip install dlib`
- **Windows**: Install Visual Studio Build Tools first

## Additional Documentation

- `QUICKSTART.md` - Quick start guide
- `IMPLEMENTATION_SUMMARY.md` - Technical implementation details
- `PROJECT_INFO.md` - Project statistics and information
- `CHANGELOG.md` - Version history

## License

TBD

## Acknowledgments

Built with:
- [OpenCV](https://opencv.org/) - Video capture and display
- [face_recognition](https://github.com/ageitgey/face_recognition) - Face detection and recognition
- [dlib](http://dlib.net/) - Machine learning backend
- [MediaPipe](https://mediapipe.dev/) - Alternative face detection

---

**Note**: This system is designed for educational and personal use. Ensure you have proper consent before using face recognition on individuals.

