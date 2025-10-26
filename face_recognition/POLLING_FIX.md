# Polling Update Fix for Person Info

## Root Cause Identified

The debug logging revealed the issue: **The polling thread was updating the API cache but NOT the face_tracker registry, so the display never showed updates.**

### The Problem Flow:

1. **First detection of person_026**:
   - `get_person_info()` is called → returns status="scraping"
   - Result stored in face_tracker: `store_api_response()` → sets `api_called=True`
   - Polling thread starts in background

2. **Subsequent frames**:
   - Main loop checks: `if not face_tracker.has_api_data(person_id)` → **FALSE** (because `api_called=True`)
   - API is never called again!
   - Display keeps reading from face_tracker, which still has status="scraping"

3. **Polling thread (running in background)**:
   - Polls Supabase every 1 second
   - Updates `PersonInfoAPI._cache` with new data
   - **BUT** never updates the `face_tracker.registry`!

4. **Display rendering**:
   - Reads from `face_tracker.get_api_data()` → still returns old "scraping" status
   - Never sees the updated data from polling!

### Why the Disconnect?

There were two separate caches:
- `PersonInfoAPI._cache` - Updated by polling thread ✓
- `FaceTracker.registry[person_id]['person_info']` - Never updated by polling ✗

The display only read from the face_tracker, so it never saw updates.

## The Fix

### Changes Made:

1. **Added face_tracker reference to PersonInfoAPI** (`person_info.py`):
   ```python
   def __init__(self, face_tracker=None):
       self._face_tracker = face_tracker  # Store reference
   ```

2. **Updated polling thread to write to both caches** (`person_info.py`):
   ```python
   # Update API cache
   self._cache[person_id] = updated_info
   
   # IMPORTANT: Also update face_tracker if available
   if self._face_tracker:
       self._face_tracker.store_api_response(person_id, updated_info.to_dict())
   ```

3. **Pass face_tracker when creating API instance** (`main.py`):
   ```python
   self.person_api = get_api_instance(face_tracker=self.face_tracker)
   ```

### How It Works Now:

1. First detection → API called → status="scraping" stored in both caches → polling starts
2. Polling thread runs every 1 second
3. When data becomes available in Supabase:
   - Polling fetches updated data with status="completed"
   - Updates `PersonInfoAPI._cache` ✓
   - **NOW ALSO** updates `face_tracker.registry` ✓
4. Display reads from face_tracker → sees updated status="completed" → shows LLM summary!

## Testing

After this fix, you should see in the console:

```
🔄 [DEBUG] Poll attempt #1 for person_026
💾 [DEBUG] Querying Supabase for: person_026_*.png
   Results found: 1
   ✅ Found record:
      - Full name: [name]
      - Social media: True
      - Nyne AI response: True
📊 [DEBUG] Parsing database row for person_026
   Full name: [name] (exists: True)
   🧠 Need to generate LLM summary for person_026
🤖 [DEBUG] Generating LLM summary for person_026
   ⏳ Calling Ollama...
   ✅ LLM response received
   ✅ Cache updated for person_026
   ✅ Face tracker updated for person_026  <-- NEW!
✅ Person info ready for person_026: [name]
```

Then on the next frame render, the display will show the completed info instead of "scraping"!

## Related Files Modified

- `face_recognition/person_info.py` - Added face_tracker reference and polling update
- `face_recognition/main.py` - Pass face_tracker to API instance

