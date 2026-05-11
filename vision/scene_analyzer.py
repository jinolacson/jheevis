"""
Enhanced Scene Understanding and Activity Recognition
Provides context-aware vision analysis beyond basic object detection
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from collections import deque
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)


@dataclass
class SceneContext:
    """Represents analyzed scene context."""
    objects: List[Dict[str, Any]]
    people_count: int
    activity: str
    relationships: List[str]
    confidence: float
    description: str
    timestamp: float


class SceneAnalyzer:
    """
    Advanced scene understanding with activity recognition and object relationships.
    Analyzes multiple frames to understand context and what's happening.
    """
    
    def __init__(self, detector, history_size: int = 10):
        """
        Initialize scene analyzer.
        
        Args:
            detector: ObjectDetector instance
            history_size: Number of frames to keep for temporal analysis
        """
        self.detector = detector
        self.history_size = history_size
        self.frame_history = deque(maxlen=history_size)
        self.context_history = deque(maxlen=history_size)
        
        # Activity keywords based on detected objects
        self.activity_patterns = {
            'working': ['laptop', 'keyboard', 'mouse', 'monitor', 'computer'],
            'eating': ['cup', 'bowl', 'fork', 'spoon', 'bottle', 'food'],
            'reading': ['book', 'laptop', 'tablet'],
            'watching': ['tv', 'monitor', 'laptop'],
            'phone_use': ['cell phone', 'phone'],
            'meeting': ['person'],  # Multiple people
            'cooking': ['oven', 'microwave', 'bowl', 'knife'],
            'relaxing': ['couch', 'bed', 'chair'],
        }
        
        # Spatial relationship keywords
        self.spatial_relations = ['next to', 'on', 'near', 'in front of', 'behind', 'above', 'below']
        
        logger.info(f"SceneAnalyzer initialized (history: {history_size} frames)")
    
    def analyze_scene(self, image: np.ndarray, use_history: bool = True) -> SceneContext:
        """
        Perform comprehensive scene analysis.
        
        Args:
            image: Image as numpy array
            use_history: Use frame history for temporal analysis
        
        Returns:
            SceneContext with full analysis
        """
        # Run object detection
        detections = self.detector.detect(image)
        
        # Store in history
        self.frame_history.append({
            'detections': detections,
            'timestamp': time.time(),
            'image_shape': image.shape
        })
        
        # Analyze current frame
        people_count = sum(1 for d in detections if d['class'] == 'person')
        
        # Recognize activity
        activity = self._recognize_activity(detections, people_count)
        
        # Determine object relationships
        relationships = self._analyze_relationships(detections, image.shape)
        
        # Generate natural description
        description = self._generate_description(detections, people_count, activity, relationships)
        
        # Calculate overall confidence
        avg_confidence = np.mean([d['confidence'] for d in detections]) if detections else 0.0
        
        # Create context
        context = SceneContext(
            objects=detections,
            people_count=people_count,
            activity=activity,
            relationships=relationships,
            confidence=avg_confidence,
            description=description,
            timestamp=time.time()
        )
        
        self.context_history.append(context)
        
        # Enhance with temporal analysis if history enabled
        if use_history and len(self.context_history) > 1:
            context = self._enhance_with_temporal_analysis(context)
        
        return context
    
    def _recognize_activity(self, detections: List[Dict[str, Any]], people_count: int) -> str:
        """
        Recognize what activity is happening based on detected objects.
        
        Args:
            detections: List of detected objects
            people_count: Number of people in scene
        
        Returns:
            Activity description
        """
        if not detections:
            return "idle"
        
        # Extract object classes
        objects = [d['class'].lower() for d in detections]
        
        # Check for specific activities
        activity_scores = {}
        
        for activity, keywords in self.activity_patterns.items():
            # Count how many keywords match
            matches = sum(1 for obj in objects if any(kw in obj for kw in keywords))
            
            # Special case for meetings (multiple people)
            if activity == 'meeting' and people_count >= 2:
                matches += 5
            
            activity_scores[activity] = matches
        
        # Get best match
        if activity_scores:
            best_activity = max(activity_scores.items(), key=lambda x: x[1])
            if best_activity[1] > 0:
                return best_activity[0]
        
        # Fallback based on people
        if people_count > 0:
            return "present"
        
        return "idle"
    
    def _analyze_relationships(self, detections: List[Dict[str, Any]], image_shape: Tuple) -> List[str]:
        """
        Analyze spatial relationships between objects.
        
        Args:
            detections: List of detected objects
            image_shape: Image dimensions (height, width, channels)
        
        Returns:
            List of relationship descriptions
        """
        relationships = []
        
        if len(detections) < 2:
            return relationships
        
        height, width = image_shape[:2]
        
        # Analyze pairwise relationships
        for i, obj1 in enumerate(detections[:10]):  # Limit to first 10 for performance
            for obj2 in detections[i+1:i+6]:  # Compare with next 5 objects
                rel = self._determine_spatial_relation(obj1, obj2, width, height)
                if rel:
                    relationships.append(rel)
        
        return relationships[:5]  # Return top 5 most relevant
    
    def _determine_spatial_relation(
        self, 
        obj1: Dict[str, Any], 
        obj2: Dict[str, Any],
        img_width: int,
        img_height: int
    ) -> Optional[str]:
        """
        Determine spatial relationship between two objects.
        
        Args:
            obj1: First object detection
            obj2: Second object detection
            img_width: Image width
            img_height: Image height
        
        Returns:
            Relationship description or None
        """
        # Get bounding box centers
        x1, y1, x2, y2 = obj1['bbox']
        center1 = ((x1 + x2) / 2, (y1 + y2) / 2)
        
        x1, y1, x2, y2 = obj2['bbox']
        center2 = ((x1 + x2) / 2, (y1 + y2) / 2)
        
        # Calculate distance
        dx = center2[0] - center1[0]
        dy = center2[1] - center1[1]
        distance = np.sqrt(dx**2 + dy**2)
        
        # Normalize by image size
        norm_dist = distance / np.sqrt(img_width**2 + img_height**2)
        
        # Only report relationships for nearby objects
        if norm_dist > 0.3:
            return None
        
        obj1_name = obj1['class']
        obj2_name = obj2['class']
        
        # Determine relationship based on position
        if abs(dy) < img_height * 0.1:  # Roughly same height
            if dx > 0:
                return f"The {obj1_name} is next to the {obj2_name}"
            else:
                return f"The {obj2_name} is next to the {obj1_name}"
        
        elif dy > img_height * 0.1:  # obj2 is below obj1
            # Check if obj2 is directly below (might be "on")
            if abs(dx) < img_width * 0.15:
                return f"The {obj2_name} is below the {obj1_name}"
        
        elif dy < -img_height * 0.1:  # obj2 is above obj1
            if abs(dx) < img_width * 0.15:
                return f"The {obj2_name} is above the {obj1_name}"
        
        return None
    
    def _generate_description(
        self,
        detections: List[Dict[str, Any]],
        people_count: int,
        activity: str,
        relationships: List[str]
    ) -> str:
        """
        Generate natural language scene description.
        
        Args:
            detections: Detected objects
            people_count: Number of people
            activity: Recognized activity
            relationships: Object relationships
        
        Returns:
            Natural description string
        """
        if not detections:
            return "I don't see anything clearly identifiable, sir."
        
        parts = []
        
        # Start with people and activity
        if people_count > 0:
            if people_count == 1:
                if activity == "working":
                    parts.append("You appear to be working")
                elif activity == "eating":
                    parts.append("You appear to be eating")
                elif activity == "reading":
                    parts.append("You appear to be reading")
                elif activity == "phone_use":
                    parts.append("You appear to be using your phone")
                else:
                    parts.append("I see you")
            else:
                parts.append(f"I see {people_count} people")
                if activity == "meeting":
                    parts.append("in what appears to be a meeting")
        
        # Add main objects
        object_counts = {}
        for det in detections:
            cls = det['class']
            if cls != 'person':  # Skip people, already mentioned
                object_counts[cls] = object_counts.get(cls, 0) + 1
        
        if object_counts:
            # Get top 3-4 objects
            top_objects = sorted(object_counts.items(), key=lambda x: x[1], reverse=True)[:4]
            
            if parts:
                if len(top_objects) == 1:
                    obj, count = top_objects[0]
                    if count == 1:
                        parts.append(f"with a {obj}")
                    else:
                        parts.append(f"with {count} {obj}s")
                else:
                    obj_list = []
                    for obj, count in top_objects:
                        if count == 1:
                            obj_list.append(f"a {obj}")
                        else:
                            obj_list.append(f"{count} {obj}s")
                    
                    if len(obj_list) > 1:
                        parts.append(f"with {', '.join(obj_list[:-1])} and {obj_list[-1]}")
                    else:
                        parts.append(f"with {obj_list[0]}")
        
        description = ' '.join(parts)
        
        # Add a relationship if available
        if relationships and len(relationships) > 0:
            description += f". {relationships[0]}"
        
        return description + "."
    
    def _enhance_with_temporal_analysis(self, current_context: SceneContext) -> SceneContext:
        """
        Enhance scene understanding using temporal analysis of frame history.
        
        Args:
            current_context: Current frame context
        
        Returns:
            Enhanced context
        """
        # Check for changes in activity over time
        recent_activities = [ctx.activity for ctx in list(self.context_history)[-5:]]
        
        # If activity is consistent, add confidence
        if len(set(recent_activities)) == 1 and len(recent_activities) >= 3:
            # Consistent activity detected
            activity = recent_activities[0]
            if activity != "idle" and activity != "present":
                # Add temporal context to description
                if "appear to be" in current_context.description:
                    current_context.description = current_context.description.replace(
                        "appear to be", "are currently"
                    )
        
        # Check for new objects appearing
        if len(self.context_history) >= 2:
            prev_objects = set(d['class'] for d in self.context_history[-2].objects)
            curr_objects = set(d['class'] for d in current_context.objects)
            
            new_objects = curr_objects - prev_objects
            if new_objects and len(new_objects) <= 2:
                obj_list = ', '.join(new_objects)
                current_context.description += f" I notice {obj_list} has appeared."
        
        return current_context
    
    def get_activity_summary(self) -> str:
        """
        Get summary of recent activity based on history.
        
        Returns:
            Activity summary
        """
        if not self.context_history:
            return "No recent activity detected."
        
        # Get recent activities
        recent = list(self.context_history)[-5:]
        
        activities = [ctx.activity for ctx in recent]
        most_common = max(set(activities), key=activities.count)
        
        if most_common == "idle":
            return "The scene appears idle, sir."
        elif most_common == "present":
            return "You are present but no specific activity detected."
        else:
            activity_name = most_common.replace('_', ' ')
            return f"You appear to be {activity_name}, sir."
    
    def clear_history(self):
        """Clear frame and context history."""
        self.frame_history.clear()
        self.context_history.clear()
        logger.info("Scene history cleared")


def test_scene_analyzer():
    """Test scene analyzer with sample detections."""
    from vision.detector import ObjectDetector
    from vision.camera import Camera
    
    # Initialize
    detector = ObjectDetector(confidence=0.25)
    analyzer = SceneAnalyzer(detector)
    camera = Camera()
    
    print("=" * 60)
    print("Scene Analyzer Test")
    print("=" * 60)
    
    # Capture and analyze
    if camera.open():
        frame = camera.capture_frame()
        if frame is not None:
            context = analyzer.analyze_scene(frame)
            
            print(f"\nScene Description:")
            print(f"  {context.description}")
            print(f"\nActivity: {context.activity}")
            print(f"People: {context.people_count}")
            print(f"Objects: {len(context.objects)}")
            print(f"Confidence: {context.confidence:.2%}")
            
            if context.relationships:
                print(f"\nRelationships:")
                for rel in context.relationships:
                    print(f"  - {rel}")
        
        camera.close()
    
    print("=" * 60)


if __name__ == "__main__":
    test_scene_analyzer()
