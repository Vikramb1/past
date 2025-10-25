"""
Face tracker for detecting and tracking unique individuals.
Prevents duplicate saves by comparing face encodings.
"""
import os
import json
import hashlib
import numpy as np
from datetime import datetime
from typing import Optional, Dict, Tuple, List
import face_recognition
import cv2
import config


class FaceTracker:
    """Tracks detected faces and prevents duplicate saves."""
    
    def __init__(
        self,
        detected_faces_dir: str = config.DETECTED_FACES_DIR,
        registry_file: str = config.FACE_REGISTRY_FILE,
        duplicate_threshold: float = config.DUPLICATE_THRESHOLD
    ):
        """
        Initialize the face tracker.
        
        Args:
            detected_faces_dir: Directory to save detected face images
            registry_file: Path to JSON registry file
            duplicate_threshold: Face distance threshold for duplicates
        """
        self.detected_faces_dir = detected_faces_dir
        self.registry_file = registry_file
        self.duplicate_threshold = duplicate_threshold
        
        # In-memory registry of tracked faces
        self.registry: Dict = {}
        
        # Lists for fast encoding comparison
        self.tracked_encodings: List = []
        self.tracked_ids: List[str] = []
        
        # Counter for new person IDs
        self.next_person_id = 1
        
        # Create directories
        os.makedirs(detected_faces_dir, exist_ok=True)
        os.makedirs(os.path.dirname(registry_file), exist_ok=True)
        
        # Load existing registry
        self._load_registry()
        
        print(f"Face Tracker initialized")
        print(f"Tracked faces: {len(self.registry)}")
        print(f"Duplicate threshold: {self.duplicate_threshold}")
    
    def _load_registry(self) -> None:
        """Load existing registry from JSON file."""
        if not os.path.exists(self.registry_file):
            print(f"No existing registry found, starting fresh")
            return
        
        try:
            with open(self.registry_file, 'r') as f:
                self.registry = json.load(f)
            
            # Rebuild in-memory encoding lists from saved data
            for person_id, data in self.registry.items():
                # Load the saved face image to get encoding
                image_path = os.path.join(
                    os.path.dirname(self.registry_file),
                    "..",
                    data['image_path']
                )
                
                if os.path.exists(image_path):
                    try:
                        image = face_recognition.load_image_file(image_path)
                        encodings = face_recognition.face_encodings(image)
                        
                        if len(encodings) > 0:
                            self.tracked_encodings.append(encodings[0])
                            self.tracked_ids.append(person_id)
                    except Exception as e:
                        print(f"Warning: Could not load encoding for {person_id}: {e}")
            
            # Update next_person_id counter
            if self.registry:
                max_id = max([int(pid.split('_')[1]) for pid in self.registry.keys()])
                self.next_person_id = max_id + 1
            
            print(f"Loaded {len(self.registry)} tracked faces from registry")
            print(f"Next person ID: {self.next_person_id}")
            
        except Exception as e:
            print(f"Error loading registry: {e}")
            self.registry = {}
    
    def _save_registry(self) -> None:
        """Save registry to JSON file."""
        try:
            with open(self.registry_file, 'w') as f:
                json.dump(self.registry, f, indent=2)
        except Exception as e:
            print(f"Error saving registry: {e}")
    
    def _generate_person_id(self) -> str:
        """
        Generate next person ID.
        
        Returns:
            Person ID like "person_001"
        """
        person_id = f"person_{self.next_person_id:03d}"
        self.next_person_id += 1
        return person_id
    
    def _encoding_to_hash(self, encoding: np.ndarray) -> str:
        """
        Convert face encoding to a hash string.
        
        Args:
            encoding: Face encoding array
        
        Returns:
            SHA256 hash of the encoding
        """
        # Convert encoding to bytes and hash
        encoding_bytes = encoding.tobytes()
        return hashlib.sha256(encoding_bytes).hexdigest()[:16]
    
    def _is_duplicate(self, encoding: np.ndarray) -> Tuple[bool, Optional[str]]:
        """
        Check if a face encoding matches an already tracked face.
        
        Args:
            encoding: Face encoding to check
        
        Returns:
            Tuple of (is_duplicate, person_id)
        """
        if len(self.tracked_encodings) == 0:
            return False, None
        
        # Calculate distances to all tracked encodings
        distances = face_recognition.face_distance(
            self.tracked_encodings,
            encoding
        )
        
        # Find closest match
        min_distance_idx = np.argmin(distances)
        min_distance = distances[min_distance_idx]
        
        # Check if below threshold (is a duplicate)
        if min_distance <= self.duplicate_threshold:
            person_id = self.tracked_ids[min_distance_idx]
            return True, person_id
        
        return False, None
    
    def track_face(
        self,
        face_image: np.ndarray,
        face_encoding: np.ndarray,
        face_location: Tuple[int, int, int, int]
    ) -> Tuple[str, bool]:
        """
        Track a detected face. Save if new, return ID if duplicate.
        
        Args:
            face_image: Full frame image (BGR format)
            face_encoding: Face encoding from face_recognition
            face_location: Face bounding box (top, right, bottom, left)
        
        Returns:
            Tuple of (person_id, is_new_face)
        """
        # Check if this face is already tracked
        is_duplicate, existing_id = self._is_duplicate(face_encoding)
        
        if is_duplicate:
            # Update detection count
            self.registry[existing_id]['detection_count'] += 1
            self.registry[existing_id]['last_seen'] = datetime.now().isoformat()
            
            # Save registry periodically (every 10 detections)
            if self.registry[existing_id]['detection_count'] % 10 == 0:
                self._save_registry()
            
            return existing_id, False
        
        # New face - save it
        person_id = self._generate_person_id()
        
        # Crop face from image
        top, right, bottom, left = face_location
        face_crop = self._crop_face_with_padding(face_image, top, right, bottom, left)
        
        # Save face image
        image_filename = f"{person_id}.jpg"
        image_path = os.path.join(self.detected_faces_dir, image_filename)
        cv2.imwrite(image_path, face_crop)
        
        # Add to in-memory tracking
        self.tracked_encodings.append(face_encoding)
        self.tracked_ids.append(person_id)
        
        # Add to registry
        now = datetime.now().isoformat()
        self.registry[person_id] = {
            'id': person_id,
            'first_seen': now,
            'last_seen': now,
            'image_path': f"detected_faces/{image_filename}",
            'encoding_hash': self._encoding_to_hash(face_encoding),
            'detection_count': 1,
            'person_info': None,  # Will be populated by API call
            'api_called': False  # Flag to track if API has been called
        }
        
        # Save registry
        self._save_registry()
        
        print(f"New face detected and saved: {person_id}")
        
        return person_id, True
    
    def _crop_face_with_padding(
        self,
        image: np.ndarray,
        top: int,
        right: int,
        bottom: int,
        left: int,
        padding: int = 20
    ) -> np.ndarray:
        """
        Crop face from image with padding.
        
        Args:
            image: Full image
            top, right, bottom, left: Face bounding box
            padding: Pixels to add around face
        
        Returns:
            Cropped face image
        """
        # Add padding
        height, width = image.shape[:2]
        top = max(0, top - padding)
        bottom = min(height, bottom + padding)
        left = max(0, left - padding)
        right = min(width, right + padding)
        
        return image[top:bottom, left:right]
    
    def get_person_info(self, person_id: str) -> Optional[Dict]:
        """
        Get information about a tracked person.
        
        Args:
            person_id: Person ID to look up
        
        Returns:
            Person data dictionary or None
        """
        return self.registry.get(person_id)
    
    def store_api_response(self, person_id: str, person_info_dict: Dict) -> None:
        """
        Store API response data for a person.
        
        Args:
            person_id: Person ID
            person_info_dict: PersonInfo dictionary from API
        """
        if person_id in self.registry:
            self.registry[person_id]['person_info'] = person_info_dict
            self.registry[person_id]['api_called'] = True
            self._save_registry()
    
    def has_api_data(self, person_id: str) -> bool:
        """
        Check if API data has been fetched for a person.
        
        Args:
            person_id: Person ID to check
        
        Returns:
            True if API has been called for this person
        """
        person_data = self.registry.get(person_id)
        return person_data is not None and person_data.get('api_called', False)
    
    def get_api_data(self, person_id: str) -> Optional[Dict]:
        """
        Get stored API response data for a person.
        
        Args:
            person_id: Person ID
        
        Returns:
            PersonInfo dictionary or None
        """
        person_data = self.registry.get(person_id)
        if person_data:
            return person_data.get('person_info')
        return None
    
    def get_statistics(self) -> Dict:
        """
        Get tracker statistics.
        
        Returns:
            Dictionary with stats
        """
        total_detections = sum(
            data['detection_count'] for data in self.registry.values()
        )
        
        return {
            'total_unique_faces': len(self.registry),
            'total_detections': total_detections,
            'tracked_encodings': len(self.tracked_encodings)
        }
    
    def reset(self) -> None:
        """Reset the tracker (clear all tracked faces)."""
        self.registry = {}
        self.tracked_encodings = []
        self.tracked_ids = []
        self.next_person_id = 1
        self._save_registry()
        print("Face tracker reset")

