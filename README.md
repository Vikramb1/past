# Past Project

This is a larger project containing multiple components.

## Components

### Face Recognition System

Real-time face detection and recognition system for streaming live video and identifying faces.

**Location**: `face_recognition/`

**Features**:
- Multi-source video streaming (webcam, USB camera, network streams)
- Real-time face detection and recognition
- Event logging and face database management
- Optimized for speed and ready for Snap AR glasses integration

**Quick Start**:
```bash
cd face_recognition
pip install -r requirements.txt
python main.py
```

See `face_recognition/README.md` for detailed documentation or `USAGE.md` for quick commands.

## Project Structure

```
past/
├── README.md                 # This file
└── face_recognition/         # Face recognition system
    ├── README.md             # Face recognition documentation
    ├── requirements.txt      # Python dependencies
    ├── main.py               # Main application
    ├── config.py             # Configuration
    ├── known_faces/          # Known face images
    ├── logs/                 # Event logs
    └── ...                   # Other components
```

## License

TBD
