# Person Info Integration - Test Guide

## Quick Test Checklist

### ✅ Test 1: Scraping State (No Data Yet)

**Setup:**
1. Delete or empty the `face_searches` table in Supabase
2. Run the face recognition system

**Expected behavior:**
```bash
cd /Users/vikra/past/face_recognition
python main.py
```

When you show your face:
- Face gets detected and saved
- Image uploads to Supabase
- Info box shows:
  ```
  🔍 Scraping...
  Fetching person info
  ```
- Console shows:
  ```
  ⚠️  No data found for person_XXX yet
  ```
- System polls every 1 second (check console for polling activity)

**Pass criteria:**
- ✅ "Scraping..." message displays
- ✅ No crashes or errors
- ✅ Polling continues in background

---

### ✅ Test 2: Data Becomes Available

**Setup:**
1. While system is running and showing "Scraping..."
2. Add test data to Supabase `face_searches` table

**SQL to insert test data:**
```sql
INSERT INTO face_searches (trigger_image_url, nyne_response)
VALUES (
  'person_001_1761435966.png',  -- Use actual filename from detected_faces/
  '{
    "success": true,
    "data": {
      "status": "completed",
      "result": {
        "displayname": "Test User",
        "bio": "This is a test person for verification",
        "location": "San Francisco, CA",
        "gender": "Male",
        "fullphone": [{"fullphone": "(555) 123-4567"}],
        "altemails": ["test@example.com"],
        "organizations": [
          {
            "name": "Test Company",
            "title": "Software Engineer"
          }
        ],
        "school_info": [
          {
            "name": "Test University",
            "degree": "BS",
            "title": "Computer Science"
          }
        ],
        "social_profiles": {
          "linkedin": {
            "url": "https://www.linkedin.com/in/testuser",
            "username": "testuser"
          }
        }
      }
    }
  }'::jsonb
);
```

**Expected behavior:**
- Within 1 second, info box updates
- Shows:
  ```
  Test User
  This is a test person for verification
  📍 San Francisco, CA | Male
  📧 test@example.com
  📞 (555) 123-4567
  
  💼 Software Engineer
     Test Company
  🎓 BS in Computer Science
  💼 Linkedin: testuser
  ```
- Console shows:
  ```
  ✅ Person info ready for person_001: Test User
  ```

**Pass criteria:**
- ✅ Display updates automatically (no restart needed)
- ✅ All fields shown correctly
- ✅ Polling stops after data found
- ✅ No duplicate API calls

---

### ✅ Test 3: Pre-populated Data

**Setup:**
1. Have test data already in database
2. Restart face recognition system
3. Show face that matches existing data

**Expected behavior:**
- First query finds data immediately
- Shows person info right away (no "Scraping..." state)
- No polling thread starts
- Data cached for subsequent detections

**Pass criteria:**
- ✅ Instant display of person info
- ✅ No scraping message shown
- ✅ No unnecessary polling

---

### ✅ Test 4: Missing Fields (Partial Data)

**Setup:**
Insert data with some fields missing:

```sql
INSERT INTO face_searches (trigger_image_url, nyne_response)
VALUES (
  'person_002_1761435970.png',
  '{
    "data": {
      "status": "completed",
      "result": {
        "displayname": "Minimal User"
      }
    }
  }'::jsonb
);
```

**Expected behavior:**
- Shows only available fields:
  ```
  Minimal User
  ```
- No crashes or errors for missing fields
- Clean display without empty sections

**Pass criteria:**
- ✅ Handles missing fields gracefully
- ✅ No error messages for missing data
- ✅ Display looks clean

---

### ✅ Test 5: Timeout Test

**Setup:**
1. Clear database
2. Run system
3. Let it run for >5 minutes without adding data

**Expected behavior:**
- Shows "Scraping..." for first 5 minutes
- After 5 minutes:
  ```
  ⏱️  Polling timeout for person_XXX
  ```
- Polling stops
- Still shows "Scraping..." message (no update)

**Pass criteria:**
- ✅ Polling stops after timeout
- ✅ No infinite polling
- ✅ No memory leaks from threads

