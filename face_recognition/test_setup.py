#!/usr/bin/env python3
"""
Test script to verify the face recognition system setup.
"""
import sys
import importlib


def test_import(module_name):
    """Test if a module can be imported."""
    try:
        importlib.import_module(module_name)
        print(f"✓ {module_name}")
        return True
    except ImportError as e:
        print(f"✗ {module_name}: {e}")
        return False


def test_camera():
    """Test if camera is accessible."""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        ret = cap.isOpened()
        cap.release()
        if ret:
            print("✓ Camera accessible")
            return True
        else:
            print("✗ Camera not accessible")
            return False
    except Exception as e:
        print(f"✗ Camera test failed: {e}")
        return False


def main():
    """Run all setup tests."""
    print("=" * 60)
    print("Face Recognition System - Setup Test")
    print("=" * 60)
    
    print("\n1. Testing Python modules...")
    modules = [
        'cv2',
        'face_recognition',
        'mediapipe',
        'numpy',
        'PIL'
    ]
    
    module_results = [test_import(m) for m in modules]
    
    print("\n2. Testing project modules...")
    project_modules = [
        'config',
        'utils',
        'stream_handler',
        'event_logger',
        'face_database',
        'face_engine'
    ]
    
    project_results = [test_import(m) for m in project_modules]
    
    print("\n3. Testing camera access...")
    camera_result = test_camera()
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    all_passed = all(module_results) and all(project_results) and camera_result
    
    total_tests = len(modules) + len(project_modules) + 1
    passed_tests = sum(module_results) + sum(project_results) + int(camera_result)
    
    print(f"Passed: {passed_tests}/{total_tests}")
    
    if all_passed:
        print("\n✓ All tests passed! System is ready to use.")
        print("\nRun the application with:")
        print("  python main.py")
        return 0
    else:
        print("\n✗ Some tests failed. Please install missing dependencies:")
        print("  pip install -r requirements.txt")
        
        if not camera_result:
            print("\nCamera issues:")
            print("  - Check if camera is connected")
            print("  - Grant camera permissions")
            print("  - Try different camera index (--source 1)")
        
        return 1


if __name__ == '__main__':
    sys.exit(main())

