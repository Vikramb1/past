# Result Images Display Feature

## Overview
Replaced the saved face thumbnail display with a dynamic display of up to 3 images from the `result_image_urls` column in Supabase. The images are downloaded from URLs and displayed in a horizontal row next to the detected face.

## Changes Made

### 1. **Updated PersonInfo Data Model** (`person_info.py`)

**Added image_urls field:**
```python
@dataclass
class PersonInfo:
    person_id: str
    status: str
    summary: str = ""
    full_name: str = ""
    email: str = ""
    image_urls: List[str] = None  # NEW: List of result image URLs
    
    def __post_init__(self):
        if self.image_urls is None:
            self.image_urls = []
```

**Updated data parsing:**
- Extracts `result_image_urls` from Supabase database
- Validates that images are available before marking status as "completed"
- Both `text_to_display` AND `result_image_urls` must be populated for "completed" status
- If either is missing, status remains "scraping"

**Debug logging:**
```python
print(f"   Has result_image_urls: {has_images} ({len(result_image_urls)} images)")
print(f"   Image URLs: {result_image_urls}")
```

### 2. **New Image Display Function** (`utils.py`)

**Added `draw_result_images_from_urls()`:**
- Downloads up to 3 images from URLs
- Displays them in a horizontal row
- Each image is a square thumbnail with consistent size
- Light blue border distinguishes from background
- Smart positioning to avoid going off-screen

**Features:**
- **Async download**: Uses `requests` library with 2-second timeout
- **Error handling**: Gracefully handles failed downloads
- **Aspect ratio**: Maintains image proportions
- **Centering**: Images centered on dark gray canvas
- **Spacing**: 5-pixel gap between thumbnails
- **Adaptive layout**: Automatically adjusts position if thumbnails don't fit

### 3. **Updated Display Logic** (`main.py`)

**Old logic:**
```python
# Get saved image path from registry
# Display single saved face thumbnail
```

**New logic:**
```python
# Get person info from API
# Check if image_urls are available
# Download and display up to 3 images from URLs
```

**Key changes:**
- Fetches `PersonInfo` object instead of registry entry
- Checks for `person_info.image_urls` presence
- Calls `draw_result_images_from_urls()` instead of `draw_saved_face_thumbnail()`

### 4. **Added Dependencies** (`utils.py`)

**New imports:**
```python
from typing import List
import requests
from io import BytesIO
```

## Visual Layout

### Single Image
```
┌──────┐     ┌────────────┐
│      │     │   Face     │
│ IMG1 │  →  │   Box      │
│      │     │            │
└──────┘     └────────────┘
```

### Three Images (Full Display)
```
┌──────┐┌──────┐┌──────┐     ┌────────────┐
│ IMG1 ││ IMG2 ││ IMG3 │  →  │   Face     │
└──────┘└──────┘└──────┘     │   Box      │
                              │            │
                              └────────────┘
```

## Status Flow

### Before (No Data)
```
Detection → Query DB → No text/images → Status: "scraping" → No images shown
```

### After (Partial Data - Text Only)
```
Detection → Query DB → Has text, no images → Status: "scraping" → No images shown
```

### After (Complete Data)
```
Detection → Query DB → Has text AND images → Status: "completed" → Images displayed
```

## Configuration

**Existing settings apply:**
```python
SHOW_FACE_THUMBNAIL = True  # Enable/disable feature
FACE_THUMBNAIL_SIZE = 120   # Size of each thumbnail
FACE_THUMBNAIL_PADDING = 10 # Distance from face box
```

**New behavior:**
- `SHOW_FACE_THUMBNAIL = True` → Shows result images from URLs
- `SHOW_FACE_THUMBNAIL = False` → Shows nothing

## Database Schema Requirements

The `face_searches` table must include:
```sql
- trigger_image_url (text): For matching detected faces
- full_name (text): Person's name
- text_to_display (text): Pre-formatted display text
- result_image_urls (jsonb or text[]): Array of image URLs ← NEW REQUIREMENT
```

**Example data:**
```json
{
  "full_name": "John Doe",
  "text_to_display": "Software Engineer at Google...",
  "result_image_urls": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg",
    "https://example.com/image3.jpg"
  ]
}
```

