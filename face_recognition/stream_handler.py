"""
Video stream handler for managing different video sources.
"""
import cv2
import numpy as np
from typing import Optional, Tuple
import config


class StreamHandler:
    """Manages video stream from various sources."""
    
    def __init__(
        self,
        stream_type: str = config.STREAM_TYPE_WEBCAM,
        source: Optional[int | str] = None
    ):
        """
        Initialize the stream handler.
        
        Args:
            stream_type: Type of stream (webcam, external, network)
            source: Camera index for webcam/external, URL for network stream
        """
        self.stream_type = stream_type
        self.source = source
        self.capture = None
        self.is_opened = False
        
        # Determine actual source
        if source is None:
            if stream_type == config.STREAM_TYPE_WEBCAM:
                self.source = config.DEFAULT_CAMERA_INDEX
            elif stream_type == config.STREAM_TYPE_EXTERNAL:
                self.source = config.EXTERNAL_CAMERA_INDEX
            else:
                raise ValueError(f"Source must be specified for stream type: {stream_type}")
        
        self._initialize_stream()
    
    def _initialize_stream(self) -> bool:
        """
        Initialize the video stream.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.capture = cv2.VideoCapture(self.source)
            
            # Configure camera settings for webcam and external cameras
            if isinstance(self.source, int):
                self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.STREAM_WIDTH)
                self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.STREAM_HEIGHT)
                self.capture.set(cv2.CAP_PROP_FPS, 30)
                # Reduce buffer size for lower latency
                self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            self.is_opened = self.capture.isOpened()
            
            if self.is_opened:
                print(f"Successfully opened {self.stream_type} stream from: {self.source}")
            else:
                print(f"Failed to open {self.stream_type} stream from: {self.source}")
            
            return self.is_opened
            
        except Exception as e:
            print(f"Error initializing stream: {e}")
            self.is_opened = False
            return False
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a frame from the video stream.
        
        Returns:
            Tuple of (success, frame)
        """
        if not self.is_opened or self.capture is None:
            return False, None
        
        ret, frame = self.capture.read()
        return ret, frame
    
    def release(self) -> None:
        """Release the video stream."""
        if self.capture is not None:
            self.capture.release()
            self.is_opened = False
            print(f"Released {self.stream_type} stream")
    
    def is_stream_opened(self) -> bool:
        """
        Check if the stream is opened.
        
        Returns:
            True if stream is opened, False otherwise
        """
        return self.is_opened
    
    def get_fps(self) -> float:
        """
        Get the FPS of the video stream.
        
        Returns:
            FPS value
        """
        if self.capture is not None and self.is_opened:
            return self.capture.get(cv2.CAP_PROP_FPS)
        return 0.0
    
    def get_frame_dimensions(self) -> Tuple[int, int]:
        """
        Get the dimensions of the video frames.
        
        Returns:
            Tuple of (width, height)
        """
        if self.capture is not None and self.is_opened:
            width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return width, height
        return 0, 0
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
    
    def __del__(self):
        """Destructor to ensure stream is released."""
        self.release()

