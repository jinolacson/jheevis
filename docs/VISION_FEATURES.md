# Vision & Object Detection Features

## 🎯 Overview

Jheevis can now **see and understand** what's in front of the camera using computer vision and AI object detection. This allows natural interactions like "What do you see?" or "Who is here?" making the assistant truly aware of its surroundings.

---

## ✨ Features

### 1. Visual Scene Understanding
Ask Jheevis to describe what it sees, and it will identify objects and people in natural language.

**Commands:**
- "What do you see?"
- "What can you see?"
- "What's in front of you?"
- "Describe what you see"
- "Look around"

**Examples:**
```
User: "What do you see?"
Jheevis: "I see one person and a laptop"

User: "What's in front of you?"
Jheevis: "I see 2 people, a keyboard, and a monitor"

User: "Look around"
Jheevis: "I see a person, a chair, and a book"
```

---

### 2. People Detection
Detect if people are present and count them.

**Commands:**
- "Who is here?"
- "Is anyone here?"
- "Who's in the room?"
- "Is someone here?"

**Examples:**
```
User: "Who is here?"
Jheevis: "I see one person"

User: "Is anyone here?"
Jheevis: "I don't see anyone"

User: "Is someone here?"
Jheevis: "I see 3 people"
```

---

### 3. People Counting
Count the number of people visible to the camera.

**Commands:**
- "How many people?"
- "Count people"
- "How many persons?"
- "Number of people"

**Examples:**
```
User: "How many people are here?"
Jheevis: "I see 2 people"

User: "Count people"
Jheevis: "I see one person"
```

---

### 4. Object Detection
Identify and list all visible objects with counts.

**Commands:**
- "What objects do you see?"
- "Detect objects"
- "What things are visible?"
- "Identify objects"

**Examples:**
```
User: "What objects can you see?"
Jheevis: "I see one laptop, one mouse, and 2 books"

User: "Detect objects"
Jheevis: "I see a keyboard, a monitor, and a cup"
```

---

### 5. Photo Capture
Take and save photos from the camera.

**Commands:**
- "Take a picture"
- "Take a photo"
- "Capture image"
- "Take a snapshot"

**Examples:**
```
User: "Take a picture"
Jheevis: "Picture saved to jheevis_photo_20260505_143022.jpg"

User: "Take a photo"
Jheevis: "Picture saved to jheevis_photo_20260505_143045.jpg"
```

Photos are automatically saved to your Desktop with timestamps.

---

## 🏗️ Technical Implementation

### Architecture

```
┌─────────────┐
│   Camera    │ ← Webcam access (OpenCV)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Capture   │ ← Frame capture & preprocessing
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ YOLO Model  │ ← Object detection (YOLOv11)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Description │ ← Natural language generation
└─────────────┘
```

### Components

1. **vision/camera.py** - Camera management
   - Webcam access and frame capture
   - Multi-frame capture for stability
   - Camera enumeration

2. **vision/detector.py** - Object detection
   - YOLO-based object detection
   - People detection and counting
   - Scene description generation
   - Object visualization

3. **llm/intent.py** - Intent classification
   - Vision-specific intent recognition
   - Natural language command parsing

4. **desktop/actions.py** - Action execution
   - Vision action handlers
   - Camera/detector integration

---

## 📦 Installation

### Required Dependencies

```bash
# Install vision dependencies
pip install opencv-python ultralytics pillow

# Or install all requirements
pip install -r requirements.txt
```

### YOLO Model

The first time you use vision features, YOLO will automatically download the model (~10MB):

```
INFO: Downloading YOLO11n model...
```

Alternatively, if you already have a YOLO model (yolo11n.pt, yolov8n.pt, etc.), place it in:
- `/Users/jino/Projects/jheevis/yolo11n.pt`
- `/Users/jino/Projects/AI-Systems/yolo11n.pt`

---

## 🔧 Configuration

### Camera Settings

Default camera (ID 0) is used automatically. To use a different camera:

```python
from vision.camera import Camera

# Use camera ID 1
camera = Camera(camera_id=1)
```

### Detection Confidence

Adjust detection confidence threshold (default: 0.5):

```python
from vision.detector import ObjectDetector

# Higher confidence = fewer but more accurate detections
detector = ObjectDetector(confidence=0.7)

# Lower confidence = more detections but less accurate
detector = ObjectDetector(confidence=0.3)
```

---

## 🧪 Testing

### Quick Test

```bash
cd /Users/jino/Projects/jheevis
python test_vision.py
```

This will test:
- Camera access
- YOLO model loading
- Object detection
- Intent classification
- Action execution

### Manual Testing

```python
from vision.camera import Camera
from vision.detector import ObjectDetector

# Capture and detect
with Camera() as cam:
    frame = cam.capture_frame()
    
detector = ObjectDetector()
description = detector.describe_scene(frame)
print(description)
```

---

## 📝 API Reference

### Camera Class

```python
from vision.camera import Camera

camera = Camera(camera_id=0)

# Open camera
camera.open()

# Capture single frame
frame = camera.capture_frame()

# Capture multiple frames (more stable)
frame = camera.capture_multiple_frames(num_frames=3, delay=0.1)

# Get camera info
info = camera.get_camera_info()
# Returns: {'status': 'open', 'width': 640, 'height': 480, 'fps': 30}

# Close camera
camera.close()

# Or use context manager
with Camera() as cam:
    frame = cam.capture_frame()
```