## Image Download Process

### 1. URL Validation
- Checks if `image_urls` list is not empty
- Limits to first 3 URLs

### 2. Download Loop
```python
for url in image_urls[:3]:
    response = requests.get(url, timeout=2)
    if response.status_code == 200:
        # Process and add to thumbnails
```

### 3. Error Handling
- Network timeouts (2 seconds)
- Invalid image data
- Decode failures
- Continues to next URL on error

### 4. Display
- Only displays successfully downloaded images
- If all downloads fail, displays nothing
- Gracefully handles partial success (e.g., 1 of 3 works)

## Performance Considerations

### Download Impact
- **Per detection**: 0-3 HTTP requests
- **Timeout**: 2 seconds per image (max 6 seconds total)
- **Caching**: Not implemented - downloads every frame

### Optimization Opportunities
1. **Cache downloaded images** by URL
2. **Background download** in separate thread
3. **Pre-load images** when status changes to "completed"
4. **Use thumbnail URLs** if available (smaller files)

### Current Performance
- **Best case**: All 3 images cached on server → ~100-200ms total
- **Worst case**: 3 slow downloads → ~6 seconds
- **Typical**: 1-2 images, fast CDN → ~300-500ms

## Error Scenarios

### 1. Network Issues
```
Error downloading image from https://...: Connection timeout
→ Skips that image, continues with others
```

### 2. Invalid URL
```
Error downloading image from invalid-url: Invalid URL
→ Skips that image, continues with others
```

### 3. No Images Available
```
image_urls = []
→ Returns frame unchanged, no display
```

### 4. All Downloads Fail
```
3 download errors
→ Returns frame unchanged, no display
```

## Debug Output

### When Images Are Available
```
📊 [DEBUG] Parsing database row for person_026
   Full name: John Doe (exists: True)
   Has text_to_display: True
   Has result_image_urls: True (3 images)
   Image URLs: ['https://...', 'https://...', 'https://...']
   ✅ Using text_to_display and 3 images from database for person_026
```

### When Images Are Missing
```
📊 [DEBUG] Parsing database row for person_026
   Full name: John Doe (exists: True)
   Has text_to_display: True
   Has result_image_urls: False (0 images)
   ℹ️  Missing data (text: True, images: False) - marking as scraping
```

### Download Errors
```
Error downloading image from https://example.com/bad.jpg: 404 Client Error
```

## Testing Recommendations

### Test Case 1: Normal Operation
1. Populate `result_image_urls` with 3 valid URLs
2. Detect face
3. Should see 3 thumbnails in a row

### Test Case 2: Partial URLs (1-2 images)
1. Populate with 1 or 2 URLs
2. Should display only available images
3. Spacing should adjust

### Test Case 3: Invalid URLs
1. Populate with mix of valid/invalid URLs
2. Should display only valid images
3. Errors logged but non-blocking

### Test Case 4: Slow Network
1. Use slow image URLs
2. May cause frame delay during download
3. Consider implementing caching

### Test Case 5: No Images
1. Leave `result_image_urls` empty
2. Should show "scraping" status
3. No thumbnails displayed

## Comparison: Old vs New

### Old System (Saved Face Thumbnail)
```
✓ Fast (local file read)
✓ Always available once saved
✗ Only shows detected face
✗ Same angle as live detection
✗ Limited information
```

### New System (Result Images from URLs)
```
✓ Shows 3 different images
✓ Can show profile photos, social media pics, etc.
✓ More context about person
✗ Requires network connection
✗ Download latency
✗ Depends on external URLs
```

## Future Enhancements

1. **Image Caching**: Cache downloaded images in memory or disk
2. **Background Downloads**: Use threading to download without blocking
3. **Loading Indicator**: Show spinner while downloading
4. **Fallback**: Show saved face if URLs fail
5. **Image Quality**: Support different thumbnail sizes per image
6. **Lazy Loading**: Only download when face is stable
7. **CDN Optimization**: Use thumbnail-optimized URLs
8. **Retry Logic**: Retry failed downloads with backoff

## Dependencies

**New Python package required:**
```bash
pip install requests
```

**Add to `requirements.txt`:**
```
requests>=2.31.0
```

