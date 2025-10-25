"""
Configuration settings for the face recognition system.
"""
import os

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWN_FACES_DIR = os.path.join(BASE_DIR, "known_faces")
SAVED_FACES_DIR = os.path.join(BASE_DIR, "saved_faces")
DETECTED_FACES_DIR = os.path.join(BASE_DIR, "detected_faces")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")
ENCODINGS_FILE = os.path.join(DATA_DIR, "encodings.pkl")
FACE_REGISTRY_FILE = os.path.join(DATA_DIR, "face_registry.json")

# Video source settings
DEFAULT_CAMERA_INDEX = 0  # Laptop camera
EXTERNAL_CAMERA_INDEX = 1  # External USB camera
STREAM_WIDTH = 640
STREAM_HEIGHT = 480
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720

# Face detection settings
DETECTION_MODEL = "hog"  # Options: "hog" (fast, CPU) or "cnn" (accurate, GPU)
DETECTION_SCALE = 0.25  # Scale down frames for faster detection (0.25 = 1/4 size)
PROCESS_EVERY_N_FRAMES = 2  # Process every Nth frame for recognition
NUMBER_OF_TIMES_TO_UPSAMPLE = 1  # Higher = more accurate but slower

# Face recognition settings
RECOGNITION_TOLERANCE = 0.6  # Lower = more strict, higher = more lenient (default: 0.6)
MIN_CONFIDENCE = 0.5  # Minimum confidence for recognition

# Performance settings
MAX_FACES_TO_PROCESS = 10  # Maximum number of faces to process per frame
ENABLE_GPU = False  # Set to True if you have a CUDA-capable GPU

# Display settings
SHOW_FPS = True
SHOW_CONFIDENCE = True
BOX_COLOR_KNOWN = (0, 255, 0)  # Green for known faces
BOX_COLOR_UNKNOWN = (0, 0, 255)  # Red for unknown faces
TEXT_COLOR = (255, 255, 255)  # White
BOX_THICKNESS = 2
FONT_SCALE = 0.6
FONT_THICKNESS = 1

# Logging settings
LOG_DETECTIONS = True
LOG_RECOGNITIONS = True
LOG_FORMAT = "csv"  # Options: "csv" or "json"
LOG_INTERVAL = 1.0  # Minimum seconds between logging the same face

# Face saving settings
SAVE_UNKNOWN_FACES = True
SAVE_FACE_SIZE = (200, 200)  # Size to save face crops

# Face tracking settings (auto-save detected faces)
AUTO_SAVE_DETECTED_FACES = True  # Automatically save all detected faces
DUPLICATE_THRESHOLD = 0.6  # Face distance threshold for duplicate detection (lower = stricter)

# Stream types
STREAM_TYPE_WEBCAM = "webcam"
STREAM_TYPE_EXTERNAL = "external"
STREAM_TYPE_NETWORK = "network"

