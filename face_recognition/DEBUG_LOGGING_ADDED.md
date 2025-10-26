# Debug Logging Added for Person 026 Issue

## Problem
Person 026 is being detected on camera and exists in the `face_searches` table, but the description is not updating from scraping. Need to trace the data flow to identify where the issue is occurring.

## Debug Logging Added

### 1. Supabase Query (`supabase_storage.py`)
**Location**: `query_face_search()` method

**Added logging**:
- Query details (table name, search pattern)
- Number of results found
- Full record details when found (ID, full_name, social_media presence, nyne_ai_response presence, google_image_results presence)
- Clear indication when no records found

### 2. Person Info Fetching (`person_info.py`)
**Location**: `_fetch_from_supabase()` method

**Added logging**:
- Person ID and image filename being queried
- Whether Supabase storage is available
- Query result status (found/not found)
- Data availability (full_name, social_media, nyne_ai_response)
- Full stack traces on errors

### 3. Database Row Parsing (`person_info.py`)
**Location**: `_parse_database_row()` method

**Added logging**:
- Person ID being parsed
- Full name and whether it exists
- Social media data presence
- Nyne AI response presence
- Decision logic (scraping vs completed)
- Cache hit/miss information
- When LLM summary generation is triggered

### 4. LLM Summary Generation (`person_info.py`)
**Location**: `_generate_llm_summary()` method

**Added logging**:
- **Input data details**:
  - Full name
  - Social media keys
  - Google images data length
  - Nyne response keys
- **LLM call details**:
  - Model name (from config)
  - Context length (characters)
  - Context preview (first 200 chars)
  - When Ollama is being called
- **Response details**:
  - Response length
  - Response preview (first 100 chars)
- Full stack traces on errors

### 5. Polling Thread (`person_info.py`)
**Location**: `_start_polling()` -> `poll_worker()` function

**Added logging**:
- Polling interval and max time settings
- Poll attempt number
- Each poll result (status)
- Cache update confirmation
- Decision to continue or stop polling
- Total polls and time elapsed when complete

### 6. Display Formatting (`info_display.py`)
**Location**: `_format_person_info()` function

**Added logging**:
- Person status
- Full name
- Summary length
- Summary preview
- Which display mode is being used (scraping/error/completed)
- Number of summary lines
- Preview of each line
- Total display lines generated

### 7. Main Display Logic (`main.py`)
**Location**: `_draw_results()` method

**Added logging**:
- When info box is being drawn
- API data keys available
- API data status
- PersonInfo object status after creation
- Confirmation when box is drawn
- Full error details with stack traces if drawing fails

### 8. Face Tracker API Storage (`face_tracker.py`)
**Location**: `store_api_response()`, `has_api_data()`, `get_api_data()` methods

**Added logging**:
- **store_api_response()**: Keys in dict, status, confirmation of storage
- **has_api_data()**: Whether person has API data
- **get_api_data()**: Whether person_info exists, status of data

## How to Use the Debug Output

When you run the application, you'll now see detailed console output showing:

1. **When person_026 is detected**: Look for the image filename in the Supabase query
2. **Database query results**: Check if the record is found and what data it contains
3. **Data parsing logic**: See if the system thinks data is available or still scraping
4. **LLM calls**: See the exact prompt being sent to Ollama and the response received
5. **Polling behavior**: Track when polls happen and what status changes occur
6. **Display updates**: Verify what's being shown on screen matches what's in the cache

## Key Debug Markers

- 🔍 - Searching/querying
- 💾 - Database/storage operations
- 📊 - Data parsing
- 🤖 - LLM operations
- 🔄 - Polling operations
- 🎨 - Display formatting
- 📺 - Main display logic
- ✅ - Success/completion
- ⚠️ - Warning
- ❌ - Error

## What to Look For

1. **Is the database query finding person_026?**
   - Look for: `💾 [DEBUG] Querying Supabase for: person_026_*.png`
   - Check: "Results found: 1" vs "Results found: 0"

2. **What data is in the database record?**
   - Check: "Has social_media: True/False"
   - Check: "Has nyne_ai_response: True/False"
   - Check: "Full name: [name or N/A]"

3. **Is the LLM being called?**
   - Look for: `🤖 [DEBUG] Generating LLM summary`
   - Check: "⏳ Calling Ollama..." followed by "✅ LLM response received"

4. **Is polling happening?**
   - Look for: `🔄 [DEBUG] Poll attempt #N`
   - Check: Status changes from "scraping" to "completed"

5. **Is the display updating?**
   - Look for: `🎨 [DEBUG] Formatting display`
   - Check: Status and summary content

## Next Steps

Run the application and look at the console output to identify at which stage the process is failing for person_026.

