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
    Now just displays LLM-generated summary.
    
    Args:
        person_info: PersonInfo object
    
    Returns:
        List of (text, font_scale, is_bold) tuples
    """
    lines = []
    
    print(f"\n🎨 [DEBUG] Formatting display for person")
    print(f"   Status: {person_info.status}")
    print(f"   Full name: {person_info.full_name}")
    print(f"   Summary length: {len(person_info.summary)} chars")
    print(f"   Summary preview: {person_info.summary[:100] if person_info.summary else 'None'}...")
    
    # Check status
    if person_info.status == "scraping":
        print(f"   → Displaying scraping status")
        lines.append(("Scraping...", config.INFO_FONT_SCALE_TITLE, True))
        lines.append(("", config.INFO_FONT_SCALE_NORMAL, False))
        lines.append(("Fetching person info...", config.INFO_FONT_SCALE_SMALL, False))
        return lines
    
    if person_info.status == "error":
        print(f"   → Displaying error status")
        lines.append(("Error", config.INFO_FONT_SCALE_TITLE, True))
        lines.append(("Could not fetch info", config.INFO_FONT_SCALE_SMALL, False))
        return lines
    
    # Display name (bold)
    name = person_info.full_name or "Unknown Person"
    print(f"   → Displaying completed status with name: {name}")
    lines.append((name, config.INFO_FONT_SCALE_TITLE, True))
    lines.append(("", config.INFO_FONT_SCALE_NORMAL, False))  # Small spacer
    
    # Display LLM summary with word wrapping for narrow box
    summary_lines = person_info.summary.split('\n')
    print(f"   → Summary has {len(summary_lines)} lines")
    
    for i, line in enumerate(summary_lines):
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Skip lines that look like artifacts (e.g., "Here is...", "Example:", etc.)
        skip_phrases = [
            'here is', 'here are', 'here\'s',
            'example:', 'format:',
            'given this', 'write', 'rules:',
            'note:', 'summary:',
            '...', '...'  # Skip lines with ellipsis
        ]
        if any(phrase in line.lower() for phrase in skip_phrases):
            print(f"      Skipping artifact line: {line[:50]}")
            continue
        
        # Remove any emojis or bullets that might have slipped through
        # Remove common emoji patterns and bullet points
        cleaned_line = line
        for char in ['•', '◦', '▪', '▫', '–', '—', '*', '→', '►']:
            cleaned_line = cleaned_line.replace(char, '').strip()
        
        # Remove emojis (basic removal of common unicode ranges)
        import re
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        cleaned_line = emoji_pattern.sub('', cleaned_line).strip()
        
        # Skip if line became empty after cleaning
        if not cleaned_line:
            continue
        
        # Check if line is a URL (social media link)
        is_url = 'http://' in cleaned_line or 'https://' in cleaned_line or '.com/' in cleaned_line or 'linkedin.com' in cleaned_line or 'twitter.com' in cleaned_line
        font_scale = config.INFO_FONT_SCALE_SMALL if is_url else config.INFO_FONT_SCALE_NORMAL
        
        # Word wrap long lines to fit narrow box (max ~40 chars per line)
        if len(cleaned_line) > 45 and not is_url:
            words = cleaned_line.split()
            current_line = ""
            for word in words:
                test_line = f"{current_line} {word}".strip()
                if len(test_line) <= 45:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append((current_line, font_scale, False))
                    current_line = word
            if current_line:
                lines.append((current_line, font_scale, False))
        else:
            print(f"      Line {i}: {cleaned_line[:50]}")
            lines.append((cleaned_line, font_scale, False))
    
    print(f"   → Total display lines: {len(lines)}")
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
            line_height = int(15 * font_scale)
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
    
    # Apply maximum width constraint
    if box_width > config.INFO_BOX_MAX_WIDTH:
        box_width = config.INFO_BOX_MAX_WIDTH
    
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

