"""
Utility functions for image processing and helper operations.
"""
import cv2
import numpy as np
from typing import Tuple, Optional
import os
from datetime import datetime


def resize_frame(frame: np.ndarray, width: int, height: int) -> np.ndarray:
    """
    Resize a frame to the specified dimensions.
    
    Args:
        frame: Input frame
        width: Target width
        height: Target height
    
    Returns:
        Resized frame
    """
    return cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)


def scale_frame(frame: np.ndarray, scale: float) -> np.ndarray:
    """
    Scale a frame by a given factor.
    
    Args:
        frame: Input frame
        scale: Scaling factor (e.g., 0.25 for 1/4 size)
    
    Returns:
        Scaled frame
    """
    if scale == 1.0:
        return frame
    
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    return cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)


def draw_face_box(
    frame: np.ndarray,
    top: int,
    right: int,
    bottom: int,
    left: int,
    name: str,
    confidence: Optional[float] = None,
    color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2,
    font_scale: float = 0.6,
    show_confidence: bool = True
) -> np.ndarray:
    """
    Draw a bounding box and label on a face.
    
    Args:
        frame: Image frame
        top, right, bottom, left: Face bounding box coordinates
        name: Name to display
        confidence: Recognition confidence (optional)
        color: Box color (BGR)
        thickness: Box line thickness
        font_scale: Text size
        show_confidence: Whether to show confidence value
    
    Returns:
        Frame with drawn annotations
    """
    # Draw rectangle around face
    cv2.rectangle(frame, (left, top), (right, bottom), color, thickness)
    
    # Prepare label text
    label = name
    if confidence is not None and show_confidence:
        label = f"{name} ({confidence:.2f})"
    
    # Draw label background
    label_height = 25
    cv2.rectangle(
        frame,
        (left, bottom - label_height),
        (right, bottom),
        color,
        cv2.FILLED
    )
    
    # Draw label text
    cv2.putText(
        frame,
        label,
        (left + 6, bottom - 6),
        cv2.FONT_HERSHEY_DUPLEX,
        font_scale,
        (255, 255, 255),
        1
    )
    
    return frame


def draw_fps(frame: np.ndarray, fps: float) -> np.ndarray:
    """
    Draw FPS counter on the frame.
    
    Args:
        frame: Image frame
        fps: Current FPS value
    
    Returns:
        Frame with FPS counter
    """
    text = f"FPS: {fps:.1f}"
    cv2.putText(
        frame,
        text,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )
    return frame


def crop_face(frame: np.ndarray, top: int, right: int, bottom: int, left: int) -> np.ndarray:
    """
    Crop a face from a frame with some padding.
    
    Args:
        frame: Image frame
        top, right, bottom, left: Face bounding box coordinates
    
    Returns:
        Cropped face image
    """
    # Add some padding
    padding = 20
    top = max(0, top - padding)
    bottom = min(frame.shape[0], bottom + padding)
    left = max(0, left - padding)
    right = min(frame.shape[1], right + padding)
    
    return frame[top:bottom, left:right]


def save_face_image(
    face_img: np.ndarray,
    person_name: str,
    output_dir: str,
    size: Optional[Tuple[int, int]] = None
) -> str:
    """
    Save a face image to disk.
    
    Args:
        face_img: Face image to save
        person_name: Name of the person
        output_dir: Directory to save the image
        size: Optional resize dimensions
    
    Returns:
        Path to saved image
    """
    # Create directory if it doesn't exist
    person_dir = os.path.join(output_dir, person_name)
    os.makedirs(person_dir, exist_ok=True)
    
    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{person_name}_{timestamp}.jpg"
    filepath = os.path.join(person_dir, filename)
    
    # Resize if needed
    if size is not None:
        face_img = cv2.resize(face_img, size, interpolation=cv2.INTER_AREA)
    
    # Save image
    cv2.imwrite(filepath, face_img)
    return filepath


def ensure_directories_exist(*directories: str) -> None:
    """
    Ensure that the specified directories exist, creating them if necessary.
    
    Args:
        *directories: Variable number of directory paths
    """
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def convert_rgb_to_bgr(image: np.ndarray) -> np.ndarray:
    """
    Convert RGB image to BGR (OpenCV format).
    
    Args:
        image: RGB image
    
    Returns:
        BGR image
    """
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


def convert_bgr_to_rgb(image: np.ndarray) -> np.ndarray:
    """
    Convert BGR image to RGB (face_recognition format).
    
    Args:
        image: BGR image
    
    Returns:
        RGB image
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def preprocess_face_image(image: np.ndarray) -> np.ndarray:
    """
    Normalize lighting and improve contrast for better face detection.
    
    Args:
        image: Input image in BGR format
    
    Returns:
        Preprocessed image with normalized lighting
    """
    # Convert to LAB color space for better lighting normalization
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)
    
    # Merge channels back
    enhanced_lab = cv2.merge([l_enhanced, a, b])
    
    # Convert back to BGR
    enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    
    return enhanced


def enhance_frame_for_detection(frame: np.ndarray) -> np.ndarray:
    """
    Apply preprocessing optimized for face detection.
    Less aggressive than full preprocessing to maintain real-time performance.
    
    Args:
        frame: Input frame in BGR or RGB format
    
    Returns:
        Enhanced frame with improved contrast and lighting
    """
    # Light histogram equalization
    # Works with both BGR and RGB
    if len(frame.shape) == 3:
        # Color image - work in YCrCb space
        ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        y, cr, cb = cv2.split(ycrcb)
        
        # Apply light CLAHE to luminance channel
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
        y_enhanced = clahe.apply(y)
        
        # Merge back
        ycrcb_enhanced = cv2.merge([y_enhanced, cr, cb])
        enhanced = cv2.cvtColor(ycrcb_enhanced, cv2.COLOR_YCrCb2BGR)
        
        return enhanced
    else:
        # Grayscale
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
        return clahe.apply(frame)

