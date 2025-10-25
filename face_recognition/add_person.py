#!/usr/bin/env python3
"""
Utility script to add a new person to the face database.
"""
import sys
import os
import argparse
from face_database import FaceDatabase


def main():
    parser = argparse.ArgumentParser(
        description='Add a person to the face recognition database'
    )
    
    parser.add_argument(
        'name',
        type=str,
        help='Name of the person'
    )
    
    parser.add_argument(
        'image_path',
        type=str,
        help='Path to the face image'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save to known_faces directory'
    )
    
    args = parser.parse_args()
    
    # Check if image exists
    if not os.path.exists(args.image_path):
        print(f"Error: Image file not found: {args.image_path}")
        return 1
    
    # Initialize database
    print(f"Adding {args.name} to face database...")
    db = FaceDatabase()
    
    # Add face
    success = db.add_face(
        args.image_path,
        args.name,
        save_to_database=not args.no_save
    )
    
    if success:
        print(f"✓ Successfully added {args.name}")
        print(f"  Total faces in database: {db.get_face_count()}")
        print(f"  Total people: {len(db.get_people_list())}")
        return 0
    else:
        print(f"✗ Failed to add {args.name}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

