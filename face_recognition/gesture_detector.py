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
        self.peace_stability = {}  # Track peace sign stability over frames
        
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

                # Detect peace sign gesture
                is_peace, peace_confidence = self._detect_peace_sign(
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
                elif is_peace:
                    gesture_event = GestureEvent(
                        gesture_type="peace",
                        hand_bbox=hand_bbox,
                        confidence=peace_confidence,
                        hand_label=hand_label,
                        hold_duration=0.0
                    )
                    gesture_events.append(gesture_event)

                # Draw gesture if detected
                if is_snap or is_peace:
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
    
    def _detect_peace_sign(
        self,
        hand_landmarks,
        hand_id: str,
        frame_shape: Tuple[int, int, int]
    ) -> Tuple[bool, float]:
        """
        Detect peace sign gesture with robust multi-criteria checking.
        Requires temporal stability (multiple consecutive frames) for reliable detection.

        Args:
            hand_landmarks: MediaPipe hand landmarks
            hand_id: Unique hand identifier
            frame_shape: Frame dimensions

        Returns:
            Tuple of (is_peace_detected, confidence)
        """
        h, w, _ = frame_shape

        # Get key landmarks for fingers
        # Tips (endpoints of fingers)
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        middle_tip = hand_landmarks.landmark[12]
        ring_tip = hand_landmarks.landmark[16]
        pinky_tip = hand_landmarks.landmark[20]

        # PIPs (middle joints) - used to check if fingers are extended
        thumb_ip = hand_landmarks.landmark[3]
        index_pip = hand_landmarks.landmark[6]
        index_dip = hand_landmarks.landmark[7]
        middle_pip = hand_landmarks.landmark[10]
        middle_dip = hand_landmarks.landmark[11]
        ring_pip = hand_landmarks.landmark[14]
        pinky_pip = hand_landmarks.landmark[18]

        # MCPs (base joints)
        index_mcp = hand_landmarks.landmark[5]
        middle_mcp = hand_landmarks.landmark[9]
        ring_mcp = hand_landmarks.landmark[13]
        pinky_mcp = hand_landmarks.landmark[17]
        thumb_mcp = hand_landmarks.landmark[2]

        # Wrist for reference
        wrist = hand_landmarks.landmark[0]

        # Convert to pixel coordinates for distance calculations
        def to_pixels(landmark):
            return np.array([landmark.x * w, landmark.y * h])

        index_tip_px = to_pixels(index_tip)
        middle_tip_px = to_pixels(middle_tip)
        ring_tip_px = to_pixels(ring_tip)
        pinky_tip_px = to_pixels(pinky_tip)
        thumb_tip_px = to_pixels(thumb_tip)
        wrist_px = to_pixels(wrist)
        index_mcp_px = to_pixels(index_mcp)
        palm_center_px = to_pixels(hand_landmarks.landmark[9])  # Middle finger MCP as palm reference

        # 1. Check if index and middle fingers are FULLY extended
        # More robust: check all joints from tip to base
        index_extended = (
            index_tip.y < index_dip.y < index_pip.y < index_mcp.y and
            (index_tip.y < index_mcp.y - 0.1)  # Significant extension
        )
        middle_extended = (
            middle_tip.y < middle_dip.y < middle_pip.y < middle_mcp.y and
            (middle_tip.y < middle_mcp.y - 0.1)  # Significant extension
        )

        # 2. Check if ring and pinky are CLEARLY folded
        # More robust: tips should be closer to palm than MCPs
        ring_folded = (ring_tip.y >= ring_mcp.y - 0.03)
        pinky_folded = (pinky_tip.y >= pinky_mcp.y - 0.03)
        
        # Additional check: ring and pinky should be close to palm
        ring_to_palm_dist = np.linalg.norm(ring_tip_px - palm_center_px)
        pinky_to_palm_dist = np.linalg.norm(pinky_tip_px - palm_center_px)
        hand_size = np.linalg.norm(index_mcp_px - wrist_px)
        ring_close_to_palm = ring_to_palm_dist < hand_size * 0.6
        pinky_close_to_palm = pinky_to_palm_dist < hand_size * 0.7

        # 3. Check thumb position (should not be extended upward)
        thumb_not_up = (thumb_tip.y >= thumb_mcp.y - 0.05)

        # 4. Check finger spacing - peace sign has moderate separation
        index_middle_distance_px = np.linalg.norm(index_tip_px - middle_tip_px)
        index_middle_distance_norm = index_middle_distance_px / hand_size
        
        # Peace sign: fingers slightly separated but not too far apart
        fingers_properly_spaced = (0.15 < index_middle_distance_norm < 0.5)

        # 5. Check finger angles (should point roughly upward)
        index_vector = index_tip_px - index_mcp_px
        middle_vector = middle_tip_px - to_pixels(middle_mcp)
        
        # Calculate angles from vertical
        index_angle = np.degrees(np.arctan2(index_vector[0], -index_vector[1]))
        middle_angle = np.degrees(np.arctan2(middle_vector[0], -middle_vector[1]))
        
        # Fingers should point generally upward (within 45 degrees of vertical)
        index_upright = abs(index_angle) < 50
        middle_upright = abs(middle_angle) < 50
        
        # Fingers should be roughly parallel (similar angles)
        fingers_parallel = abs(index_angle - middle_angle) < 30

        # 6. Check that extended fingers are significantly longer than folded ones
        index_length = np.linalg.norm(index_tip_px - index_mcp_px)
        middle_length = np.linalg.norm(middle_tip_px - to_pixels(middle_mcp))
        ring_length = np.linalg.norm(ring_tip_px - to_pixels(ring_mcp))
        
        extended_significantly_longer = (
            index_length > ring_length * 1.3 and
            middle_length > ring_length * 1.3
        )

        # Combine all criteria with scoring
        criteria = {
            'index_extended': index_extended,
            'middle_extended': middle_extended,
            'ring_folded': ring_folded and ring_close_to_palm,
            'pinky_folded': pinky_folded and pinky_close_to_palm,
            'thumb_not_up': thumb_not_up,
            'fingers_spaced': fingers_properly_spaced,
            'index_upright': index_upright,
            'middle_upright': middle_upright,
            'fingers_parallel': fingers_parallel,
            'length_check': extended_significantly_longer
        }
        
        # Count how many criteria are met
        criteria_met = sum(criteria.values())
        total_criteria = len(criteria)
        
        # Require at least 8 out of 10 criteria to be met
        is_peace_candidate = criteria_met >= 8

        # Initialize stability tracking
        if hand_id not in self.peace_stability:
            self.peace_stability[hand_id] = {
                'frames': [],
                'last_update': time.time()
            }

        current_time = time.time()
        stability = self.peace_stability[hand_id]
        
        # Clear old frames (older than 0.5 seconds)
        stability['frames'] = [
            f for f in stability['frames'] 
            if current_time - f['time'] < 0.5
        ]
        
        # Add current detection
        if is_peace_candidate:
            stability['frames'].append({
                'time': current_time,
                'confidence': criteria_met / total_criteria,
                'criteria': criteria
            })
        
        # Require stable detection over at least 3 consecutive frames (roughly 0.1-0.15 seconds)
        stable_frames = len(stability['frames'])
        is_peace = is_peace_candidate and stable_frames >= 3

        # Calculate confidence
        confidence = 0.0
        if is_peace:
            # Base confidence from criteria
            confidence = criteria_met / total_criteria
            
            # Bonus for stability
            if stable_frames >= 5:
                confidence = min(1.0, confidence + 0.1)

            # Check cooldown to prevent spam
            cooldown_key = f"peace_{hand_id}"
            if cooldown_key in self.gesture_cooldowns:
                if current_time - self.gesture_cooldowns[cooldown_key] < config.GESTURE_COOLDOWN_SECONDS:
                    return False, 0.0

            # Update cooldown
            self.gesture_cooldowns[cooldown_key] = current_time
            
            # Clear stability after detection
            stability['frames'] = []
            
            print(f"✌️ PEACE SIGN detected! Hand: {hand_id}, Confidence: {confidence:.2f}, "
                  f"Criteria: {criteria_met}/{total_criteria}, Stable frames: {stable_frames}")
            print(f"   Details: {', '.join([k for k, v in criteria.items() if v])}")

        return is_peace, confidence

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
        
        # Draw gesture label based on type
        if gesture_event.gesture_type == "peace":
            label = f"PEACE! ({gesture_event.hand_label})"
        else:
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
        self.peace_stability = {}
    
    def close(self):
        """Clean up resources."""
        self.hands.close()

