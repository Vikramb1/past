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
NUMBER_OF_TIMES_TO_UPSAMPLE = 1  # Higher = more accurate but slower (better for small/distant faces)

# Face recognition settings
RECOGNITION_TOLERANCE = 0.6  # Lower = more strict, higher = more lenient (default: 0.6)
MIN_CONFIDENCE = 0.5  # Minimum confidence for recognition

# Face encoding quality settings (for robust recognition)
ENCODING_NUM_JITTERS = 3  # Number of times to resample face for robust encoding (default: 1)
ENCODING_MODEL = 'large'   # 'small' or 'large' - large is more accurate for encodings

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
DUPLICATE_THRESHOLD = 0.45  # Face distance threshold for duplicate detection (lower = stricter)

# Face quality settings (prevent blurry faces)
ENABLE_QUALITY_CHECK = True  # Only save sharp, non-blurry faces
QUALITY_FRAMES_TO_COLLECT = 5  # Number of frames to collect before selecting best
QUALITY_SHARPNESS_THRESHOLD = 100.0  # Minimum sharpness score (100 = balanced)

# Person information API settings
ENABLE_PERSON_INFO_API = True  # Fetch and display person information
API_CALL_DELAY = 0.5  # Simulated API delay in seconds (for dummy API)
INFO_DISPLAY_POSITION = "right"  # Position relative to face: "right", "left", "top", "bottom"

# Person info polling settings (for Supabase integration)
PERSON_INFO_POLL_INTERVAL = 1.0  # Poll every 1 second for scraping data
PERSON_INFO_MAX_POLL_TIME = 300  # Stop polling after 5 minutes

# Info box display settings
INFO_BOX_BG_COLOR = (40, 40, 40)  # Dark gray background (BGR)
INFO_BOX_BORDER_COLOR = (100, 200, 255)  # Light blue border (BGR)
INFO_BOX_BORDER_THICKNESS = 1
INFO_BOX_ALPHA = 0.85  # Background transparency (0.0-1.0, higher = more opaque)
INFO_BOX_PADDING_LEFT = 6
INFO_BOX_PADDING_RIGHT = 6
INFO_BOX_PADDING_TOP = 6
INFO_BOX_PADDING_BOTTOM = 6
INFO_BOX_MARGIN = 5  # Space between face box and info box
INFO_BOX_MAX_WIDTH = 350  # Maximum width of info box in pixels

# Info text settings
INFO_TEXT_COLOR = (255, 255, 255)  # White text (BGR)
INFO_FONT_SCALE_TITLE = 0.5  # Font size for name
INFO_FONT_SCALE_NORMAL = 0.35  # Font size for description
INFO_FONT_SCALE_SMALL = 0.28  # Font size for social links
INFO_LINE_SPACING = 2  # Pixels between lines

# Gesture detection settings
ENABLE_GESTURE_DETECTION = True  # Enable hand gesture recognition
GESTURE_DETECTION_CONFIDENCE = 0.7  # MediaPipe confidence threshold (0.0-1.0)
GESTURE_COOLDOWN_SECONDS = 1.0  # Prevent repeated triggers (seconds)
SNAP_DISTANCE_THRESHOLD = 25  # Finger distance threshold for snap (pixels)
SNAP_VELOCITY_THRESHOLD = 0.3  # Time window for snap detection (seconds)

# Gesture visual settings
GESTURE_BOX_COLOR = (0, 255, 0)  # Green for detected gesture (BGR)
GESTURE_BOX_THICKNESS = 3  # Box line thickness
SHOW_HAND_LANDMARKS = False  # Show all 21 hand landmarks (debug mode)
GESTURE_LABEL_TEXT = "SNAP!"  # Text to display when gesture detected

