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

### FastAPI Application

A simple FastAPI application with CRUD operations for managing items.

**Location**: Root directory

**Features**:
- **RESTful API** with full CRUD operations
- **Automatic API documentation** with Swagger UI
- **Data validation** using Pydantic models
- **CORS support** for frontend integration
- **Search functionality** with filtering options
- **Health check endpoint**

**Quick Start**:
```bash
pip install -r requirements.txt
python main.py
```

**API Endpoints**:
- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /items` - Get all items
- `POST /items` - Create new item
- `PUT /items/{item_id}` - Update item
- `DELETE /items/{item_id}` - Delete item
- `GET /items/search/` - Search items with filters

Access the API at http://localhost:8000 and interactive docs at http://localhost:8000/docs

## Project Structure

```
past/
├── README.md                 # This file
├── main.py                   # FastAPI application
├── requirements.txt          # Python dependencies
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
