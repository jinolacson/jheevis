"""
Object Detection module
Detects objects and people using YOLO
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
import cv2

logger = logging.getLogger(__name__)


class ObjectDetector:
    """
    Object detector using YOLO (Ultralytics).
    Detects people, objects, and provides scene descriptions.
    """
    
    def __init__(self, model_path: Optional[str] = None, confidence: float = 0.5):
        """
        Initialize object detector.
        
        Args:
            model_path: Path to YOLO model (default: yolo11n.pt)
            confidence: Minimum confidence threshold (0.0-1.0)
        """
        self.confidence = confidence
        self.model = None
        self.model_loaded = False
        
        # Set default model path
        if model_path is None:
            # Try to find YOLO model in common locations
            possible_paths = [
                Path(__file__).parent.parent / "yolo11n.pt",
                Path(__file__).parent.parent / "AI-Systems" / "yolo11n.pt",
                Path.home() / "Projects" / "AI-Systems" / "yolo11n.pt",
            ]
            
            for path in possible_paths:
                if path.exists():
                    model_path = str(path)
                    break
        
        self.model_path = model_path
        logger.info(f"ObjectDetector initialized (model: {model_path}, conf: {confidence})")
    
    def load_model(self) -> bool:
        """
        Load YOLO model.
        
        Returns:
            True if successful
        """
        if self.model_loaded:
            return True
        
        try:
            from ultralytics import YOLO
            
            if self.model_path and Path(self.model_path).exists():
                logger.info(f"Loading YOLO model from {self.model_path}")
                self.model = YOLO(self.model_path)
            else:
                logger.info("Downloading YOLO11n model...")
                self.model = YOLO("yolo11n.pt")
            
            self.model_loaded = True
            logger.info("YOLO model loaded successfully")
            return True
        
        except ImportError:
            logger.error("Ultralytics package not installed. Install with: pip install ultralytics")
            return False
        except Exception as e:
            logger.error(f"Error loading YOLO model: {e}")
            return False
    
    def detect(self, image: np.ndarray, verbose: bool = False) -> List[Dict[str, Any]]:
        """
        Detect objects in an image.
        
        Args:
            image: Image as numpy array (BGR format)
            verbose: Print detection details
        
        Returns:
            List of detected objects with class, confidence, and bbox
        """
        if not self.model_loaded:
            if not self.load_model():
                return []
        
        try:
            # Run detection
            results = self.model(image, conf=self.confidence, verbose=verbose)
            
            detections = []
            
            for result in results:
                boxes = result.boxes
                
                for box in boxes:
                    # Get box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # Get class and confidence
                    cls_id = int(box.cls[0].cpu().numpy())
                    conf = float(box.conf[0].cpu().numpy())
                    class_name = result.names[cls_id]
                    
                    detection = {
                        'class': class_name,
                        'confidence': conf,
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'class_id': cls_id
                    }
                    
                    detections.append(detection)
            
            return detections
        
        except Exception as e:
            logger.error(f"Error during detection: {e}")
            return []
    
    def detect_people(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect only people in an image.
        
        Args:
            image: Image as numpy array
        
        Returns:
            List of detected people
        """
        all_detections = self.detect(image)
        people = [d for d in all_detections if d['class'] == 'person']
        return people
    
    def describe_scene(self, image: np.ndarray, detailed: bool = False) -> str:
        """
        Generate a natural language description of the scene.
        
        Args:
            image: Image as numpy array
            detailed: Include detailed information
        
        Returns:
            Description string
        """
        detections = self.detect(image)
        
        if not detections:
            return "I don't see anything clearly recognizable."
        
        # Count objects by class
        class_counts = {}
        for det in detections:
            cls = det['class']
            class_counts[cls] = class_counts.get(cls, 0) + 1
        
        # Build description
        parts = []
        
        # People first (most important)
        if 'person' in class_counts:
            count = class_counts['person']
            if count == 1:
                parts.append("I see one person")
            else:
                parts.append(f"I see {count} people")
            del class_counts['person']
        
        # Other objects
        if class_counts:
            objects = []
            for cls, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
                if count == 1:
                    objects.append(f"a {cls}")
                else:
                    objects.append(f"{count} {cls}s")
            
            if parts:
                if len(objects) == 1:
                    parts.append(f"and {objects[0]}")
                else:
                    parts.append(f"and {', '.join(objects)}")
            else:
                parts.append(f"I see {', '.join(objects)}")
        
        description = ' '.join(parts)
        
        if detailed:
            # Add confidence information
            avg_conf = sum(d['confidence'] for d in detections) / len(detections)
            description += f". Average confidence: {avg_conf:.1%}"
        
        return description
    
    def count_people(self, image: np.ndarray) -> int:
        """
        Count number of people in image.
        
        Args:
            image: Image as numpy array
        
        Returns:
            Number of people detected
        """
        people = self.detect_people(image)
        return len(people)
    
    def is_person_present(self, image: np.ndarray) -> bool:
        """
        Check if at least one person is present.
        
        Args:
            image: Image as numpy array
        
        Returns:
            True if person detected
        """
        return self.count_people(image) > 0
    
    def draw_detections(self, image: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
        """
        Draw bounding boxes and labels on image.
        
        Args:
            image: Image as numpy array
            detections: List of detections
        
        Returns:
            Image with drawn detections
        """
        output = image.copy()
        
        for det in detections:
            # Get coordinates
            x1, y1, x2, y2 = det['bbox']
            
            # Color based on class (person = green, others = blue)
            color = (0, 255, 0) if det['class'] == 'person' else (255, 0, 0)
            
            # Draw box
            cv2.rectangle(output, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{det['class']} {det['confidence']:.2f}"
            cv2.putText(output, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return output
    
    def get_object_counts(self, image: np.ndarray) -> Dict[str, int]:
        """
        Get count of each object type.
        
        Args:
            image: Image as numpy array
        
        Returns:
            Dictionary with class names and counts
        """
        detections = self.detect(image)
        
        counts = {}
        for det in detections:
            cls = det['class']
            counts[cls] = counts.get(cls, 0) + 1
        
        return counts


# Convenience functions
def detect_objects(image: np.ndarray, confidence: float = 0.5) -> List[Dict[str, Any]]:
    """Quick object detection."""
    detector = ObjectDetector(confidence=confidence)
    return detector.detect(image)


def detect_people(image: np.ndarray, confidence: float = 0.5) -> List[Dict[str, Any]]:
    """Quick people detection."""
    detector = ObjectDetector(confidence=confidence)
    return detector.detect_people(image)


def describe_scene(image: np.ndarray, confidence: float = 0.5) -> str:
    """Quick scene description."""
    detector = ObjectDetector(confidence=confidence)
    return detector.describe_scene(image)
