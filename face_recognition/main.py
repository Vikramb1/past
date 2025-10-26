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
import threading

import config
import utils
from stream_handler import StreamHandler
from face_database import FaceDatabase
from face_engine import FaceEngine
from event_logger import EventLogger
from face_tracker import FaceTracker
from person_info import get_api_instance, PersonInfo
from info_display import draw_person_info_box
from gesture_detector import GestureDetector
from speech_transcription import SpeechTranscriber
from amount_parser import AmountParser


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
            config.DETECTED_FACES_DIR,
            config.LOGS_DIR,
            config.DATA_DIR
        )
        
        # Initialize components
        print("\nInitializing components...")
        self.stream_handler = StreamHandler(stream_type, source)
        self.face_database = FaceDatabase()
        
        # Initialize face tracker if auto-save is enabled
        if config.AUTO_SAVE_DETECTED_FACES:
            self.face_tracker = FaceTracker()
        else:
            self.face_tracker = None
        
        self.face_engine = FaceEngine(self.face_database, self.face_tracker)
        self.event_logger = EventLogger()
        
        # Initialize person info API if enabled
        if config.ENABLE_PERSON_INFO_API:
            self.person_api = get_api_instance()
        else:
            self.person_api = None
        
        # Initialize gesture detector if enabled
        if config.ENABLE_GESTURE_DETECTION:
            self.gesture_detector = GestureDetector()
        else:
            self.gesture_detector = None
        
        # Initialize crypto payment handler if enabled
        if config.ENABLE_CRYPTO_PAYMENT:
            from crypto_payment import CryptoPaymentHandler
            self.crypto_handler = CryptoPaymentHandler()
            self.crypto_handler.start_server()
            self.payment_status = None  # Track current payment state
        else:
            self.crypto_handler = None
            self.payment_status = None
        
        # Initialize speech transcription if enabled
        if config.ENABLE_SPEECH_TRANSCRIPTION:
            self.speech_transcriber = SpeechTranscriber()
            self.speech_transcriber.start()
            self.amount_parser = AmountParser()
            self.amount_preview = None  # Track amount preview state
        else:
            self.speech_transcriber = None
            self.amount_parser = None
            self.amount_preview = None
        
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
        print("  s         - Save detected faces manually")
        print("  r         - Rebuild face database")
        print("  SPACE     - Pause/Resume")
        if config.AUTO_SAVE_DETECTED_FACES:
            print("\nAUTO-SAVE: Enabled - Detected faces saved automatically")
        if config.ENABLE_PERSON_INFO_API:
            print("PERSON INFO API: Enabled - Fetching person details")
        if config.ENABLE_GESTURE_DETECTION:
            print("GESTURE DETECTION: Enabled - Detecting snaps/clicks")
        if config.ENABLE_CRYPTO_PAYMENT:
            print("CRYPTO PAYMENT: Enabled - Hold snap for 2s to send SUI")
        if config.ENABLE_SPEECH_TRANSCRIPTION:
            print("SPEECH TRANSCRIPTION: Enabled - Say amount before snap")
            print("  Example: 'send 0.5 SUI' then hold snap gesture")
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
                
                # Detect and recognize faces (pass BGR frame for tracking)
                face_locations, face_names, face_confidences, tracked_ids = \
                    self.face_engine.detect_and_recognize_faces(rgb_frame, frame)
                
                # Fetch person info for newly detected faces
                if self.person_api and self.face_tracker:
                    for tracked_id in tracked_ids:
                        if tracked_id and not self.face_tracker.has_api_data(tracked_id):
                            # Call API for new person
                            person_info = self.person_api.get_person_info(tracked_id)
                            if person_info:
                                # Store API response in tracker
                                self.face_tracker.store_api_response(
                                    tracked_id,
                                    person_info.to_dict()
                                )
                
                # Detect gestures if enabled
                gesture_events = []
                if self.gesture_detector:
                    gesture_events, frame = self.gesture_detector.detect_gestures(frame)
                    
                    # Check for payment trigger
                    if config.ENABLE_CRYPTO_PAYMENT and self.crypto_handler:
                        for event in gesture_events:
                            if event.gesture_type == "snap":
                                hand_id = f"{event.hand_label}_0"
                                
                                # Show amount preview during hold
                                if event.hold_duration >= 1.5 and event.hold_duration < config.PAYMENT_HOLD_DURATION:
                                    if not self.amount_preview:
                                        # Parse amount from recent transcription
                                        if self.speech_transcriber and self.amount_parser:
                                            recent_text = self.speech_transcriber.get_recent_transcription()
                                            parsed_amount, currency, display_text = self.amount_parser.parse_amount(recent_text)
                                            is_valid, validated_amount, message, validated_currency, validated_display = self.amount_parser.validate_amount(parsed_amount, currency, display_text)
                                            
                                            if is_valid:
                                                self.amount_preview = {
                                                    'amount': validated_amount,
                                                    'currency': validated_currency,
                                                    'display_text': validated_display,
                                                    'message': message,
                                                    'timestamp': time.time(),
                                                    'state': 'preview'
                                                }
                                                print(f"💰 {message}")
                                            else:
                                                print(f"⚠️  {message}")
                                        else:
                                            # No transcription, use default SUI
                                            self.amount_preview = {
                                                'amount': config.DEFAULT_PAYMENT_AMOUNT_SUI,
                                                'currency': 'SUI',
                                                'display_text': 'SUI',
                                                'message': f'Using default: {config.DEFAULT_PAYMENT_AMOUNT_SUI} SUI',
                                                'timestamp': time.time(),
                                                'state': 'preview'
                                            }
                                
                                # Check if held for required duration and not already triggered
                                if (event.hold_duration >= config.PAYMENT_HOLD_DURATION and
                                    hand_id in self.gesture_detector.gesture_states and
                                    not self.gesture_detector.gesture_states[hand_id]['payment_triggered'] and
                                    self.crypto_handler.can_send_payment()):
                                    
                                    # Mark as triggered to prevent repeat
                                    self.gesture_detector.gesture_states[hand_id]['payment_triggered'] = True
                                    
                                    # Extract amount and currency from preview
                                    if self.amount_preview and 'amount' in self.amount_preview:
                                        amount = self.amount_preview['amount']
                                        currency = self.amount_preview.get('currency', 'SUI')
                                        display_text = self.amount_preview.get('display_text', 'SUI')
                                    else:
                                        amount = config.DEFAULT_PAYMENT_AMOUNT_SUI
                                        currency = 'SUI'
                                        display_text = 'SUI'
                                    
                                    # Send payment in background thread
                                    print(f"\n💰 Payment triggered by {event.hold_duration:.1f}s snap hold!")
                                    print(f"💸 Sending {amount} {display_text}")
                                    threading.Thread(target=self._send_payment_async, args=(amount, currency, display_text), daemon=True).start()
                                    
                                    # Clear amount preview
                                    self.amount_preview = None
                
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
                    face_confidences,
                    tracked_ids
                )
                
                # Draw FPS if enabled
                if config.SHOW_FPS:
                    display_frame = utils.draw_fps(display_frame, self.fps)
                
                # Draw transcription overlay if enabled
                if config.ENABLE_SPEECH_TRANSCRIPTION and self.speech_transcriber:
                    display_frame = self._draw_transcription_overlay(display_frame)
                
                # Draw amount preview if active
                if self.amount_preview:
                    display_frame = self._draw_amount_preview(display_frame)
                
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
        face_confidences,
        tracked_ids
    ):
        """Draw face detection and recognition results on frame."""
        for i, ((top, right, bottom, left), name, confidence, tracked_id) in enumerate(zip(
            face_locations, face_names, face_confidences, tracked_ids
        )):
            # Choose color based on recognition status
            if name == "Unknown":
                color = config.BOX_COLOR_UNKNOWN
            else:
                color = config.BOX_COLOR_KNOWN
            
            # Use tracked ID if available, otherwise use recognition name
            display_name = name
            if tracked_id:
                # Show tracked ID for all faces
                display_name = tracked_id if name == "Unknown" else f"{name} ({tracked_id})"
            
            # Draw face box and label
            frame = utils.draw_face_box(
                frame,
                top, right, bottom, left,
                display_name,
                confidence if config.SHOW_CONFIDENCE and name != "Unknown" else None,
                color,
                config.BOX_THICKNESS,
                config.FONT_SCALE,
                config.SHOW_CONFIDENCE
            )
            
            # Draw person info box if API is enabled and data is available
            if config.ENABLE_PERSON_INFO_API and self.face_tracker and tracked_id:
                api_data = self.face_tracker.get_api_data(tracked_id)
                if api_data:
                    try:
                        person_info = PersonInfo.from_dict(api_data)
                        frame = draw_person_info_box(
                            frame,
                            person_info,
                            (top, right, bottom, left),
                            config.INFO_DISPLAY_POSITION
                        )
                    except Exception as e:
                        # Silently handle display errors
                        pass
        
        # Draw payment status overlay if enabled
        if config.ENABLE_CRYPTO_PAYMENT and self.payment_status:
            frame = self._draw_payment_overlay(frame)
        
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
    
    def _send_payment_async(self, amount: float = None, currency: str = 'SUI', display_text: str = 'SUI'):
        """Send crypto payment asynchronously (runs in background thread).
        
        Args:
            amount: Amount to send in the specified currency
            currency: Currency type ('SUI' or 'XRPL')
            display_text: Display text for the currency (e.g., 'XRP', 'XRPL', 'SUI')
        """
        try:
            # Use default if amount not provided
            if amount is None:
                if currency == 'XRPL':
                    amount = config.DEFAULT_PAYMENT_AMOUNT_XRPL
                else:
                    amount = config.DEFAULT_PAYMENT_AMOUNT_SUI
            
            # Set sending status
            self.payment_status = {
                "state": "sending",
                "message": f"Sending {amount} {display_text}...",
                "timestamp": time.time()
            }
            
            # Send the payment
            result = self.crypto_handler.send_payment(amount, currency, display_text)
            
            if result['success']:
                # Payment successful
                recipient_addr = result.get('recipientAddress', 'N/A')
                amount_display = result.get('amountDisplay', f"{amount} {display_text}")
                self.payment_status = {
                    "state": "success",
                    "message": f"Sent {amount_display}!",
                    "digest": result.get('transactionDigest', 'N/A'),
                    "explorerUrl": result.get('explorerUrl', ''),
                    "recipientAddress": recipient_addr,
                    "currency": currency,
                    "timestamp": time.time()
                }
                print(f"\n✅ {currency} crypto gift successful!")
                print(f"   Transaction: {result.get('transactionDigest', 'N/A')}")
                print(f"   New wallet: {recipient_addr[:20]}..." if len(recipient_addr) > 20 else recipient_addr)
            else:
                # Payment failed
                error_msg = result.get('message', 'Unknown error')
                self.payment_status = {
                    "state": "failure",
                    "message": f"Payment failed: {error_msg}",
                    "timestamp": time.time()
                }
                print(f"\n❌ Payment failed: {error_msg}")
        
        except Exception as e:
            print(f"\n❌ Payment error: {e}")
            self.payment_status = {
                "state": "failure",
                "message": f"Error: {str(e)}",
                "timestamp": time.time()
            }
    
    def _draw_payment_overlay(self, frame):
        """Draw payment status overlay at top center of frame."""
        state = self.payment_status['state']
        message = self.payment_status['message']
        
        # Auto-clear success/failure after configured duration
        if state in ['success', 'failure']:
            if time.time() - self.payment_status['timestamp'] > config.PAYMENT_DISPLAY_DURATION:
                self.payment_status = None
                return frame
        
        # Choose color based on state
        color_map = {
            'sending': config.PAYMENT_TEXT_COLOR,
            'success': config.PAYMENT_SUCCESS_COLOR,
            'failure': config.PAYMENT_FAILURE_COLOR
        }
        color = color_map.get(state, config.PAYMENT_TEXT_COLOR)
        
        # Get frame dimensions
        h, w = frame.shape[:2]
        
        # Calculate text size for the message
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = config.PAYMENT_TEXT_SIZE
        thickness = 2
        
        # Get text dimensions
        (text_width, text_height), baseline = cv2.getTextSize(
            message, font, font_scale, thickness
        )
        
        # Calculate position (top center)
        padding = 20
        box_x = (w - text_width) // 2 - padding
        box_y = 20
        box_width = text_width + padding * 2
        box_height = text_height + padding * 2
        
        # Draw semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (box_x, box_y),
            (box_x + box_width, box_y + box_height),
            (40, 40, 40),
            -1
        )
        
        # Blend overlay
        alpha = config.PAYMENT_OVERLAY_ALPHA
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        # Draw border
        cv2.rectangle(
            frame,
            (box_x, box_y),
            (box_x + box_width, box_y + box_height),
            color,
            2
        )
        
        # Draw message text
        text_x = box_x + padding
        text_y = box_y + padding + text_height
        cv2.putText(
            frame,
            message,
            (text_x, text_y),
            font,
            font_scale,
            color,
            thickness,
            cv2.LINE_AA
        )
        
        # For success, add transaction digest below (smaller font)
        if state == 'success' and 'digest' in self.payment_status:
            digest = self.payment_status['digest']
            if len(digest) > 20:
                digest_short = f"{digest[:10]}...{digest[-10:]}"
            else:
                digest_short = digest
            
            small_font_scale = font_scale * 0.5
            small_thickness = 1
            
            cv2.putText(
                frame,
                digest_short,
                (text_x, text_y + 25),
                font,
                small_font_scale,
                (200, 200, 200),
                small_thickness,
                cv2.LINE_AA
            )
        
        return frame
    
    def _draw_transcription_overlay(self, frame):
        """Draw transcription text at bottom center of frame."""
        if not self.speech_transcriber or not self.speech_transcriber.is_ready():
            return frame
        
        # Get latest transcription
        transcription = self.speech_transcriber.get_latest_transcription()
        if not transcription or not transcription.strip():
            return frame
        
        # Get frame dimensions
        h, w = frame.shape[:2]
        
        # Prepare text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = config.TRANSCRIPTION_FONT_SCALE
        thickness = 1
        color = config.TRANSCRIPTION_TEXT_COLOR
        
        # Truncate if too long
        max_chars = 100
        if len(transcription) > max_chars:
            transcription = transcription[-max_chars:]
        
        # Get text dimensions
        (text_width, text_height), baseline = cv2.getTextSize(
            transcription, font, font_scale, thickness
        )
        
        # Calculate position (bottom center)
        padding = 10
        text_x = (w - text_width) // 2
        text_y = h - padding - 5
        
        # Draw semi-transparent background
        overlay = frame.copy()
        bg_x1 = text_x - padding
        bg_y1 = text_y - text_height - padding
        bg_x2 = text_x + text_width + padding
        bg_y2 = text_y + baseline + padding
        
        cv2.rectangle(
            overlay,
            (max(0, bg_x1), max(0, bg_y1)),
            (min(w, bg_x2), min(h, bg_y2)),
            (40, 40, 40),
            -1
        )
        
        # Blend overlay
        alpha = 0.7
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        # Draw text
        cv2.putText(
            frame,
            transcription,
            (text_x, text_y),
            font,
            font_scale,
            color,
            thickness,
            cv2.LINE_AA
        )
        
        return frame
    
    def _draw_amount_preview(self, frame):
        """Draw amount preview at top right of frame."""
        if not self.amount_preview:
            return frame
        
        amount = self.amount_preview.get('amount', 0)
        display_text = self.amount_preview.get('display_text', 'SUI')
        state = self.amount_preview.get('state', 'preview')
        
        # Get frame dimensions
        h, w = frame.shape[:2]
        
        # Prepare text
        text = f"Sending: {amount} {display_text}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = config.AMOUNT_FONT_SCALE
        thickness = 2
        color = config.AMOUNT_TEXT_COLOR
        
        # Get text dimensions
        (text_width, text_height), baseline = cv2.getTextSize(
            text, font, font_scale, thickness
        )
        
        # Calculate position (top right)
        padding = 20
        text_x = w - text_width - padding
        text_y = padding + text_height
        
        # Draw semi-transparent background
        overlay = frame.copy()
        bg_x1 = text_x - padding
        bg_y1 = text_y - text_height - padding
        bg_x2 = text_x + text_width + padding
        bg_y2 = text_y + baseline + padding
        
        cv2.rectangle(
            overlay,
            (bg_x1, bg_y1),
            (bg_x2, bg_y2),
            (40, 40, 40),
            -1
        )
        
        # Blend overlay
        alpha = 0.85
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        # Draw border
        cv2.rectangle(
            frame,
            (bg_x1, bg_y1),
            (bg_x2, bg_y2),
            color,
            2
        )
        
        # Draw text
        cv2.putText(
            frame,
            text,
            (text_x, text_y),
            font,
            font_scale,
            color,
            thickness,
            cv2.LINE_AA
        )
        
        return frame
    
    def _cleanup(self):
        """Clean up resources."""
        print("\nCleaning up...")
        self.stream_handler.release()
        self.event_logger.close()
        
        # Print face tracker stats if enabled
        if self.face_tracker:
            stats = self.face_tracker.get_statistics()
            print("\n=== Face Tracker Statistics ===")
            print(f"Unique faces detected: {stats['total_unique_faces']}")
            print(f"Total detections: {stats['total_detections']}")
            print(f"Faces saved to: {config.DETECTED_FACES_DIR}")
        
        # Close gesture detector if enabled
        if self.gesture_detector:
            self.gesture_detector.close()
        
        # Stop crypto server if enabled
        if self.crypto_handler:
            # Print transaction statistics
            try:
                stats = self.crypto_handler.get_transaction_stats()
                total = stats['total_sent']
                if total.get('SUI', 0) > 0 or total.get('XRPL', 0) > 0:
                    print("\n=== Transaction Statistics ===")
                    if total.get('SUI', 0) > 0:
                        print(f"Total SUI sent: {total['SUI']:.6f} SUI")
                    if total.get('XRPL', 0) > 0:
                        print(f"Total XRPL sent: {total['XRPL']:.6f} XRPL")
                    print(f"Transaction log: {config.LOGS_DIR}/transactions.csv")
            except Exception as e:
                pass
            
            self.crypto_handler.stop_server()
        
        # Stop speech transcription if enabled
        if self.speech_transcriber:
            self.speech_transcriber.stop()
        
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