### ObjectDetector Class

```python
from vision.detector import ObjectDetector

detector = ObjectDetector(confidence=0.5)

# Load model (automatic on first detection)
detector.load_model()

# Detect objects
detections = detector.detect(frame)
# Returns: [{'class': 'person', 'confidence': 0.87, 'bbox': [x1, y1, x2, y2]}, ...]

# Detect only people
people = detector.detect_people(frame)

# Count people
count = detector.count_people(frame)

# Check if person present
is_present = detector.is_person_present(frame)

# Get scene description
description = detector.describe_scene(frame)
# Returns: "I see one person and a laptop"

# Get object counts
counts = detector.get_object_counts(frame)
# Returns: {'person': 1, 'laptop': 1, 'mouse': 1}

# Draw detections on image
annotated = detector.draw_detections(frame, detections)
```

### ActionExecutor Vision Methods

```python
from desktop.actions import ActionExecutor

executor = ActionExecutor()

# What do you see
result = executor.what_do_you_see()
# Returns: {'success': True, 'description': '...', 'detections': [...]}

# Who is here
result = executor.who_is_here()
# Returns: {'success': True, 'count': 2, 'message': 'I see 2 people'}

# Count people
result = executor.count_people()

# Detect objects
result = executor.detect_objects()
# Returns: {'success': True, 'objects': {'laptop': 1, 'mouse': 1}}

# Take picture
result = executor.take_picture(save_path="/path/to/photo.jpg")
# Returns: {'success': True, 'path': '/path/to/photo.jpg'}
```

---

## 🎨 Detected Object Classes

YOLO can detect 80+ object classes including:

**People & Animals:**
- person, cat, dog, horse, bird, etc.

**Vehicles:**
- car, bicycle, motorcycle, bus, truck, etc.

**Electronics:**
- laptop, mouse, keyboard, cell phone, monitor, etc.

**Furniture:**
- chair, couch, table, bed, etc.

**Food & Kitchen:**
- cup, bowl, bottle, fork, knife, etc.

**Office:**
- book, clock, scissors, keyboard, mouse, etc.

[Full list of 80 classes available in COCO dataset]

---

## 🔒 Privacy & Security

### Camera Access
- Camera is only accessed when vision commands are used
- No continuous recording or background capture
- Camera is released after each command

### Data Storage
- No images are stored unless you use "Take a picture"
- Saved photos go to Desktop with clear timestamps
- No cloud upload - all processing is local

### Permissions
On first camera use, macOS will prompt for camera permission. Grant access to:
- Terminal (if running from terminal)
- Your preferred terminal app
- Python (if applicable)

Settings → Privacy & Security → Camera

---

## 🐛 Troubleshooting

### "Failed to open camera"
- Check camera permissions in System Settings
- Ensure no other app is using the camera
- Try different camera_id (0, 1, 2...)
- Check camera connection

### "YOLO model not found"
- Run script once to auto-download
- Or manually place yolo11n.pt in project root
- Install ultralytics: `pip install ultralytics`

### "I don't see anything clearly recognizable"
- Improve lighting conditions
- Ensure camera is not obstructed
- Lower confidence threshold
- Check if objects are in frame

### Slow detection
- Use yolo11n (nano) for speed
- Increase confidence threshold
- Reduce image resolution
- Close other applications

---

## 💡 Tips & Best Practices

1. **Lighting**: Ensure good lighting for best detection accuracy

2. **Camera Position**: Position camera to have clear view of subjects

3. **Distance**: Keep objects/people at reasonable distance (2-10 feet)

4. **Angle**: Straight-on views work better than extreme angles

5. **Multiple Captures**: The system captures 3 frames and uses the middle one for stability

6. **Confidence Tuning**: 
   - 0.3-0.5: More detections, some false positives
   - 0.5-0.7: Balanced (default)
   - 0.7-0.9: Fewer detections, high accuracy

---

## 🚀 Future Enhancements

Potential additions:
- **Face Recognition**: Identify specific people
- **Gesture Recognition**: Hand gesture commands
- **Activity Recognition**: Detect actions (sitting, standing, waving)
- **Object Tracking**: Track movement over time
- **Scene Classification**: Indoor/outdoor, room type
- **OCR**: Read text from images
- **Continuous Monitoring**: Background object detection
- **Custom Objects**: Train on custom object classes

---

## 📊 Performance

Typical performance on Apple Silicon (M1/M2/M3):
- Detection time: 50-200ms per frame
- Camera capture: 30-50ms
- Total latency: <300ms (very responsive)

---

## ✅ Summary

**Implemented:**
- ✅ Camera access and frame capture
- ✅ YOLO-based object detection  
- ✅ People detection and counting
- ✅ Scene description in natural language
- ✅ Photo capture and saving
- ✅ Intent classification for vision commands
- ✅ Integration with voice assistant
- ✅ Privacy-focused local processing

**Ready to use:**
Just say **"Hey Jheevis, what do you see?"** and let the assistant tell you what's visible!

---

## 📚 Related Documentation

- [README.md](README.md) - Main documentation
- [NEW_FEATURES.md](NEW_FEATURES.md) - All features overview
- [test_vision.py](test_vision.py) - Vision test suite

**Status:** ✅ Ready for use

**Version:** 1.0

**Date Added:** May 5, 2026
