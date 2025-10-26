#!/usr/bin/env python3
"""
Utility script to clear the result_image_urls image cache.

The image cache is stored in memory in utils.py as _image_cache.
Since it's a module-level variable, it persists across calls within
the same Python process but is cleared when the app restarts.

Usage:
    python clear_image_cache.py

Note: This only works if imported into a running Python session.
For a running face recognition app, the cache will be cleared on restart.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Clear the image cache and report results."""
    try:
        import utils
        
        # Get current cache size
        cache_size = utils.get_image_cache_size()
        
        if cache_size == 0:
            print("✅ Image cache is already empty (0 images)")
            return
        
        print(f"📊 Current cache size: {cache_size} images")
        
        # Clear the cache
        utils.clear_image_cache()
        
        # Verify it's cleared
        new_size = utils.get_image_cache_size()
        print(f"✅ Cache cleared successfully")
        print(f"📊 New cache size: {new_size} images")
        
    except Exception as e:
        print(f"❌ Error clearing cache: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

