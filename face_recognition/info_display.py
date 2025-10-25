"""
Information display module for rendering person details on video frames.
"""
import cv2
import numpy as np
from typing import Tuple, Optional
import config
from person_info import PersonInfo


def draw_person_info_box(
    frame: np.ndarray,
    person_info: PersonInfo,
    face_location: Tuple[int, int, int, int],
    position: str = "right"
) -> np.ndarray:
    """
    Draw person information box next to detected face.
    
    Args:
        frame: Video frame (BGR format)
        person_info: PersonInfo object with details to display
        face_location: Face bounding box (top, right, bottom, left)
        position: Position relative to face ("right", "left", "top", "bottom")
    
    Returns:
        Frame with info box drawn
    """
    top, right, bottom, left = face_location
    
    # Prepare text lines
    lines = _format_person_info(person_info)
    
    # Calculate box dimensions
    box_width, box_height, line_heights = _calculate_box_dimensions(lines)
    
    # Calculate box position
    box_x, box_y = _calculate_box_position(
        face_location, box_width, box_height, position, frame.shape
    )
    
    # Draw the info box
    _draw_info_box_background(frame, box_x, box_y, box_width, box_height)
    
    # Draw text lines
    _draw_text_lines(frame, lines, box_x, box_y, line_heights)
    
    return frame


def _format_person_info(person_info: PersonInfo) -> list:
    """
    Format person info into display lines.
    
    Args:
        person_info: PersonInfo object
    
    Returns:
        List of (text, font_scale, is_bold) tuples
    """
    lines = []
    
    # Name (bold, larger)
    lines.append((person_info.name, config.INFO_FONT_SCALE_TITLE, True))
    
    # Email
    lines.append((f"📧 {person_info.email}", config.INFO_FONT_SCALE_NORMAL, False))
    
    # Phone
    lines.append((f"📞 {person_info.phone}", config.INFO_FONT_SCALE_NORMAL, False))
    
    # Empty line
    lines.append(("", config.INFO_FONT_SCALE_NORMAL, False))
    
    # Employment history
    if person_info.employment_history:
        lines.append(("Employment:", config.INFO_FONT_SCALE_NORMAL, True))
        
        for entry in person_info.employment_history:
            # Role and company
            role_line = f"• {entry.role}"
            lines.append((role_line, config.INFO_FONT_SCALE_SMALL, False))
            
            company_line = f"  {entry.company}"
            lines.append((company_line, config.INFO_FONT_SCALE_SMALL, False))
            
            years_line = f"  {entry.years}"
            lines.append((years_line, config.INFO_FONT_SCALE_SMALL, False))
    
    return lines


def _calculate_box_dimensions(lines: list) -> Tuple[int, int, list]:
    """
    Calculate dimensions needed for info box.
    
    Args:
        lines: List of (text, font_scale, is_bold) tuples
    
    Returns:
        Tuple of (width, height, line_heights)
    """
    max_width = 0
    total_height = config.INFO_BOX_PADDING_TOP
    line_heights = []
    
    for text, font_scale, is_bold in lines:
        if text == "":
            # Empty line
            line_height = int(20 * font_scale)
            line_heights.append(line_height)
            total_height += line_height
            continue
        
        thickness = 2 if is_bold else 1
        (text_width, text_height), baseline = cv2.getTextSize(
            text,
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            thickness
        )
        
        max_width = max(max_width, text_width)
        line_height = text_height + baseline + config.INFO_LINE_SPACING
        line_heights.append(line_height)
        total_height += line_height
    
    total_height += config.INFO_BOX_PADDING_BOTTOM
    box_width = max_width + config.INFO_BOX_PADDING_LEFT + config.INFO_BOX_PADDING_RIGHT
    
    return box_width, total_height, line_heights


def _calculate_box_position(
    face_location: Tuple[int, int, int, int],
    box_width: int,
    box_height: int,
    position: str,
    frame_shape: Tuple
) -> Tuple[int, int]:
    """
    Calculate position for info box relative to face.
    
    Args:
        face_location: Face bounding box (top, right, bottom, left)
        box_width: Info box width
        box_height: Info box height
        position: Desired position ("right", "left", "top", "bottom")
        frame_shape: Frame dimensions (height, width, channels)
    
    Returns:
        Tuple of (x, y) for top-left corner of box
    """
    top, right, bottom, left = face_location
    frame_height, frame_width = frame_shape[:2]
    
    margin = config.INFO_BOX_MARGIN
    
    if position == "right":
        x = right + margin
        y = top
        # Ensure box fits in frame
        if x + box_width > frame_width:
            x = left - box_width - margin  # Try left instead
        if x < 0:
            x = margin
    
    elif position == "left":
        x = left - box_width - margin
        y = top
        if x < 0:
            x = right + margin  # Try right instead
        if x + box_width > frame_width:
            x = frame_width - box_width - margin
    
    elif position == "top":
        x = left
        y = top - box_height - margin
        if y < 0:
            y = bottom + margin  # Try bottom instead
    
    elif position == "bottom":
        x = left
        y = bottom + margin
        if y + box_height > frame_height:
            y = top - box_height - margin  # Try top instead
    
    else:
        # Default to right
        x = right + margin
        y = top
    
    # Final bounds checking
    x = max(0, min(x, frame_width - box_width))
    y = max(0, min(y, frame_height - box_height))
    
    return x, y


def _draw_info_box_background(
    frame: np.ndarray,
    x: int,
    y: int,
    width: int,
    height: int
) -> None:
    """
    Draw the background and border for info box.
    
    Args:
        frame: Video frame
        x, y: Top-left corner position
        width, height: Box dimensions
    """
    # Draw semi-transparent background
    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (x, y),
        (x + width, y + height),
        config.INFO_BOX_BG_COLOR,
        -1  # Filled
    )
    
    # Blend with original frame for transparency
    alpha = config.INFO_BOX_ALPHA
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    
    # Draw border
    cv2.rectangle(
        frame,
        (x, y),
        (x + width, y + height),
        config.INFO_BOX_BORDER_COLOR,
        config.INFO_BOX_BORDER_THICKNESS
    )


def _draw_text_lines(
    frame: np.ndarray,
    lines: list,
    box_x: int,
    box_y: int,
    line_heights: list
) -> None:
    """
    Draw text lines in the info box.
    
    Args:
        frame: Video frame
        lines: List of (text, font_scale, is_bold) tuples
        box_x, box_y: Top-left corner of box
        line_heights: Height for each line
    """
    current_y = box_y + config.INFO_BOX_PADDING_TOP
    
    for (text, font_scale, is_bold), line_height in zip(lines, line_heights):
        if text == "":
            # Skip empty lines
            current_y += line_height
            continue
        
        thickness = 2 if is_bold else 1
        
        # Calculate text position
        text_x = box_x + config.INFO_BOX_PADDING_LEFT
        text_y = current_y + line_height - config.INFO_LINE_SPACING
        
        # Draw text
        cv2.putText(
            frame,
            text,
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            config.INFO_TEXT_COLOR,
            thickness,
            cv2.LINE_AA
        )
        
        current_y += line_height

