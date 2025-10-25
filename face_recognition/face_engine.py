"""
Face detection and recognition engine.
"""
import face_recognition
import numpy as np
from typing import List, Tuple, Optional
import time
import config
from face_database import FaceDatabase
from face_tracker import FaceTracker


class FaceEngine:
    """Main face detection and recognition engine."""
    
    def __init__(self, face_database: FaceDatabase, face_tracker: Optional[FaceTracker] = None):
        """
        Initialize the face engine.
        
        Args:
            face_database: FaceDatabase instance with known faces
            face_tracker: Optional FaceTracker instance for auto-saving detected faces
        """
        self.face_database = face_database
        self.face_tracker = face_tracker
        self.detection_model = config.DETECTION_MODEL
        self.recognition_tolerance = config.RECOGNITION_TOLERANCE
        self.process_every_n_frames = config.PROCESS_EVERY_N_FRAMES
        
        # Frame counter for processing optimization
        self.frame_count = 0
        
        # Cache for last detected faces (for frames we skip processing)
        self.last_face_locations = []
        self.last_face_names = []
        self.last_face_confidences = []
        self.last_face_encodings = []
        self.last_tracked_ids = []
        
        print(f"Face engine initialized")
        print(f"Detection model: {self.detection_model}")
        print(f"Recognition tolerance: {self.recognition_tolerance}")
        print(f"Processing every {self.process_every_n_frames} frame(s)")
        print(f"Known faces loaded: {self.face_database.get_face_count()}")
        if self.face_tracker:
            print(f"Face tracking: ENABLED")
    
    def detect_and_recognize_faces(
        self,
        frame: np.ndarray,
        bgr_frame: Optional[np.ndarray] = None,
        scale: float = config.DETECTION_SCALE
    ) -> Tuple[List[Tuple], List[str], List[float], List[str]]:
        """
        Detect and recognize faces in a frame.
        
        Args:
            frame: RGB image frame
            bgr_frame: Optional BGR frame for face tracking (required if tracking enabled)
            scale: Scale factor for detection (smaller = faster)
        
        Returns:
            Tuple of (face_locations, face_names, confidences, tracked_ids)
        """
        self.frame_count += 1
        
        # Only process recognition every Nth frame for performance
        if self.frame_count % self.process_every_n_frames != 0:
            # Return cached results
            return (
                self.last_face_locations,
                self.last_face_names,
                self.last_face_confidences,
                self.last_tracked_ids
            )
        
        # Scale down frame for faster detection
        if scale != 1.0:
            small_frame = self._scale_frame(frame, scale)
        else:
            small_frame = frame
        
        # Detect faces
        face_locations = face_recognition.face_locations(
            small_frame,
            number_of_times_to_upsample=config.NUMBER_OF_TIMES_TO_UPSAMPLE,
            model=self.detection_model
        )
        
        # If no faces detected, return empty results
        if len(face_locations) == 0:
            self.last_face_locations = []
            self.last_face_names = []
            self.last_face_confidences = []
            self.last_tracked_ids = []
            return [], [], [], []
        
        # Limit number of faces to process
        if len(face_locations) > config.MAX_FACES_TO_PROCESS:
            face_locations = face_locations[:config.MAX_FACES_TO_PROCESS]
        
        # Scale face locations back to original frame size
        if scale != 1.0:
            face_locations = self._scale_face_locations(face_locations, 1.0 / scale)
        
        # Get face encodings
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        
        # Recognize faces
        face_names = []
        face_confidences = []
        tracked_ids = []
        
        known_encodings, known_names = self.face_database.get_known_faces()
        
        if len(known_encodings) == 0:
            # No known faces in database
            face_names = ["Unknown"] * len(face_encodings)
            face_confidences = [0.0] * len(face_encodings)
        else:
            for face_encoding in face_encodings:
                name, confidence = self._recognize_face(
                    face_encoding,
                    known_encodings,
                    known_names
                )
                face_names.append(name)
                face_confidences.append(confidence)
        
        # Track faces if tracker is enabled
        if self.face_tracker and config.AUTO_SAVE_DETECTED_FACES and bgr_frame is not None:
            for i, (face_location, face_encoding) in enumerate(zip(face_locations, face_encodings)):
                person_id, is_new = self.face_tracker.track_face(
                    bgr_frame,
                    face_encoding,
                    face_location
                )
                tracked_ids.append(person_id)
        else:
            tracked_ids = [""] * len(face_encodings)
        
        # Cache results
        self.last_face_locations = face_locations
        self.last_face_names = face_names
        self.last_face_confidences = face_confidences
        self.last_face_encodings = face_encodings
        self.last_tracked_ids = tracked_ids
        
        return face_locations, face_names, face_confidences, tracked_ids
    
    def _recognize_face(
        self,
        face_encoding: np.ndarray,
        known_encodings: List[np.ndarray],
        known_names: List[str]
    ) -> Tuple[str, float]:
        """
        Recognize a face against known faces.
        
        Args:
            face_encoding: Encoding of the face to recognize
            known_encodings: List of known face encodings
            known_names: List of corresponding names
        
        Returns:
            Tuple of (name, confidence)
        """
        # Calculate face distances
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        
        # Find the best match
        best_match_index = np.argmin(face_distances)
        best_distance = face_distances[best_match_index]
        
        # Convert distance to confidence (0 = perfect match, 1 = no match)
        # Confidence = 1 - distance
        confidence = 1.0 - best_distance
        
        # Check if match is good enough
        if best_distance <= self.recognition_tolerance:
            name = known_names[best_match_index]
            return name, confidence
        else:
            return "Unknown", confidence
    
    def detect_faces_only(
        self,
        frame: np.ndarray,
        scale: float = config.DETECTION_SCALE
    ) -> List[Tuple]:
        """
        Detect faces without recognition (faster).
        
        Args:
            frame: RGB image frame
            scale: Scale factor for detection
        
        Returns:
            List of face locations
        """
        # Scale down frame
        if scale != 1.0:
            small_frame = self._scale_frame(frame, scale)
        else:
            small_frame = frame
        
        # Detect faces
        face_locations = face_recognition.face_locations(
            small_frame,
            number_of_times_to_upsample=config.NUMBER_OF_TIMES_TO_UPSAMPLE,
            model=self.detection_model
        )
        
        # Scale back up
        if scale != 1.0:
            face_locations = self._scale_face_locations(face_locations, 1.0 / scale)
        
        return face_locations
    
    def _scale_frame(self, frame: np.ndarray, scale: float) -> np.ndarray:
        """Scale a frame by a given factor."""
        if scale == 1.0:
            return frame
        
        width = int(frame.shape[1] * scale)
        height = int(frame.shape[0] * scale)
        
        import cv2
        return cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)
    
    def _scale_face_locations(
        self,
        face_locations: List[Tuple],
        scale: float
    ) -> List[Tuple]:
        """
        Scale face locations by a given factor.
        
        Args:
            face_locations: List of (top, right, bottom, left) tuples
            scale: Scaling factor
        
        Returns:
            Scaled face locations
        """
        scaled_locations = []
        for (top, right, bottom, left) in face_locations:
            scaled_locations.append((
                int(top * scale),
                int(right * scale),
                int(bottom * scale),
                int(left * scale)
            ))
        return scaled_locations
    
    def reset_frame_cache(self) -> None:
        """Reset the frame processing cache."""
        self.frame_count = 0
        self.last_face_locations = []
        self.last_face_names = []
        self.last_face_confidences = []

