"""
Live camera preview with detection
Press 'q' to quit, 's' to save screenshot
"""

import cv2
import logging
from vision.camera import Camera
from vision.detector import ObjectDetector

logging.basicConfig(level=logging.INFO)

print("=" * 60)
print("LIVE CAMERA PREVIEW WITH DETECTION")
print("=" * 60)
print("\nControls:")
print("  - Press 'q' to quit")
print("  - Press 's' to save screenshot")
print("  - Press 'd' to toggle detection")
print("\nStarting camera...")

camera = Camera()
detector = ObjectDetector(confidence=0.25)

if not camera.open():
    print("❌ Failed to open camera!")
    exit(1)

print("✅ Camera opened")
print("Loading YOLO model...")

if not detector.load_model():
    print("❌ Failed to load model!")
    exit(1)

print("✅ Model loaded")
print("\n▶️  Press 'q' in the preview window to quit\n")

show_detection = True
frame_count = 0

try:
    while True:
        frame = camera.capture_frame()
        
        if frame is None:
            print("⚠️  Failed to capture frame")
            continue
        
        display_frame = frame.copy()
        
        # Run detection every 5 frames (for performance)
        if show_detection and frame_count % 5 == 0:
            detections = detector.detect(frame, verbose=False)
            
            if detections:
                display_frame = detector.draw_detections(frame, detections)
                
                # Show count on screen
                people_count = len([d for d in detections if d['class'] == 'person'])
                total_count = len(detections)
                
                text = f"People: {people_count} | Objects: {total_count}"
                cv2.putText(display_frame, text, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Show instructions
        instructions = "q=quit | s=save | d=toggle detection"
        cv2.putText(display_frame, instructions, (10, display_frame.shape[0] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow('Jheevis Camera Preview', display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            print("\n👋 Quitting...")
            break
        elif key == ord('s'):
            filename = f'screenshot_{frame_count}.jpg'
            cv2.imwrite(filename, display_frame)
            print(f"📸 Saved: {filename}")
        elif key == ord('d'):
            show_detection = not show_detection
            status = "ON" if show_detection else "OFF"
            print(f"🔄 Detection: {status}")
        
        frame_count += 1

except KeyboardInterrupt:
    print("\n\n⚠️  Interrupted by user")

finally:
    camera.close()
    cv2.destroyAllWindows()
    print("✅ Camera closed")
