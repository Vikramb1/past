"""
Gesture detection module for recognizing hand gestures like snaps/clicks.
Uses MediaPipe for hand tracking and custom logic for gesture detection.
"""
import cv2
import mediapipe as mp
import numpy as np
import time
from typing import List, Tuple, Optional, Dict
import config


class GestureEvent:
    """Represents a detected gesture event."""
    
    def __init__(self, gesture_type: str, hand_bbox: Tuple[int, int, int, int], 
                 confidence: float, hand_label: str, hold_duration: float = 0.0):
        """
        Initialize gesture event.
        
        Args:
            gesture_type: Type of gesture (e.g., "snap", "click")
            hand_bbox: Hand bounding box (x, y, width, height)
            confidence: Gesture confidence (0.0-1.0)
            hand_label: "Left" or "Right"
            hold_duration: Duration in seconds gesture has been held
        """
        self.gesture_type = gesture_type
        self.hand_bbox = hand_bbox
        self.confidence = confidence
        self.hand_label = hand_label
        self.hold_duration = hold_duration
        self.timestamp = time.time()


class GestureDetector:
    """Detects hand gestures using MediaPipe."""
    
    def __init__(self):
        """Initialize the gesture detector."""
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=config.GESTURE_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.GESTURE_DETECTION_CONFIDENCE
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Tracking variables for gesture detection
        self.finger_distances = {}  # Track distance history per hand
        self.gesture_cooldowns = {}  # Prevent repeated triggers
        self.last_detection_time = {}
        self.gesture_states = {}  # Track current gesture state per hand
        
        print(f"Gesture detector initialized")
        print(f"Detection confidence: {config.GESTURE_DETECTION_CONFIDENCE}")
        print(f"Cooldown period: {config.GESTURE_COOLDOWN_SECONDS}s")
    
    def detect_gestures(self, frame: np.ndarray) -> Tuple[List[GestureEvent], np.ndarray]:
        """
        Detect gestures in a frame.
        
        Args:
            frame: BGR image frame
        
        Returns:
            Tuple of (gesture_events, annotated_frame)
        """
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process frame
        results = self.hands.process(rgb_frame)
        
        gesture_events = []
        annotated_frame = frame.copy()
        
        if results.multi_hand_landmarks:
            for hand_idx, (hand_landmarks, hand_info) in enumerate(
                zip(results.multi_hand_landmarks, results.multi_handedness)
            ):
                # Get hand label (Left/Right)
                hand_label = hand_info.classification[0].label
                hand_id = f"{hand_label}_{hand_idx}"
                
                # Get hand bounding box
                hand_bbox = self._get_hand_bbox(hand_landmarks, frame.shape)
                
                # Detect snap gesture
                is_snap, confidence, hold_duration = self._detect_snap(
                    hand_landmarks, 
                    hand_id,
                    frame.shape
                )
                
                # Create gesture event if detected
                if is_snap:
                    gesture_event = GestureEvent(
                        gesture_type="snap",
                        hand_bbox=hand_bbox,
                        confidence=confidence,
                        hand_label=hand_label,
                        hold_duration=hold_duration
                    )
                    gesture_events.append(gesture_event)
                    
                    # Draw snap detection
                    annotated_frame = self._draw_gesture(
                        annotated_frame,
                        gesture_event,
                        hand_landmarks
                    )
                else:
                    # Draw regular hand detection
                    annotated_frame = self._draw_hand(
                        annotated_frame,
                        hand_bbox,
                        hand_label,
                        hand_landmarks
                    )
        
        return gesture_events, annotated_frame
    
    def _get_hand_bbox(
        self, 
        hand_landmarks, 
        frame_shape: Tuple[int, int, int]
    ) -> Tuple[int, int, int, int]:
        """
        Calculate bounding box for hand.
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            frame_shape: Frame dimensions (height, width, channels)
        
        Returns:
            Bounding box (x, y, width, height)
        """
        h, w, _ = frame_shape
        
        # Get all landmark coordinates
        x_coords = [lm.x * w for lm in hand_landmarks.landmark]
        y_coords = [lm.y * h for lm in hand_landmarks.landmark]
        
        # Calculate bounding box
        x_min = int(min(x_coords))
        x_max = int(max(x_coords))
        y_min = int(min(y_coords))
        y_max = int(max(y_coords))
        
        # Add padding
        padding = 20
        x_min = max(0, x_min - padding)
        y_min = max(0, y_min - padding)
        x_max = min(w, x_max + padding)
        y_max = min(h, y_max + padding)
        
        return (x_min, y_min, x_max - x_min, y_max - y_min)
    
    def _detect_snap(
        self,
        hand_landmarks,
        hand_id: str,
        frame_shape: Tuple[int, int, int]
    ) -> Tuple[bool, float, float]:
        """
        Detect snap gesture by identifying the crossed X shape formed by 
        thumb and index finger after a snap.
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            hand_id: Unique hand identifier
            frame_shape: Frame dimensions
        
        Returns:
            Tuple of (is_snap_detected, confidence, hold_duration)
        """
        h, w, _ = frame_shape
        
        # Get key landmarks
        thumb_tip = hand_landmarks.landmark[4]      # Thumb tip
        thumb_ip = hand_landmarks.landmark[3]       # Thumb IP joint
        index_tip = hand_landmarks.landmark[8]      # Index finger tip
        index_mcp = hand_landmarks.landmark[5]      # Index finger base (MCP joint)
        middle_tip = hand_landmarks.landmark[12]    # Middle finger tip
        
        # Convert to pixel coordinates
        thumb_tip_pos = np.array([thumb_tip.x * w, thumb_tip.y * h])
        thumb_ip_pos = np.array([thumb_ip.x * w, thumb_ip.y * h])
        index_tip_pos = np.array([index_tip.x * w, index_tip.y * h])
        index_mcp_pos = np.array([index_mcp.x * w, index_mcp.y * h])
        middle_tip_pos = np.array([middle_tip.x * w, middle_tip.y * h])
        
        # Initialize tracking for this hand if needed
        if hand_id not in self.gesture_states:
            self.gesture_states[hand_id] = {
                'active': False,
                'start_time': 0,
                'last_print_time': 0,
                'payment_triggered': False  # Track if payment sent this hold
            }
        
        # Check if thumb and index are in snap position
        thumb_index_distance = np.linalg.norm(thumb_tip_pos - index_tip_pos)
        index_middle_distance = np.linalg.norm(index_tip_pos - middle_tip_pos)
        
        # Calculate crossing angle
        index_vector = index_tip_pos - index_mcp_pos
        thumb_vector = thumb_tip_pos - thumb_ip_pos
        
        cos_angle = np.dot(index_vector, thumb_vector) / (
            np.linalg.norm(index_vector) * np.linalg.norm(thumb_vector) + 1e-6
        )
        angle_degrees = np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))
        
        # Snap position criteria (holding the snap pose)
        # More relaxed thresholds to maintain detection while holding
        in_snap_position = (
            thumb_index_distance < 40 and          # Fingers are close/touching (relaxed threshold)
            20 < angle_degrees < 90 and            # Fingers form crossing angle (relaxed)
            index_middle_distance > 20             # Middle finger is separated (relaxed)
        )
        
        current_time = time.time()
        state = self.gesture_states[hand_id]
        
        if in_snap_position:
            # Calculate confidence
            distance_score = max(0, 1.0 - (thumb_index_distance / 40))
            angle_score = 1.0 - abs(angle_degrees - 50) / 40
            angle_score = max(0, min(1.0, angle_score))
            confidence = (distance_score + angle_score) / 2
            
            if not state['active']:
                # New snap detected - entering snap position
                state['active'] = True
                state['start_time'] = current_time
                state['last_print_time'] = current_time
                state['payment_triggered'] = False  # Reset payment trigger
                print(f"SNAP detected! Hand: {hand_id}, Confidence: {confidence:.2f}, "
                      f"Angle: {angle_degrees:.1f}°, Distance: {thumb_index_distance:.1f}px")
            else:
                # Already in snap position - only print occasionally
                if current_time - state['last_print_time'] > 2.0:
                    state['last_print_time'] = current_time
                    duration = current_time - state['start_time']
                    print(f"SNAP held for {duration:.1f}s, Confidence: {confidence:.2f}")
            
            # Calculate hold duration
            hold_duration = current_time - state['start_time']
            return True, confidence, hold_duration
        else:
            # Not in snap position
            if state['active']:
                # Was in snap position, now released
                duration = current_time - state['start_time']
                print(f"SNAP released after {duration:.1f}s")
                state['active'] = False
                state['payment_triggered'] = False  # Reset on release
            
            return False, 0.0, 0.0
    
    def _draw_gesture(
        self,
        frame: np.ndarray,
        gesture_event: GestureEvent,
        hand_landmarks
    ) -> np.ndarray:
        """
        Draw detected gesture on frame.
        
        Args:
            frame: Image frame
            gesture_event: Detected gesture event
            hand_landmarks: MediaPipe hand landmarks
        
        Returns:
            Annotated frame
        """
        x, y, w, h = gesture_event.hand_bbox
        
        # Draw bounding box (green for detected gesture)
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            config.GESTURE_BOX_COLOR,
            config.GESTURE_BOX_THICKNESS
        )
        
        # Draw gesture label
        label = f"{config.GESTURE_LABEL_TEXT} ({gesture_event.hand_label})"
        label_size = cv2.getTextSize(
            label,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            2
        )[0]
        
        # Draw label background
        cv2.rectangle(
            frame,
            (x, y - label_size[1] - 10),
            (x + label_size[0] + 10, y),
            config.GESTURE_BOX_COLOR,
            -1
        )
        
        # Draw label text
        cv2.putText(
            frame,
            label,
            (x + 5, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )
        
        # Draw hand landmarks if enabled
        if config.SHOW_HAND_LANDMARKS:
            self.mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS
            )
        
        return frame
    
    def _draw_hand(
        self,
        frame: np.ndarray,
        hand_bbox: Tuple[int, int, int, int],
        hand_label: str,
        hand_landmarks
    ) -> np.ndarray:
        """
        Draw detected hand (no gesture) on frame.
        
        Args:
            frame: Image frame
            hand_bbox: Hand bounding box
            hand_label: "Left" or "Right"
            hand_landmarks: MediaPipe hand landmarks
        
        Returns:
            Annotated frame
        """
        x, y, w, h = hand_bbox
        
        # Draw bounding box (blue for hand without gesture)
        color = (255, 150, 0)  # Blue
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            color,
            2
        )
        
        # Draw hand label
        label = f"{hand_label} Hand"
        cv2.putText(
            frame,
            label,
            (x + 5, y + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1,
            cv2.LINE_AA
        )
        
        # Draw hand landmarks if enabled
        if config.SHOW_HAND_LANDMARKS:
            self.mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS
            )
        
        return frame
    
    def reset(self):
        """Reset tracking state."""
        self.finger_distances = {}
        self.gesture_cooldowns = {}
        self.last_detection_time = {}
        self.gesture_states = {}
    
    def close(self):
        """Clean up resources."""
        self.hands.close()

