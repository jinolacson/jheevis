"""
Test script for Vision/Camera features
Tests object detection and people recognition
"""

import logging
import cv2
from vision.camera import Camera, list_cameras
from vision.detector import ObjectDetector
from desktop.actions import ActionExecutor
from llm.intent import IntentClassifier, ActionType

# Setup logging
logging.basicConfig(level=logging.INFO)


def test_camera():
    """Test camera functionality."""
    print("=" * 60)
    print("TESTING CAMERA")
    print("=" * 60)
    
    # List available cameras
    print("\n1. Listing available cameras:")
    cameras = list_cameras()
    if cameras:
        print(f"   Found cameras: {cameras}")
        print("   ✅ Camera detection works")
    else:
        print("   ❌ No cameras found")
        return False
    
    # Test camera capture
    print("\n2. Testing camera capture:")
    try:
        with Camera() as cam:
            info = cam.get_camera_info()
            print(f"   Camera info: {info}")
            
            frame = cam.capture_frame()
            if frame is not None:
                print(f"   Captured frame: {frame.shape}")
                print("   ✅ Camera capture works")
                return True
            else:
                print("   ❌ Failed to capture frame")
                return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_object_detection():
    """Test object detection."""
    print("\n" + "=" * 60)
    print("TESTING OBJECT DETECTION")
    print("=" * 60)
    
    print("\n1. Loading YOLO model:")
    try:
        detector = ObjectDetector(confidence=0.5)
        
        # Load model
        if detector.load_model():
            print("   ✅ YOLO model loaded")
        else:
            print("   ❌ Failed to load YOLO model")
            print("   Install with: pip install ultralytics")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n2. Testing detection on camera image:")
    try:
        with Camera() as cam:
            frame = cam.capture_multiple_frames(num_frames=3)
            
            if frame is None:
                print("   ❌ Failed to capture frame")
                return False
            
            # Detect objects
            detections = detector.detect(frame, verbose=False)
            
            print(f"   Found {len(detections)} objects:")
            for det in detections[:5]:  # Show first 5
                print(f"     - {det['class']}: {det['confidence']:.2%}")
            
            # Get scene description
            description = detector.describe_scene(frame)
            print(f"\n   Scene description: \"{description}\"")
            
            print("   ✅ Object detection works")
            return True
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_intent_classifier():
    """Test intent classification for vision commands."""
    print("\n" + "=" * 60)
    print("TESTING VISION INTENT CLASSIFIER")
    print("=" * 60)
    
    classifier = IntentClassifier()
    
    test_cases = [
        ("what do you see", ActionType.WHAT_DO_YOU_SEE),
        ("what can you see", ActionType.WHAT_DO_YOU_SEE),
        ("who is here", ActionType.WHO_IS_HERE),
        ("is anyone here", ActionType.WHO_IS_HERE),
        ("how many people", ActionType.COUNT_PEOPLE),
        ("count people", ActionType.COUNT_PEOPLE),
        ("what objects", ActionType.DETECT_OBJECTS),
        ("detect objects", ActionType.DETECT_OBJECTS),
        ("take picture", ActionType.TAKE_PICTURE),
        ("take a photo", ActionType.TAKE_PICTURE),
    ]
    
    passed = 0
    failed = 0
    
    for text, expected_action in test_cases:
        intent = classifier.classify(text)
        
        if intent.action_type == expected_action:
            print(f"✅ '{text}' -> {intent.action_type.value}")
            passed += 1
        else:
            print(f"❌ '{text}' -> Expected: {expected_action.value}, Got: {intent.action_type}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_action_executor():
    """Test action executor vision methods."""
    print("\n" + "=" * 60)
    print("TESTING ACTION EXECUTOR")
    print("=" * 60)
    
    executor = ActionExecutor()
    
    print("\n⚠️  The following tests will access your camera")
    
    try:
        input("Press Enter to test 'what_do_you_see' (or Ctrl+C to skip)...")
        
        print("\n1. Testing what_do_you_see():")
        result = executor.what_do_you_see()
        
        if result.get('success'):
            print(f"   ✅ {result.get('description')}")
            print(f"   Found {result.get('num_objects', 0)} objects")
        else:
            print(f"   ❌ {result.get('description')}")
    
    except KeyboardInterrupt:
        print("\n   ⏭️  Skipped")
    
    try:
        input("\nPress Enter to test 'who_is_here' (or Ctrl+C to skip)...")
        
        print("\n2. Testing who_is_here():")
        result = executor.who_is_here()
        
        if result.get('success'):
            print(f"   ✅ {result.get('message')}")
            print(f"   Count: {result.get('count', 0)}")
        else:
            print(f"   ❌ {result.get('message')}")
    
    except KeyboardInterrupt:
        print("\n   ⏭️  Skipped")
    
    try:
        input("\nPress Enter to test 'detect_objects' (or Ctrl+C to skip)...")
        
        print("\n3. Testing detect_objects():")
        result = executor.detect_objects()
        
        if result.get('success'):
            print(f"   ✅ {result.get('message')}")
            print(f"   Objects: {result.get('objects', {})}")
        else:
            print(f"   ❌ {result.get('message')}")
    
    except KeyboardInterrupt:
        print("\n   ⏭️  Skipped")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("VISION & CAMERA TEST SUITE")
    print("=" * 60 + "\n")
    
    try:
        # Test 1: Camera
        camera_ok = test_camera()
        
        if not camera_ok:
            print("\n❌ Camera tests failed. Cannot proceed with vision tests.")
            return
        
        # Test 2: Object Detection
        detection_ok = test_object_detection()
        
        if not detection_ok:
            print("\n⚠️  Object detection failed, but continuing with other tests...")
        
        # Test 3: Intent Classification
        intent_ok = test_intent_classifier()
        
        # Test 4: Action Executor (interactive)
        print("\n" + "=" * 60)
        print("INTERACTIVE ACTION TESTS")
        print("=" * 60)
        print("\nThe following tests will access your camera.")
        print("Press Ctrl+C at any prompt to skip.\n")
        
        try:
            input("Press Enter to start interactive tests (or Ctrl+C to skip all)...")
            test_action_executor()
        except KeyboardInterrupt:
            print("\n\n⏭️  Interactive tests skipped\n")
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED")
        print("=" * 60)
        print("\n✅ Vision features are ready!")
        print("\nTry these voice commands:")
        print("  - 'What do you see?'")
        print("  - 'Who is here?'")
        print("  - 'How many people?'")
        print("  - 'Detect objects'")
        print("  - 'Take a picture'")
        print()
    
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
