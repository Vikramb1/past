"""
Event logger for tracking face detections and recognitions.
"""
import os
import csv
import json
from datetime import datetime
from typing import Optional, Dict, List
import config


class EventLogger:
    """Logs face detection and recognition events."""
    
    def __init__(self, log_dir: str = config.LOGS_DIR, log_format: str = config.LOG_FORMAT):
        """
        Initialize the event logger.
        
        Args:
            log_dir: Directory to store log files
            log_format: Format for logs ("csv" or "json")
        """
        self.log_dir = log_dir
        self.log_format = log_format.lower()
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log files with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.log_format == "csv":
            self.log_file = os.path.join(log_dir, f"events_{timestamp}.csv")
            self._init_csv_log()
        else:  # json
            self.log_file = os.path.join(log_dir, f"events_{timestamp}.json")
            self.events = []
        
        # Track recent events to avoid duplicate logging
        self.recent_events: Dict[str, float] = {}
        self.log_interval = config.LOG_INTERVAL
        
        print(f"Event logger initialized: {self.log_file}")
    
    def _init_csv_log(self) -> None:
        """Initialize CSV log file with headers."""
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp',
                'event_type',
                'name',
                'confidence',
                'recognized',
                'face_location'
            ])
    
    def log_detection(
        self,
        name: str = "Unknown",
        confidence: Optional[float] = None,
        recognized: bool = False,
        face_location: Optional[tuple] = None
    ) -> None:
        """
        Log a face detection event.
        
        Args:
            name: Name of the person (or "Unknown")
            confidence: Recognition confidence (if applicable)
            recognized: Whether the face was recognized
            face_location: Face bounding box (top, right, bottom, left)
        """
        # Check if we should log this event (avoid spam)
        current_time = datetime.now().timestamp()
        event_key = f"{name}_{recognized}"
        
        if event_key in self.recent_events:
            if current_time - self.recent_events[event_key] < self.log_interval:
                return  # Skip this event, too soon
        
        self.recent_events[event_key] = current_time
        
        # Prepare event data
        timestamp = datetime.now().isoformat()
        event_type = "recognition" if recognized else "detection"
        confidence_str = f"{confidence:.4f}" if confidence is not None else ""
        location_str = str(face_location) if face_location is not None else ""
        
        # Log the event
        if self.log_format == "csv":
            self._log_csv_event(
                timestamp, event_type, name, confidence_str, recognized, location_str
            )
        else:  # json
            self._log_json_event(
                timestamp, event_type, name, confidence, recognized, face_location
            )
        
        # Print to console
        if recognized:
            conf_str = f" (confidence: {confidence:.2f})" if confidence else ""
            print(f"[{timestamp}] RECOGNIZED: {name}{conf_str}")
        else:
            print(f"[{timestamp}] DETECTED: {name}")
    
    def _log_csv_event(
        self,
        timestamp: str,
        event_type: str,
        name: str,
        confidence: str,
        recognized: bool,
        location: str
    ) -> None:
        """Write an event to CSV log."""
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                event_type,
                name,
                confidence,
                recognized,
                location
            ])
    
    def _log_json_event(
        self,
        timestamp: str,
        event_type: str,
        name: str,
        confidence: Optional[float],
        recognized: bool,
        location: Optional[tuple]
    ) -> None:
        """Write an event to JSON log."""
        event = {
            'timestamp': timestamp,
            'event_type': event_type,
            'name': name,
            'confidence': confidence,
            'recognized': recognized,
            'face_location': location
        }
        
        self.events.append(event)
        
        # Write to file
        with open(self.log_file, 'w') as f:
            json.dump(self.events, f, indent=2)
    
    def log_recognition(
        self,
        name: str,
        confidence: float,
        face_location: Optional[tuple] = None
    ) -> None:
        """
        Log a successful face recognition event.
        
        Args:
            name: Name of the recognized person
            confidence: Recognition confidence
            face_location: Face bounding box
        """
        self.log_detection(
            name=name,
            confidence=confidence,
            recognized=True,
            face_location=face_location
        )
    
    def log_unknown_face(self, face_location: Optional[tuple] = None) -> None:
        """
        Log an unknown face detection.
        
        Args:
            face_location: Face bounding box
        """
        self.log_detection(
            name="Unknown",
            confidence=None,
            recognized=False,
            face_location=face_location
        )
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get statistics about logged events.
        
        Returns:
            Dictionary with event counts
        """
        stats = {
            'total_detections': 0,
            'total_recognitions': 0,
            'unknown_faces': 0,
            'unique_people': set()
        }
        
        if self.log_format == "csv":
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        stats['total_detections'] += 1
                        if row['recognized'] == 'True':
                            stats['total_recognitions'] += 1
                            stats['unique_people'].add(row['name'])
                        else:
                            stats['unknown_faces'] += 1
        else:  # json
            for event in self.events:
                stats['total_detections'] += 1
                if event['recognized']:
                    stats['total_recognitions'] += 1
                    stats['unique_people'].add(event['name'])
                else:
                    stats['unknown_faces'] += 1
        
        stats['unique_people'] = len(stats['unique_people'])
        return stats
    
    def close(self) -> None:
        """Close the logger and print statistics."""
        stats = self.get_statistics()
        print("\n=== Event Logger Statistics ===")
        print(f"Total detections: {stats['total_detections']}")
        print(f"Total recognitions: {stats['total_recognitions']}")
        print(f"Unknown faces: {stats['unknown_faces']}")
        print(f"Unique people recognized: {stats['unique_people']}")
        print(f"Log file: {self.log_file}")

