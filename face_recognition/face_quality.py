"""
Face quality detection module.
Measures face sharpness to ensure only clear images are saved.
"""
import cv2
import numpy as np
from typing import Tuple


class FaceQualityDetector:
    """Detects face image quality (sharpness/blur)."""
    
    # Quality thresholds for Laplacian variance
    STRICT_THRESHOLD = 150.0      # Very sharp only
    BALANCED_THRESHOLD = 100.0    # Good quality (recommended)
    LENIENT_THRESHOLD = 50.0      # Accept slightly soft
    
    def __init__(self, threshold: float = BALANCED_THRESHOLD):
        """
        Initialize quality detector.
        
        Args:
            threshold: Minimum sharpness score (higher = sharper required)
        """
        self.threshold = threshold
        print(f"Face Quality Detector initialized")
        print(f"Sharpness threshold: {self.threshold}")
    
    def calculate_sharpness(self, image: np.ndarray) -> float:
        """
        Calculate sharpness score using Laplacian variance.
        
        Higher values = sharper image
        Lower values = blurrier image
        
        Args:
            image: Face image (BGR or grayscale)
        
        Returns:
            Sharpness score (typically 0-500+)
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Calculate Laplacian variance
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        
        return variance
    
    def is_sharp(self, image: np.ndarray) -> Tuple[bool, float]:
        """
        Check if image is sharp enough.
        
        Args:
            image: Face image to check
        
        Returns:
            Tuple of (is_sharp, sharpness_score)
        """
        sharpness = self.calculate_sharpness(image)
        is_sharp = sharpness >= self.threshold
        
        return is_sharp, sharpness
    
    def get_quality_rating(self, sharpness: float) -> str:
        """
        Get human-readable quality rating.
        
        Args:
            sharpness: Sharpness score
        
        Returns:
            Quality rating string
        """
        if sharpness >= 200:
            return "Excellent"
        elif sharpness >= 150:
            return "Very Good"
        elif sharpness >= 100:
            return "Good"
        elif sharpness >= 50:
            return "Fair"
        else:
            return "Poor"
    
    def compare_faces(self, face1: np.ndarray, face2: np.ndarray) -> int:
        """
        Compare two face images and return the sharper one.
        
        Args:
            face1: First face image
            face2: Second face image
        
        Returns:
            Index of sharper image (0 for face1, 1 for face2)
        """
        sharpness1 = self.calculate_sharpness(face1)
        sharpness2 = self.calculate_sharpness(face2)
        
        return 0 if sharpness1 >= sharpness2 else 1
    
    def select_best_face(self, faces: list) -> Tuple[int, float]:
        """
        Select the sharpest face from a list of face images.
        
        Args:
            faces: List of face images
        
        Returns:
            Tuple of (best_index, sharpness_score)
        """
        if not faces:
            return -1, 0.0
        
        sharpness_scores = [self.calculate_sharpness(face) for face in faces]
        best_index = np.argmax(sharpness_scores)
        best_sharpness = sharpness_scores[best_index]
        
        return best_index, best_sharpness


class MultiFrameCollector:
    """Collects multiple frames of a face to select the best quality one."""
    
    def __init__(self, num_frames: int = 5, quality_detector: FaceQualityDetector = None):
        """
        Initialize frame collector.
        
        Args:
            num_frames: Number of frames to collect
            quality_detector: Quality detector instance
        """
        self.num_frames = num_frames
        self.quality_detector = quality_detector or FaceQualityDetector()
        
        # Storage for pending collections
        self.pending_collections = {}  # {person_hash: [frames, encodings, locations]}
        
        print(f"Multi-Frame Collector initialized")
        print(f"Frames to collect: {self.num_frames}")
    
    def start_collection(self, person_hash: str):
        """
        Start collecting frames for a person.
        
        Args:
            person_hash: Unique identifier for this face detection
        """
        self.pending_collections[person_hash] = {
            'frames': [],
            'encodings': [],
            'locations': [],
            'count': 0
        }
    
    def add_frame(
        self,
        person_hash: str,
        frame: np.ndarray,
        encoding: np.ndarray,
        location: Tuple[int, int, int, int]
    ) -> bool:
        """
        Add a frame to the collection.
        
        Args:
            person_hash: Unique identifier
            frame: Face image
            encoding: Face encoding
            location: Face location
        
        Returns:
            True if collection is complete
        """
        if person_hash not in self.pending_collections:
            return False
        
        collection = self.pending_collections[person_hash]
        collection['frames'].append(frame.copy())
        collection['encodings'].append(encoding.copy())
        collection['locations'].append(location)
        collection['count'] += 1
        
        return collection['count'] >= self.num_frames
    
    def get_best_frame(self, person_hash: str) -> Tuple[np.ndarray, np.ndarray, Tuple, float]:
        """
        Get the best quality frame from collection.
        
        Args:
            person_hash: Unique identifier
        
        Returns:
            Tuple of (best_frame, best_encoding, best_location, sharpness_score)
        """
        if person_hash not in self.pending_collections:
            return None, None, None, 0.0
        
        collection = self.pending_collections[person_hash]
        frames = collection['frames']
        
        if not frames:
            return None, None, None, 0.0
        
        # Find the sharpest frame
        best_index, sharpness = self.quality_detector.select_best_face(frames)
        
        best_frame = frames[best_index]
        best_encoding = collection['encodings'][best_index]
        best_location = collection['locations'][best_index]
        
        # Clean up
        del self.pending_collections[person_hash]
        
        return best_frame, best_encoding, best_location, sharpness
    
    def is_collecting(self, person_hash: str) -> bool:
        """Check if still collecting frames for a person."""
        return person_hash in self.pending_collections
    
    def get_collection_progress(self, person_hash: str) -> int:
        """Get number of frames collected so far."""
        if person_hash not in self.pending_collections:
            return 0
        return self.pending_collections[person_hash]['count']

