"""
Utility functions for image processing and helper operations.
"""
import cv2
import numpy as np
from typing import Tuple, Optional, List, Dict
import os
from datetime import datetime
import requests
from io import BytesIO

# Global cache for downloaded images
_image_cache: Dict[str, np.ndarray] = {}


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


def draw_saved_face_thumbnail(
    frame: np.ndarray,
    face_location: Tuple[int, int, int, int],
    saved_image_path: Optional[str] = None,
    thumbnail_size: int = 120,
    position: str = "top_left",
    padding: int = 10
) -> np.ndarray:
    """
    Draw the saved face image from detected_faces folder as a thumbnail.
    
    Args:
        frame: Image frame (BGR)
        face_location: Face bounding box (top, right, bottom, left)
        saved_image_path: Path to saved face image in detected_faces folder
        thumbnail_size: Size of the thumbnail (square)
        position: Position relative to face ("top_left", "top_right", "bottom_left", "bottom_right")
        padding: Padding from face box
    
    Returns:
        Frame with thumbnail drawn
    """
    # If no saved image path provided, return frame unchanged
    if not saved_image_path or not os.path.exists(saved_image_path):
        return frame
    
    top, right, bottom, left = face_location
    
    # Load the saved face image
    try:
        saved_face = cv2.imread(saved_image_path)
        if saved_face is None or saved_face.size == 0:
            return frame
    except Exception as e:
        print(f"Error loading saved face image: {e}")
        return frame
    
    # Resize to thumbnail size (maintaining aspect ratio)
    h, w = saved_face.shape[:2]
    if h > w:
        new_h = thumbnail_size
        new_w = int(w * (thumbnail_size / h))
    else:
        new_w = thumbnail_size
        new_h = int(h * (thumbnail_size / w))
    
    thumbnail = cv2.resize(saved_face, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # Create a square canvas
    canvas = np.zeros((thumbnail_size, thumbnail_size, 3), dtype=np.uint8)
    canvas.fill(40)  # Dark gray background
    
    # Center thumbnail on canvas
    y_offset = (thumbnail_size - new_h) // 2
    x_offset = (thumbnail_size - new_w) // 2
    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = thumbnail
    
    # Calculate position for thumbnail
    frame_h, frame_w = frame.shape[:2]
    
    if position == "top_left":
        thumb_x = left - thumbnail_size - padding
        thumb_y = top
    elif position == "top_right":
        thumb_x = right + padding
        thumb_y = top
    elif position == "bottom_left":
        thumb_x = left - thumbnail_size - padding
        thumb_y = bottom - thumbnail_size
    else:  # bottom_right
        thumb_x = right + padding
        thumb_y = bottom - thumbnail_size
    
    # Ensure thumbnail fits on frame
    if thumb_x < 0:
        thumb_x = right + padding  # Try right side
    if thumb_x + thumbnail_size > frame_w:
        thumb_x = left - thumbnail_size - padding  # Try left side
    if thumb_y < 0:
        thumb_y = 0
    if thumb_y + thumbnail_size > frame_h:
        thumb_y = frame_h - thumbnail_size
    
    # Ensure still in bounds
    thumb_x = max(0, min(thumb_x, frame_w - thumbnail_size))
    thumb_y = max(0, min(thumb_y, frame_h - thumbnail_size))
    
    # Draw border around thumbnail
    border_color = (100, 100, 100)  # Gray
    cv2.rectangle(
        frame,
        (thumb_x - 2, thumb_y - 2),
        (thumb_x + thumbnail_size + 2, thumb_y + thumbnail_size + 2),
        border_color,
        2
    )
    
    # Overlay thumbnail on frame
    frame[thumb_y:thumb_y+thumbnail_size, thumb_x:thumb_x+thumbnail_size] = canvas
    
    return frame


def draw_result_images_from_urls(
    frame: np.ndarray,
    face_location: Tuple[int, int, int, int],
    image_urls: List[str],
    thumbnail_size: int = 120,
    position: str = "top_left",
    padding: int = 10,
    spacing: int = 5
) -> np.ndarray:
    """
    Display up to 3 cached images from URLs next to the detected face.
    Images are displayed in a vertical column and cached after first download.
    
    Args:
        frame: Image frame (BGR)
        face_location: Face bounding box (top, right, bottom, left)
        image_urls: List of image URLs to display (max 3)
        thumbnail_size: Size of each thumbnail (square)
        position: Position relative to face ("top_left", "top_right", "bottom_left", "bottom_right")
        padding: Padding from face box
        spacing: Space between thumbnails (vertical)
    
    Returns:
        Frame with images drawn
    """
    global _image_cache
    
    if not image_urls or len(image_urls) == 0:
        return frame
    
    # Limit to 3 images
    image_urls = image_urls[:3]
    top, right, bottom, left = face_location
    frame_h, frame_w = frame.shape[:2]
    
    # Get or download images (with caching)
    thumbnails = []
    for url in image_urls:
        # Check cache first
        if url in _image_cache:
            thumbnails.append(_image_cache[url])
            continue
        
        # Not in cache - download and process
        try:
            # Download image
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                # Convert to numpy array
                image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                
                if img is not None and img.size > 0:
                    # Resize to thumbnail size (maintaining aspect ratio)
                    h, w = img.shape[:2]
                    if h > w:
                        new_h = thumbnail_size
                        new_w = int(w * (thumbnail_size / h))
                    else:
                        new_w = thumbnail_size
                        new_h = int(h * (thumbnail_size / w))
                    
                    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
                    
                    # Create square canvas
                    canvas = np.zeros((thumbnail_size, thumbnail_size, 3), dtype=np.uint8)
                    canvas.fill(40)  # Dark gray background
                    
                    # Center on canvas
                    y_offset = (thumbnail_size - new_h) // 2
                    x_offset = (thumbnail_size - new_w) // 2
                    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
                    
                    # Cache and add to thumbnails
                    _image_cache[url] = canvas
                    thumbnails.append(canvas)
                    print(f"📥 Downloaded and cached image from {url[:50]}...")
        except Exception as e:
            print(f"Error downloading image from {url}: {e}")
            continue
    
    if len(thumbnails) == 0:
        return frame
    
    # Calculate total height needed for vertical display
    total_height = len(thumbnails) * thumbnail_size + (len(thumbnails) - 1) * spacing
    
    # Calculate position for thumbnail column (vertical)
    if position == "top_left":
        thumb_x = left - thumbnail_size - padding
        thumb_y = top
    elif position == "top_right":
        thumb_x = right + padding
        thumb_y = top
    elif position == "bottom_left":
        thumb_x = left - thumbnail_size - padding
        thumb_y = bottom - total_height
    else:  # bottom_right
        thumb_x = right + padding
        thumb_y = bottom - total_height
    
    # Ensure thumbnails fit on frame
    if thumb_x < 0:
        thumb_x = right + padding  # Try right side
    if thumb_x + thumbnail_size > frame_w:
        thumb_x = left - thumbnail_size - padding  # Try left side
    if thumb_y < 0:
        thumb_y = 0
    if thumb_y + total_height > frame_h:
        thumb_y = frame_h - total_height
    
    # Ensure still in bounds
    thumb_x = max(0, min(thumb_x, frame_w - thumbnail_size))
    thumb_y = max(0, min(thumb_y, frame_h - total_height))
    
    # Draw each thumbnail vertically
    current_y = thumb_y
    for thumbnail in thumbnails:
        # Check if this thumbnail will fit
        if current_y + thumbnail_size > frame_h:
            break
        
        # Draw border
        border_color = (100, 200, 255)  # Light blue
        cv2.rectangle(
            frame,
            (thumb_x - 2, current_y - 2),
            (thumb_x + thumbnail_size + 2, current_y + thumbnail_size + 2),
            border_color,
            2
        )
        
        # Overlay thumbnail
        frame[current_y:current_y+thumbnail_size, thumb_x:thumb_x+thumbnail_size] = thumbnail
        
        # Move to next position (vertical)
        current_y += thumbnail_size + spacing
    
    return frame


def clear_image_cache():
    """Clear the global image cache to free memory."""
    global _image_cache
    cache_size = len(_image_cache)
    _image_cache.clear()
    print(f"🗑️  Cleared image cache ({cache_size} images)")


def get_image_cache_size() -> int:
    """Get the number of images in the cache."""
    global _image_cache
    return len(_image_cache)


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

