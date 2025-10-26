# Root Cause: Person_026 Stuck at "Scraping" Status

## The Real Problem

After adding debugging, we discovered the actual issue wasn't with the query or polling logic - it was with **when the API was being called**.

### What Was Happening:

1. **First Detection** (previous run):
   - person_026 detected → API called → returns status="scraping"
   - Data stored in face_registry.json with `api_called=True`
   - Polling **should** start but app was closed before polling completed

2. **Current Run**:
   - person_026 detected again
   - Main loop checks: `if not has_api_data()` → **Returns FALSE** (because `api_called=True`)
   - **API is never called again!**
   - Polling never starts because `get_person_info()` is never called
   - Display keeps showing old cached "scraping" status from registry

### The Evidence:

From `face_registry.json` line 753-772:
```json
"person_026": {
  "image_filename": "person_026_1761447798.png",
  "person_info": {
    "person_id": "person_026",
    "status": "scraping",
    "summary": "🔍 Scraping...",
    "full_name": ""
  },
  "api_called": true  ← This prevented re-checking!
}
```

The debug output showed:
- ✅ Face detection working
- ✅ Display logic working
- ❌ No Supabase query logs (API never called)
- ❌ No polling logs (polling never started)

## The Fix

Changed `main.py` to **always call `get_person_info()`** for detected faces, not just when `api_called=False`.

### Old Logic (Broken):
```python
if not self.face_tracker.has_api_data(tracked_id):
    # Only call API if never called before
    person_info = self.person_api.get_person_info(...)
```

**Problem**: Once `api_called=True`, API never called again, even if data is still "scraping".

### New Logic (Fixed):
```python
# Always call get_person_info for every detected face
person_info = self.person_api.get_person_info(
    person_id=tracked_id,
    image_filename=image_filename
)

# Update tracker only if status changed
if not api_data or api_data.get('status') != person_info.status:
    self.face_tracker.store_api_response(...)
```

**Benefits**:
1. ✅ `get_person_info()` uses internal cache (fast for repeated calls)
2. ✅ Checks `_cache` first - returns immediately if cached
3. ✅ For "scraping" status, ensures polling is active (line 86-87 in person_info.py)
4. ✅ Polling thread updates both caches
5. ✅ When status changes to "completed", tracker gets updated
6. ✅ Display shows new status on next frame

## How It Works Now:

### Frame N (person_026 detected):
```
1. get_person_info("person_026", "person_026_1761447798.png")
2. Check _cache → Found with status="scraping"
3. Check if polling active → Start if not active
4. Return cached PersonInfo (fast)
5. Compare with tracker → status same, skip update
```

### Background (Polling Thread Running):
```
Poll #1 (after 1 second):
   → Query Supabase
   → Find record with full_name="John Doe" and data
   → Generate LLM summary
   → Update _cache with status="completed"
   → Update face_tracker.registry with status="completed"  ← KEY FIX!
   → Stop polling
```

### Frame N+30 (1 second later):
```
1. get_person_info("person_026", "person_026_1761447798.png")
2. Check _cache → Found with status="completed"  ← UPDATED!
3. Return PersonInfo with LLM summary
4. Compare with tracker → status CHANGED!
5. Update tracker with new data
6. Display shows completed info with summary!
```

## Why This Fixes the Issue:

1. **Always calls API**: No longer skipped for `api_called=True` faces
2. **Polling always active**: `get_person_info()` ensures polling runs for "scraping" status
3. **Both caches updated**: Polling updates both API cache and face_tracker
4. **Display refreshes**: When status changes, tracker updates and display shows new data

## Testing:

Run the app and you should now see:

```
💾 [DEBUG] Querying Supabase for: person_026_1761447798.png
   Results found: 1
   ✅ Found record:
      - Full name: [name]
      - Social media: True
      - Nyne AI response: True

🤖 [DEBUG] Generating LLM summary for person_026
   ⏳ Calling Ollama...
   ✅ LLM response received

🔄 [DEBUG] Poll attempt #1 for person_026
   Poll result: status=completed
   ✅ Cache updated for person_026
   ✅ Face tracker updated for person_026

🎨 [DEBUG] Formatting display for person
   Status: completed
   Full name: [Name]
   → Displaying completed status with name: [Name]
```

The display will update from "🔍 Scraping..." to showing the actual person information!

