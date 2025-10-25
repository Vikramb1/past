#!/usr/bin/env python3
"""
Real-time Face Detection and Recognition System
Main application entry point.
"""
import cv2
import argparse
import time
from typing import Optional
import sys

import config
import utils
from stream_handler import StreamHandler
from face_database import FaceDatabase
from face_engine import FaceEngine
from event_logger import EventLogger


class FaceRecognitionApp:
    """Main application class for face recognition system."""
    
    def __init__(
        self,
        stream_type: str = config.STREAM_TYPE_WEBCAM,
        source: Optional[int | str] = None,
        display_width: int = config.DISPLAY_WIDTH,
        display_height: int = config.DISPLAY_HEIGHT
    ):
        """
        Initialize the face recognition application.
        
        Args:
            stream_type: Type of video stream
            source: Video source (camera index or URL)
            display_width: Display window width
            display_height: Display window height
        """
        print("=" * 60)
        print("Real-Time Face Detection & Recognition System")
        print("=" * 60)
        
        # Ensure directories exist
        utils.ensure_directories_exist(
            config.KNOWN_FACES_DIR,
            config.SAVED_FACES_DIR,
            config.LOGS_DIR,
            config.DATA_DIR
        )
        
        # Initialize components
        print("\nInitializing components...")
        self.stream_handler = StreamHandler(stream_type, source)
        self.face_database = FaceDatabase()
        self.face_engine = FaceEngine(self.face_database)
        self.event_logger = EventLogger()
        
        # Display settings
        self.display_width = display_width
        self.display_height = display_height
        
        # Performance tracking
        self.fps = 0.0
        self.frame_times = []
        self.max_frame_times = 30
        
        # Counters for saved faces
        self.unknown_face_counter = 0
        
        print("\nInitialization complete!")
        self._print_instructions()
    
    def _print_instructions(self) -> None:
        """Print usage instructions."""
        print("\n" + "=" * 60)
        print("CONTROLS:")
        print("  q or ESC  - Quit application")
        print("  s         - Save detected faces")
        print("  r         - Rebuild face database")
        print("  SPACE     - Pause/Resume")
        print("=" * 60)
    
    def run(self) -> None:
        """Run the main application loop."""
        if not self.stream_handler.is_stream_opened():
            print("Error: Could not open video stream")
            return
        
        print("\nStarting face recognition...")
        print("Press 'q' to quit\n")
        
        paused = False
        last_frame = None
        
        try:
            while True:
                # Handle pause
                if paused:
                    key = cv2.waitKey(100) & 0xFF
                    if key == ord(' '):
                        paused = False
                        print("Resumed")
                    elif key == ord('q') or key == 27:  # ESC
                        break
                    
                    if last_frame is not None:
                        cv2.imshow('Face Recognition', last_frame)
                    continue
                
                # Start frame timer
                frame_start = time.time()
                
                # Read frame from stream
                ret, frame = self.stream_handler.read_frame()
                
                if not ret or frame is None:
                    print("Error: Could not read frame from stream")
                    break
                
                # Convert BGR to RGB for face_recognition library
                rgb_frame = utils.convert_bgr_to_rgb(frame)
                
                # Detect and recognize faces
                face_locations, face_names, face_confidences = \
                    self.face_engine.detect_and_recognize_faces(rgb_frame)
                
                # Log events
                if config.LOG_DETECTIONS or config.LOG_RECOGNITIONS:
                    for location, name, confidence in zip(
                        face_locations, face_names, face_confidences
                    ):
                        if name == "Unknown":
                            if config.LOG_DETECTIONS:
                                self.event_logger.log_unknown_face(location)
                        else:
                            if config.LOG_RECOGNITIONS:
                                self.event_logger.log_recognition(
                                    name, confidence, location
                                )
                
                # Draw results on frame
                display_frame = self._draw_results(
                    frame,
                    face_locations,
                    face_names,
                    face_confidences
                )
                
                # Draw FPS if enabled
                if config.SHOW_FPS:
                    display_frame = utils.draw_fps(display_frame, self.fps)
                
                # Resize for display
                if (display_frame.shape[1] != self.display_width or
                    display_frame.shape[0] != self.display_height):
                    display_frame = utils.resize_frame(
                        display_frame,
                        self.display_width,
                        self.display_height
                    )
                
                # Display the frame
                cv2.imshow('Face Recognition', display_frame)
                last_frame = display_frame
                
                # Calculate FPS
                frame_time = time.time() - frame_start
                self.frame_times.append(frame_time)
                if len(self.frame_times) > self.max_frame_times:
                    self.frame_times.pop(0)
                self.fps = 1.0 / (sum(self.frame_times) / len(self.frame_times))
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q') or key == 27:  # ESC
                    break
                elif key == ord('s'):
                    self._save_faces(frame, face_locations, face_names)
                elif key == ord('r'):
                    self._rebuild_database()
                elif key == ord(' '):
                    paused = True
                    print("Paused (press SPACE to resume)")
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        
        finally:
            self._cleanup()
    
    def _draw_results(
        self,
        frame,
        face_locations,
        face_names,
        face_confidences
    ):
        """Draw face detection and recognition results on frame."""
        for (top, right, bottom, left), name, confidence in zip(
            face_locations, face_names, face_confidences
        ):
            # Choose color based on recognition status
            if name == "Unknown":
                color = config.BOX_COLOR_UNKNOWN
            else:
                color = config.BOX_COLOR_KNOWN
            
            # Draw face box and label
            frame = utils.draw_face_box(
                frame,
                top, right, bottom, left,
                name,
                confidence if config.SHOW_CONFIDENCE else None,
                color,
                config.BOX_THICKNESS,
                config.FONT_SCALE,
                config.SHOW_CONFIDENCE
            )
        
        return frame
    
    def _save_faces(self, frame, face_locations, face_names):
        """Save detected faces to disk."""
        if len(face_locations) == 0:
            print("No faces to save")
            return
        
        saved_count = 0
        
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Crop face
            face_img = utils.crop_face(frame, top, right, bottom, left)
            
            # Determine name for saving
            if name == "Unknown":
                self.unknown_face_counter += 1
                save_name = f"unknown_{self.unknown_face_counter:04d}"
            else:
                save_name = name
            
            # Save face
            filepath = utils.save_face_image(
                face_img,
                save_name,
                config.SAVED_FACES_DIR,
                config.SAVE_FACE_SIZE
            )
            
            saved_count += 1
            print(f"Saved face: {filepath}")
        
        print(f"Saved {saved_count} face(s) to {config.SAVED_FACES_DIR}")
    
    def _rebuild_database(self):
        """Rebuild the face database from images."""
        print("\nRebuilding face database...")
        self.face_database.rebuild_encodings()
        self.face_engine.reset_frame_cache()
        print("Database rebuilt successfully")
    
    def _cleanup(self):
        """Clean up resources."""
        print("\nCleaning up...")
        self.stream_handler.release()
        self.event_logger.close()
        cv2.destroyAllWindows()
        print("Application closed")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Real-time Face Detection and Recognition System'
    )
    
    parser.add_argument(
        '--source',
        type=str,
        default=None,
        help='Video source: camera index (0, 1, ...) or URL for network stream'
    )
    
    parser.add_argument(
        '--type',
        type=str,
        choices=[
            config.STREAM_TYPE_WEBCAM,
            config.STREAM_TYPE_EXTERNAL,
            config.STREAM_TYPE_NETWORK
        ],
        default=config.STREAM_TYPE_WEBCAM,
        help='Type of video source'
    )
    
    parser.add_argument(
        '--width',
        type=int,
        default=config.DISPLAY_WIDTH,
        help='Display window width'
    )
    
    parser.add_argument(
        '--height',
        type=int,
        default=config.DISPLAY_HEIGHT,
        help='Display window height'
    )
    
    args = parser.parse_args()
    
    # Parse source argument
    source = args.source
    if source is not None and source.isdigit():
        source = int(source)
    
    # Create and run application
    app = FaceRecognitionApp(
        stream_type=args.type,
        source=source,
        display_width=args.width,
        display_height=args.height
    )
    
    app.run()


if __name__ == '__main__':
    main()

