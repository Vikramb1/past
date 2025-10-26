# Supabase Person Info Integration - Complete

## Overview

Successfully replaced the dummy person info system with real data from Supabase `face_searches` table containing Nyne AI analysis results. The system now polls every 1 second until data is populated, displaying "Scraping..." while waiting.

## Implementation Summary

### 1. Database Query Layer (supabase_storage.py)

Added `query_face_search()` method to query the `face_searches` table:
- Matches on `trigger_image_url` containing the image filename
- Uses SQL LIKE pattern matching (e.g., `%person_001_1729901234.png%`)
- Returns first matching row or None

### 2. Data Model Update (person_info.py)

**Replaced dataclasses:**
- OLD: `EmploymentEntry` 
- NEW: `Organization`, `Education`, `SocialProfile`

**Updated PersonInfo fields:**
- `status`: "scraping", "completed", or "error"
- `displayname`: Person's display name
- `bio`: Biography text
- `location`: Location string
- `gender`: Gender
- `phones`: List of phone numbers
- `emails`: List of email addresses
- `social_profiles`: List of SocialProfile objects (LinkedIn, Twitter, etc.)
- `organizations`: List of Organization objects (work history)
- `schools`: List of Education objects

### 3. Real-Time Data Fetching (person_info.py)

**PersonInfoAPI refactored:**
- Accepts `image_filename` parameter
- Queries Supabase via `SupabaseStorage.query_face_search()`
- Parses Nyne AI JSON response structure: `data.result.displayname`, etc.
- Returns PersonInfo with appropriate status

**Status handling:**
- No data found → status="scraping"
- data.status != "completed" → status="scraping"
- data.status == "completed" → status="completed", parse all fields
- Parse error → status="error"

### 4. Background Polling Mechanism (person_info.py)

**Automatic polling for "scraping" entries:**
- Background thread starts when status="scraping"
- Polls every 1 second (configurable via `PERSON_INFO_POLL_INTERVAL`)
- Updates cache when data becomes available
- Stops polling when:
  - Data is completed
  - Error occurs
  - Max timeout reached (5 minutes by default)
- Thread-safe with daemon threads

### 5. Display Updates (info_display.py)

**Updated `_format_person_info()` to handle new fields:**

**Scraping state:**
```
🔍 Scraping...
Fetching person info
```

**Error state:**
```
❌ Error
Could not fetch info
```

**Completed state displays:**
1. **Display name** (bold, large)
2. **Bio** (truncated to 100 chars)
3. **Location & Gender** (📍 San Francisco, CA | Male)
4. **First Email** (📧)
5. **First Phone** (📞)
6. **Current Organization** (💼 title at company)
7. **Education** (🎓 degree in major)
8. **Social Profiles** (max 2: LinkedIn 💼, Twitter 🐦)

All fields are optional - only displays what's available.

### 6. Main Application Integration (main.py)

Updated person info fetching:
```python
# Get registry entry to extract image filename
registry_entry = self.face_tracker.get_person_info(tracked_id)
image_filename = registry_entry.get('image_filename') if registry_entry else None

# Call API with image filename for matching
person_info = self.person_api.get_person_info(
    person_id=tracked_id,
    image_filename=image_filename
)
```

### 7. Configuration (config.py)

Added new settings:
```python
# Person info polling settings (for Supabase integration)
PERSON_INFO_POLL_INTERVAL = 1.0  # Poll every 1 second for scraping data
PERSON_INFO_MAX_POLL_TIME = 300  # Stop polling after 5 minutes
```

## Nyne AI Response Structure

The system expects this JSON structure in the `nyne_response` column:

```json
{
  "success": true,
  "data": {
    "request_id": "...",
    "status": "completed",
    "result": {
      "displayname": "John Smith",
      "bio": "John Smith is a software engineer...",
      "location": "San Francisco, CA",
      "gender": "Male",
      "fullphone": [
        { "fullphone": "(555) 123-4567" }
      ],
      "altemails": [
        "john.smith@example.com",
        "j.smith@company.com"
      ],
      "social_profiles": {
        "linkedin": {
          "url": "https://www.linkedin.com/in/johnsmith",
          "username": "johnsmith"
        },
        "twitter": {
          "url": "https://twitter.com/johnsmith",
          "username": "johnsmith"
        }
      },
      "organizations": [
        {
          "name": "Tech Corp",
          "title": "Senior Software Engineer"
        },
        {
          "name": "Startup Inc",
          "title": "Software Engineer",
          "startDate": "2020-01-01"
        }
      ],
      "school_info": [
        {
          "name": "State University",
          "degree": "BS",
          "title": "Computer Science"
        }
      ]
    }
  }
}
```

