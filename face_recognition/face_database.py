"""
Face database for managing known faces and their encodings.
"""
import os
import pickle
from typing import List, Dict, Tuple, Optional
import face_recognition
import cv2
import config


class FaceDatabase:
    """Manages known faces and their encodings."""
    
    def __init__(
        self,
        known_faces_dir: str = config.KNOWN_FACES_DIR,
        encodings_file: str = config.ENCODINGS_FILE
    ):
        """
        Initialize the face database.
        
        Args:
            known_faces_dir: Directory containing known face images
            encodings_file: Path to cached encodings file
        """
        self.known_faces_dir = known_faces_dir
        self.encodings_file = encodings_file
        
        # Lists to store known face encodings and names
        self.known_face_encodings: List = []
        self.known_face_names: List[str] = []
        
        # Create directories if they don't exist
        os.makedirs(known_faces_dir, exist_ok=True)
        os.makedirs(os.path.dirname(encodings_file), exist_ok=True)
        
        # Load or create encodings
        self._load_or_create_encodings()
    
    def _load_or_create_encodings(self) -> None:
        """Load encodings from cache or create new ones from images."""
        # Try to load cached encodings
        if os.path.exists(self.encodings_file):
            print(f"Loading cached face encodings from {self.encodings_file}...")
            try:
                with open(self.encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data['encodings']
                    self.known_face_names = data['names']
                print(f"Loaded {len(self.known_face_names)} known faces from cache")
                return
            except Exception as e:
                print(f"Error loading cached encodings: {e}")
                print("Creating new encodings from images...")
        
        # Create new encodings from images
        self._create_encodings_from_images()
    
    def _create_encodings_from_images(self) -> None:
        """Create face encodings from images in the known_faces directory."""
        print(f"Scanning {self.known_faces_dir} for face images...")
        
        face_count = 0
        
        # Check if directory exists and has subdirectories
        if not os.path.exists(self.known_faces_dir):
            print(f"Known faces directory not found: {self.known_faces_dir}")
            print("Create subdirectories with person names and add face images.")
            return
        
        # Iterate through person directories
        for person_name in os.listdir(self.known_faces_dir):
            person_dir = os.path.join(self.known_faces_dir, person_name)
            
            # Skip if not a directory
            if not os.path.isdir(person_dir):
                continue
            
            print(f"Processing faces for: {person_name}")
            
            # Iterate through images for this person
            for filename in os.listdir(person_dir):
                # Check if file is an image
                if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    continue
                
                image_path = os.path.join(person_dir, filename)
                
                try:
                    # Load image
                    image = face_recognition.load_image_file(image_path)
                    
                    # Get face encodings
                    encodings = face_recognition.face_encodings(
                        image,
                        model='small'  # Use 'small' for faster processing
                    )
                    
                    if len(encodings) > 0:
                        # Use the first face found
                        self.known_face_encodings.append(encodings[0])
                        self.known_face_names.append(person_name)
                        face_count += 1
                        print(f"  ✓ Encoded: {filename}")
                    else:
                        print(f"  ✗ No face found in: {filename}")
                
                except Exception as e:
                    print(f"  ✗ Error processing {filename}: {e}")
        
        print(f"\nTotal faces encoded: {face_count}")
        
        # Save encodings to cache
        if face_count > 0:
            self._save_encodings()
    
    def _save_encodings(self) -> None:
        """Save face encodings to cache file."""
        try:
            data = {
                'encodings': self.known_face_encodings,
                'names': self.known_face_names
            }
            with open(self.encodings_file, 'wb') as f:
                pickle.dump(data, f)
            print(f"Saved encodings to {self.encodings_file}")
        except Exception as e:
            print(f"Error saving encodings: {e}")
    
    def add_face(
        self,
        image_path: str,
        person_name: str,
        save_to_database: bool = True
    ) -> bool:
        """
        Add a new face to the database.
        
        Args:
            image_path: Path to the face image
            person_name: Name of the person
            save_to_database: Whether to save to the known_faces directory
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load and encode the image
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image, model='small')
            
            if len(encodings) == 0:
                print(f"No face found in image: {image_path}")
                return False
            
            # Add to database
            self.known_face_encodings.append(encodings[0])
            self.known_face_names.append(person_name)
            
            # Save to known_faces directory if requested
            if save_to_database:
                person_dir = os.path.join(self.known_faces_dir, person_name)
                os.makedirs(person_dir, exist_ok=True)
                
                # Copy image to person directory
                filename = os.path.basename(image_path)
                dest_path = os.path.join(person_dir, filename)
                
                # Read and write image
                img = cv2.imread(image_path)
                cv2.imwrite(dest_path, img)
            
            # Update cache
            self._save_encodings()
            
            print(f"Added face for {person_name} to database")
            return True
            
        except Exception as e:
            print(f"Error adding face: {e}")
            return False
    
    def get_known_faces(self) -> Tuple[List, List[str]]:
        """
        Get all known face encodings and names.
        
        Returns:
            Tuple of (encodings, names)
        """
        return self.known_face_encodings, self.known_face_names
    
    def get_face_count(self) -> int:
        """
        Get the number of known faces.
        
        Returns:
            Number of known faces
        """
        return len(self.known_face_names)
    
    def get_people_list(self) -> List[str]:
        """
        Get a list of unique people in the database.
        
        Returns:
            List of unique person names
        """
        return list(set(self.known_face_names))
    
    def rebuild_encodings(self) -> None:
        """Rebuild all encodings from scratch."""
        print("Rebuilding face encodings...")
        self.known_face_encodings = []
        self.known_face_names = []
        self._create_encodings_from_images()
    
    def clear_cache(self) -> None:
        """Clear the cached encodings file."""
        if os.path.exists(self.encodings_file):
            os.remove(self.encodings_file)
            print(f"Cleared encodings cache: {self.encodings_file}")

