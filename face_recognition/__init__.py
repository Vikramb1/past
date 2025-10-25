"""
Real-Time Face Detection & Recognition System
A modular system for streaming live video and identifying faces in real-time.

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "Real-time face detection and recognition system"

# Main components
from . import config
from . import utils
from . import stream_handler
from . import face_database
from . import face_engine
from . import event_logger

__all__ = [
    'config',
    'utils',
    'stream_handler',
    'face_database',
    'face_engine',
    'event_logger',
]