## How It Works

### Initial Detection Flow

1. **Face detected** → Image saved to `detected_faces/person_XXX_timestamp.png`
2. **Image uploaded** to Supabase storage
3. **Person info API called** with `image_filename="person_XXX_timestamp.png"`
4. **Database queried** for matching `trigger_image_url`

### Scraping State Flow

```
Query Database
    ↓
No match found OR status != "completed"
    ↓
Return PersonInfo(status="scraping")
    ↓
Display "🔍 Scraping..."
    ↓
Start background polling thread
    ↓
Poll every 1 second
    ↓
Check database again
    ↓
Data ready? → Update cache → Display real info
Still scraping? → Continue polling
Timeout (5 min)? → Stop polling
```

### Completed State Flow

```
Query Database
    ↓
Match found AND status == "completed"
    ↓
Parse Nyne AI JSON
    ↓
Extract: displayname, bio, location, etc.
    ↓
Return PersonInfo(status="completed", ...)
    ↓
Display formatted info box with all available data
```

## Database Schema Requirements

The `face_searches` table should have at minimum:
- `trigger_image_url` (text): Contains the image filename
- `nyne_response` (jsonb or text): Contains the Nyne AI response JSON

## Testing

### Test with Scraping State

1. Run the face recognition system
2. Detect a face (image gets uploaded to Supabase)
3. Should display "🔍 Scraping... / Fetching person info"
4. Watch console for polling messages
5. When data appears in database, display updates automatically

### Test with Completed Data

1. Manually insert test data into `face_searches` table:
```sql
INSERT INTO face_searches (trigger_image_url, nyne_response)
VALUES (
  'person_001_1729901234.png',
  '{"data": {"status": "completed", "result": {"displayname": "Test Person", ...}}}'::jsonb
);
```
2. Run face recognition and detect the face
3. Should immediately show real person info

### Verify Polling

Check console output:
```
⚠️  No data found for person_001 yet
✅ Person info ready for person_001: John Smith
```

## Error Handling

**No Supabase client:**
- Returns PersonInfo(status="error", displayname="DB Error")

**No database match:**
- Returns PersonInfo(status="scraping", displayname="Scraping...")
- Starts polling

**Parse error:**
- Returns PersonInfo(status="error", displayname="Parse Error")
- Logs error to console

**Polling timeout:**
- Stops polling after 5 minutes
- Leaves status as "scraping"
- User still sees "🔍 Scraping..." message

## Performance Considerations

**Caching:**
- All fetched data is cached in memory
- No redundant queries for same person_id
- Cache persists for application lifetime

**Polling overhead:**
- 1 query per second per scraping person
- Daemon threads don't block main execution
- Automatic cleanup when data found or timeout

**Database load:**
- Lightweight SELECT queries with LIKE matching
- Single row returned per query
- Consider adding index on `trigger_image_url` for performance

## Cleanup

**Stop all polling:**
```python
person_api.stop_polling()  # Stop all
person_api.stop_polling(person_id)  # Stop specific
```

**Clear cache:**
```python
person_api.clear_cache()  # Also stops all polling
```

## Files Modified

1. ✅ `supabase_storage.py` - Added `query_face_search()` method
2. ✅ `person_info.py` - Complete rewrite with Nyne AI integration
3. ✅ `info_display.py` - Updated display formatting for new fields
4. ✅ `main.py` - Pass `image_filename` to API calls
5. ✅ `config.py` - Added polling configuration

## Summary

The system now:
- ✅ Queries real Supabase data instead of generating dummy data
- ✅ Matches face images to database entries via filename
- ✅ Shows "Scraping..." while waiting for data
- ✅ Polls every 1 second until data is ready
- ✅ Displays comprehensive person info from Nyne AI
- ✅ Handles all optional fields gracefully
- ✅ Provides thread-safe background polling
- ✅ Includes timeout protection (5 minutes)
- ✅ Fully backward compatible with existing code

Ready to use! 🚀

