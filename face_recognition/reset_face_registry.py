#!/usr/bin/env python3
"""
Utility to reset the face registry and start fresh.
Useful if faces were incorrectly grouped together.
"""
import os
import json
import shutil
from datetime import datetime
import config


def backup_registry():
    """Create a backup of the current registry."""
    if os.path.exists(config.FACE_REGISTRY_FILE):
        backup_name = f"face_registry_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = os.path.join(config.DATA_DIR, backup_name)
        shutil.copy2(config.FACE_REGISTRY_FILE, backup_path)
        print(f"✅ Backup created: {backup_path}")
        return backup_path
    return None


def reset_registry():
    """Reset the face registry."""
    print("\n🔄 Resetting Face Registry")
    print("=" * 50)
    
    # Backup current registry
    backup_path = backup_registry()
    
    # Clear registry file
    with open(config.FACE_REGISTRY_FILE, 'w') as f:
        json.dump({}, f, indent=2)
    
    print(f"✅ Registry cleared: {config.FACE_REGISTRY_FILE}")
    print(f"   Previous data backed up to: {backup_path}")
    
    # Optionally clear detected faces
    print("\n⚠️  Detected faces in {config.DETECTED_FACES_DIR} are kept.")
    print("   To remove them manually: rm -rf detected_faces/*")


def list_tracked_faces():
    """List all currently tracked faces."""
    if not os.path.exists(config.FACE_REGISTRY_FILE):
        print("No registry file found")
        return
    
    with open(config.FACE_REGISTRY_FILE, 'r') as f:
        registry = json.load(f)
    
    print("\n📋 Currently Tracked Faces")
    print("=" * 50)
    
    for person_id, data in sorted(registry.items()):
        print(f"\n{person_id}:")
        print(f"  First seen: {data.get('first_seen', 'N/A')}")
        print(f"  Detection count: {data.get('detection_count', 0)}")
        print(f"  Image: {data.get('image_filename', 'N/A')}")
        if data.get('supabase_url'):
            print(f"  Supabase: ✅")


def main():
    import sys
    
    print("\n" + "=" * 50)
    print("Face Registry Management")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        list_tracked_faces()
        return
    
    list_tracked_faces()
    
    print("\n\n⚠️  WARNING: This will reset the face registry!")
    print("All tracked faces will be cleared (backup will be created).")
    print("Detected face images will be kept but associations will be lost.")
    
    response = input("\nDo you want to continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        reset_registry()
        print("\n✅ Reset complete! Run main.py to start fresh.")
    else:
        print("\n❌ Reset cancelled.")


if __name__ == '__main__':
    main()