---

### ✅ Test 6: Multiple People

**Setup:**
1. Have data for multiple people in database
2. Show different faces sequentially

**Expected behavior:**
- Each person gets their own data
- No data mixing between people
- Independent polling for each if needed
- Correct matching by filename

**Pass criteria:**
- ✅ Correct data for each person
- ✅ No cross-contamination
- ✅ Multiple polling threads work simultaneously

---

## Debug Console Output

### Successful Flow
```
✅ Supabase Storage initialized
✅ Bucket 'detected-faces' exists
📸 Starting quality collection (0/5 frames)
...
✅ Best frame selected: Sharpness = 156.3
New face detected and saved: person_001_1761435966.png
   Supabase URL: https://...
✅ Person info ready for person_001: John Smith
```

### Scraping Flow
```
⚠️  No data found for person_001 yet
[Wait 1 second]
⚠️  No data found for person_001 yet
[Wait 1 second]
✅ Person info ready for person_001: John Smith
```

### Error Cases
```
⚠️  Supabase client not initialized
⚠️  Error querying face_searches: [error details]
⚠️  Error parsing Nyne response: [error details]
⚠️  Polling error for person_001: [error details]
⏱️  Polling timeout for person_001
```

---

## Configuration Tuning

### Adjust polling speed

**Faster polling (0.5 seconds):**
```python
# config.py
PERSON_INFO_POLL_INTERVAL = 0.5
```

**Slower polling (2 seconds):**
```python
PERSON_INFO_POLL_INTERVAL = 2.0
```

### Adjust timeout

**Shorter timeout (2 minutes):**
```python
PERSON_INFO_MAX_POLL_TIME = 120
```

**Longer timeout (10 minutes):**
```python
PERSON_INFO_MAX_POLL_TIME = 600
```

### Disable person info feature

```python
ENABLE_PERSON_INFO_API = False
```

---

## Troubleshooting

### Issue: Always shows "Scraping..."

**Possible causes:**
1. No data in `face_searches` table
2. `trigger_image_url` doesn't match filename
3. `nyne_response` format is wrong
4. `data.status` is not "completed"

**Debug:**
```sql
-- Check if data exists
SELECT * FROM face_searches 
WHERE trigger_image_url LIKE '%person_001_%';

-- Check nyne_response structure
SELECT 
  trigger_image_url,
  nyne_response->'data'->>'status' as status
FROM face_searches;
```

### Issue: Wrong person info shown

**Cause:** Filename mismatch in database

**Fix:** Ensure `trigger_image_url` contains exact filename:
```sql
UPDATE face_searches 
SET trigger_image_url = 'person_001_1761435966.png'
WHERE id = [row_id];
```

### Issue: Polling doesn't stop

**Check console for:**
- Timeout messages
- Parse errors
- Database connection issues

**Manual stop:**
```python
# In Python console or code
from person_info import get_api_instance
api = get_api_instance()
api.stop_polling()  # Stop all
```

### Issue: Display looks wrong

**Check:**
- Info box position in config: `INFO_DISPLAY_POSITION`
- Font scales: `INFO_FONT_SCALE_*`
- Box dimensions: `INFO_BOX_*` settings

---

## Performance Monitoring

### Check polling activity

Add debug logging:
```python
# Temporarily in person_info.py poll_worker()
print(f"🔄 Polling {person_id}... (attempt {attempt})")
```

### Monitor thread count

```python
import threading
print(f"Active threads: {threading.active_count()}")
```

### Check cache size

```python
api = get_api_instance()
print(f"Cached entries: {len(api._cache)}")
print(f"Active polling: {len([p for p, active in api._polling_active.items() if active])}")
```

---

## Success Criteria Summary

System is working correctly if:

1. ✅ "Scraping..." shows when no data available
2. ✅ Display updates automatically when data added
3. ✅ Polling stops after data found or timeout
4. ✅ All available fields display correctly
5. ✅ Missing fields handled gracefully
6. ✅ Multiple people tracked independently
7. ✅ No memory leaks or infinite loops
8. ✅ Performance remains smooth during polling

Ready to test! 🧪

