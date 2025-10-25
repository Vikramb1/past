# Real-Time Face Detection & Recognition System

A Python-based real-time face detection and recognition system that streams from laptop camera or external sources, logs events, and is optimized for speed. Designed with future support for Snap AR glasses streaming.

## Features

- **Multi-source video streaming**: Webcam, external USB camera, or network streams (RTSP/HTTP)
- **Real-time face detection**: Fast face detection using optimized models
- **Face recognition**: Identify known individuals from a database
- **Event logging**: Comprehensive logging of detections and recognitions to CSV/JSON
- **Auto-save faces**: Save detected faces for building your face database
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
- **s** - Save currently detected faces to `saved_faces/`
- **r** - Rebuild face database from `known_faces/`
- **SPACE** - Pause/Resume video

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
├── event_logger.py           # Event logging system
├── utils.py                  # Helper functions
├── add_person.py             # Add person utility
├── test_setup.py             # Setup verification
├── known_faces/              # Known face images (organized by person)
├── saved_faces/              # Auto-saved detected faces
├── logs/                     # Event logs (CSV/JSON)
└── data/                     # Cached encodings
    └── encodings.pkl
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

