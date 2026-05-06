"""
Vision module for Jheevis
Handles camera access, object detection, and scene understanding
"""

from .camera import Camera
from .detector import ObjectDetector

__all__ = ['Camera', 'ObjectDetector']
