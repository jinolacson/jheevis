"""
Quick debug script to test camera and detection
Shows what the detector sees
"""

import cv2
import logging
from vision.camera import Camera
from vision.detector import ObjectDetector

logging.basicConfig(level=logging.INFO)

print("=" * 60)
print("CAMERA & DETECTION DEBUG")
print("=" * 60)

# Test camera
print("\n1. Testing camera...")
camera = Camera()
frame = camera.capture_multiple_frames(num_frames=3)

if frame is None:
    print("❌ Failed to capture from camera!")
    exit(1)

print(f"✅ Camera working - captured frame: {frame.shape}")

# Test detection with low confidence
print("\n2. Testing detection with confidence=0.25...")
detector = ObjectDetector(confidence=0.25)

if not detector.load_model():
    print("❌ Failed to load YOLO model!")
    exit(1)

print("✅ YOLO model loaded")

# Detect with verbose output
print("\n3. Running detection...")
detections = detector.detect(frame, verbose=True)

print(f"\n📊 Detection Results:")
print(f"   Total detections: {len(detections)}")

if detections:
    print("\n   Detected objects:")
    for i, det in enumerate(detections, 1):
        print(f"   {i}. {det['class']}: {det['confidence']:.2%} at {det['bbox']}")
    
    # Count people
    people = [d for d in detections if d['class'] == 'person']
    print(f"\n   👥 People detected: {len(people)}")
    
    # Scene description
    description = detector.describe_scene(frame)
    print(f"\n   📝 Scene: \"{description}\"")
else:
    print("   ❌ No objects detected!")

# Save annotated image for debugging
print("\n4. Saving debug image...")
if detections:
    annotated = detector.draw_detections(frame, detections)
    cv2.imwrite("debug_detection.jpg", annotated)
    print("   ✅ Saved annotated image to: debug_detection.jpg")
else:
    cv2.imwrite("debug_no_detection.jpg", frame)
    print("   ⚠️  Saved raw frame to: debug_no_detection.jpg")

print("\n" + "=" * 60)
print("TIPS:")
print("  - Make sure you're 3-10 feet from camera")
print("  - Ensure good lighting")
print("  - Check if camera is pointing at you")
print("  - View saved image to see what camera sees")
print("=" * 60)

camera.close()