# Crypto payment settings
ENABLE_CRYPTO_PAYMENT = True  # Enable crypto payments on snap gesture
CRYPTO_SERVER_PATH = "../crypto-stuff"  # Path to crypto server directory
PAYMENT_HOLD_DURATION = 2.0  # Seconds to hold snap before payment triggers
PAYMENT_COOLDOWN = 30.0  # Seconds between payments (prevents accidental double-sends)
PAYMENT_AMOUNT_MIST = 100000  # 0.0001 SUI (1 SUI = 1,000,000,000 MIST)

# Wallet configuration (from send-from-funded.ts)
FUNDED_WALLET_PRIVATE_KEY = "suiprivkey1qrdkvfpf9ksrsh8pwayg6n8vgk5n89087fy05u9uavvwsd6egv5ezxt843t"
RECIPIENT_WALLET_ADDRESS = "0xbf8ba70997c705101fa3bbd478a6c87e884a34196408a08c40d90f0b5ae59511"

# XRPL settings
XRPL_FUNDED_WALLET_PRIVATE_KEY = "2fa8efe237294d598f4c2699f69a0a9228c5263805a408dffabbea6dcf6e4105"
XRPL_FUNDED_WALLET_PUBLIC_KEY = "0x60d6252fC31177B48732ab89f073407788F09C61"

# Gift crypto settings (generates new wallets for recipients)
RECIPIENT_EMAIL = "sanjay.amirthraj@gmail.com"  # Email to send crypto gift credentials
SENDER_NAME = "Face Recognition Payment System"  # Name shown in gift email

# Payment visual feedback settings
PAYMENT_OVERLAY_POSITION = "top_center"  # Position on screen
PAYMENT_TEXT_COLOR = (0, 255, 255)  # Yellow text (BGR)
PAYMENT_SUCCESS_COLOR = (0, 255, 0)  # Green for success (BGR)
PAYMENT_FAILURE_COLOR = (0, 0, 255)  # Red for failure (BGR)
PAYMENT_OVERLAY_ALPHA = 0.8  # Background transparency
PAYMENT_TEXT_SIZE = 1.0  # Font scale
PAYMENT_DISPLAY_DURATION = 5.0  # Seconds to show success/failure message

# Speech transcription settings
ENABLE_SPEECH_TRANSCRIPTION = True
DEEPGRAM_API_KEY = "b6dd69dddfa27a355aa91f7b1c7688c7c8805f72"
TRANSCRIPTION_BUFFER_SECONDS = 10
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1

# Amount parsing settings  
OLLAMA_MODEL = "llama3.2"
DEFAULT_PAYMENT_AMOUNT_SUI = 0.0001
DEFAULT_PAYMENT_AMOUNT_XRPL = 0.0001
AMOUNT_DISPLAY_DURATION = 2.0

# Transcription display settings
TRANSCRIPTION_TEXT_COLOR = (200, 200, 200)  # Light gray (BGR)
TRANSCRIPTION_FONT_SCALE = 0.4
TRANSCRIPTION_POSITION = "bottom_center"
AMOUNT_DISPLAY_POSITION = "top_right"
AMOUNT_TEXT_COLOR = (0, 255, 255)  # Yellow (BGR)
AMOUNT_FONT_SCALE = 0.7

# Supabase storage settings
SUPABASE_URL = "https://afwpcbmhvjwrnolhrocz.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFmd3BjYm1odmp3cm5vbGhyb2N6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTM2NzYwOCwiZXhwIjoyMDc2OTQzNjA4fQ.32C1dNH0-aQFhpODSlw9UzAj721kjP_BIZfuS-2VMGE"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFmd3BjYm1odmp3cm5vbGhyb2N6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzNjc2MDgsImV4cCI6MjA3Njk0MzYwOH0.Sjg-8h3tEOn0eoGR3GK-DPz_5dCwS07MZFpkC-qL_Bs"
SUPABASE_BUCKET_NAME = "detected-faces"
ENABLE_SUPABASE_UPLOAD = True  # Enable automatic upload to Supabase

# Stream types
STREAM_TYPE_WEBCAM = "webcam"
STREAM_TYPE_EXTERNAL = "external"
STREAM_TYPE_NETWORK = "network"

