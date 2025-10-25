# Supabase Storage Integration

## Overview

Every time a new face is detected, it is automatically:
1. Saved locally with format: `person_XXX_{timestamp}.png`
2. Uploaded to Supabase storage bucket
3. Logged in the face registry with Supabase URL

## Setup

### 1. Install Dependencies

```bash
cd /Users/vikra/past/face_recognition
pip install supabase
```

### 2. Supabase Configuration

Already configured in `config.py`:

```python
SUPABASE_URL = "https://afwpcbmhvjwrnolhrocz.supabase.co"
SUPABASE_SERVICE_KEY = "your-service-role-key"
SUPABASE_BUCKET_NAME = "detected-faces"
ENABLE_SUPABASE_UPLOAD = True
```

### 3. Create Storage Bucket (First Time)

The system will automatically attempt to create the bucket `detected-faces` if it doesn't exist.

Or manually create it in Supabase Dashboard:
1. Go to https://supabase.com/dashboard
2. Select your project
3. Storage → New Bucket
4. Name: `detected-faces`
5. Public: No (keep private)

## How It Works

### File Naming Convention

**Old format**: `person_001.jpg`  
**New format**: `person_001_1729881234.png`

- `person_001`: Sequential person ID
- `1729881234`: Unix timestamp
- `.png`: PNG format for better quality

### Automatic Upload Flow

1. **Face detected** → System checks if it's a duplicate
2. **New face** → Saves locally with timestamp
3. **Upload** → Sends to Supabase storage at `faces/person_XXX_{timestamp}.png`
4. **Registry updated** → Stores Supabase URL in `face_registry.json`

### Example Console Output

```
New face detected and saved: person_005 (person_005_1729881234.png)
✅ Uploaded to Supabase: faces/person_005_1729881234.png
   Supabase URL: https://afwpcbmhvjwrnolhrocz.supabase.co/storage/v1/object/public/detected-faces/faces/person_005_1729881234.png
```

## Files Modified

### Created Files
- `supabase_storage.py` - Supabase storage integration
- `SUPABASE_INTEGRATION.md` - This guide

### Modified Files
- `face_tracker.py`:
  - Added timestamp to filenames
  - Changed format from JPG to PNG
  - Added Supabase upload after saving
  - Stores Supabase URL in registry
  
- `config.py`:
  - Added Supabase URL and keys
  - Added bucket name
  - Added enable/disable flag

- `requirements.txt`:
  - Added `supabase>=2.0.0`

## Registry Entry Example

```json
{
  "person_005": {
    "id": "person_005",
    "first_seen": "2025-10-25T14:30:34.560000",
    "last_seen": "2025-10-25T14:30:34.560000",
    "image_path": "detected_faces/person_005_1729881234.png",
    "image_filename": "person_005_1729881234.png",
    "timestamp": 1729881234,
    "supabase_url": "https://afwpcbmhvjwrnolhrocz.supabase.co/storage/v1/object/public/detected-faces/faces/person_005_1729881234.png",
    "encoding_hash": "a1b2c3d4e5f6g7h8",
    "detection_count": 1,
    "person_info": null,
    "api_called": false
  }
}
```

## Storage Structure in Supabase

```
detected-faces/           (bucket)
└── faces/
    ├── person_001_1729881234.png
    ├── person_002_1729881456.png
    ├── person_003_1729881678.png
    └── ...
```

## Features

### ✅ Automatic Upload
Every new face is automatically uploaded to Supabase.

### ✅ Duplicate Prevention
Uses face encoding comparison to avoid uploading the same person multiple times.

### ✅ Timestamp Tracking
Each file has a unique timestamp in the filename.

### ✅ URL Storage
Supabase URLs are stored in the registry for easy access.

### ✅ Error Handling
Gracefully handles upload failures without breaking face detection.

### ✅ Local Backup
All faces are saved locally AND in Supabase (redundancy).

## Accessing Uploaded Images

### Via Supabase Dashboard
1. Go to https://supabase.com/dashboard
2. Select your project
3. Storage → detected-faces
4. Browse `faces/` folder

### Via URL
Each image has a public URL stored in the registry:
```
https://afwpcbmhvjwrnolhrocz.supabase.co/storage/v1/object/public/detected-faces/faces/person_XXX_timestamp.png
```

### Via API
```python
from supabase_storage import SupabaseStorage

storage = SupabaseStorage()
files = storage.list_files("faces/")
print(files)
```

## Troubleshooting

### Bucket Not Found
```
⚠️  Bucket 'detected-faces' not found
   Creating bucket...
✅ Bucket 'detected-faces' created
```
The system automatically creates the bucket if missing.

### Upload Failed
```
❌ Failed to upload to Supabase: [error details]
```
**Solutions**:
- Check internet connection
- Verify Supabase credentials in `config.py`
- Check bucket exists and is accessible
- Verify service role key has storage permissions

### Supabase Client Not Initialized
```
⚠️  Supabase client not initialized
```
**Solutions**:
- Install supabase package: `pip install supabase`
- Check credentials in `config.py`
- Verify Supabase URL is correct

## Configuration Options

### Disable Supabase Upload
Edit `config.py`:
```python
ENABLE_SUPABASE_UPLOAD = False
```

This will:
- Still save faces locally
- Skip Supabase upload
- Useful for testing without internet

### Change Bucket Name
Edit `config.py`:
```python
SUPABASE_BUCKET_NAME = "my-custom-bucket"
```

### Use Anon Key Instead of Service Key
For less privileged operations:
```python
SUPABASE_SERVICE_KEY = config.SUPABASE_ANON_KEY
```

## Security Notes

### Service Role Key
- Has full access to your Supabase project
- Keep it secure (don't commit to public repos)
- Use environment variables in production:

```python
import os
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
```

### Bucket Permissions
- Bucket is set to private by default
- Only accessible via authenticated API calls
- Public access requires explicit configuration

## Performance

### Upload Speed
- Typical upload: ~100-500ms per image
- PNG files: ~50-200KB each
- Non-blocking (doesn't slow down face detection)

### Storage Limits
- Free tier: 1GB storage
- Pro tier: 100GB+ available
- Monitor usage in Supabase dashboard

## Benefits

1. **Cloud Backup**: All detected faces automatically backed up
2. **Access Anywhere**: View faces from any device
3. **Collaboration**: Share bucket access with team
4. **Scalability**: Supabase handles storage management
5. **Redundancy**: Local + cloud storage
6. **Timestamps**: Easy to track when faces were detected
7. **Organized**: All faces in one centralized location

## Next Steps

1. Install package: `pip install supabase`
2. Run the app: `python main.py`
3. Detect faces → automatically uploaded!
4. Check Supabase dashboard to see uploads

---

**All set!** Every new face will now be saved with timestamps and automatically uploaded to Supabase! 🎉☁️

