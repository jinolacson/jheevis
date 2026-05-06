"""
Camera module
Handles webcam access and frame capture
"""

import cv2
import logging
import numpy as np
from typing import Optional, Tuple
import time

logger = logging.getLogger(__name__)


class Camera:
    """
    Manages webcam access for capturing frames.
    """
    
    def __init__(self, camera_id: int = 0):
        """
        Initialize camera.
        
        Args:
            camera_id: Camera device ID (0 for default webcam)
        """
        self.camera_id = camera_id
        self.cap = None
        self.is_open = False
        logger.info(f"Camera initialized (device {camera_id})")
    
    def open(self) -> bool:
        """
        Open camera connection.
        
        Returns:
            True if successful
        """
        if self.is_open:
            logger.debug("Camera already open")
            return True
        
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                logger.error("Failed to open camera")
                return False
            
            # Set camera properties for better quality
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_open = True
            logger.info("Camera opened successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error opening camera: {e}")
            return False
    
    def close(self):
        """Close camera connection."""
        if self.cap is not None:
            self.cap.release()
            self.is_open = False
            logger.info("Camera closed")
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from camera.
        
        Returns:
            Frame as numpy array (BGR format), or None if failed
        """
        if not self.is_open:
            if not self.open():
                return None
        
        try:
            ret, frame = self.cap.read()
            
            if not ret or frame is None:
                logger.warning("Failed to capture frame")
                return None
            
            return frame
        
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None
    
    def capture_multiple_frames(self, num_frames: int = 3, delay: float = 0.1) -> Optional[np.ndarray]:
        """
        Capture multiple frames and return the best one.
        Useful for getting a stable image.
        
        Args:
            num_frames: Number of frames to capture
            delay: Delay between frames in seconds
        
        Returns:
            Best frame as numpy array, or None if failed
        """
        frames = []
        
        for i in range(num_frames):
            frame = self.capture_frame()
            if frame is not None:
                frames.append(frame)
            
            if i < num_frames - 1:
                time.sleep(delay)
        
        if not frames:
            return None
        
        # Return the middle frame (usually more stable)
        return frames[len(frames) // 2]
    
    def get_camera_info(self) -> dict:
        """
        Get camera information.
        
        Returns:
            Dictionary with camera properties
        """
        if not self.is_open:
            return {"status": "closed"}
        
        try:
            info = {
                "status": "open",
                "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "fps": int(self.cap.get(cv2.CAP_PROP_FPS)),
                "backend": self.cap.getBackendName()
            }
            return info
        
        except Exception as e:
            logger.error(f"Error getting camera info: {e}")
            return {"status": "error", "error": str(e)}
    
    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()


def list_cameras(max_test: int = 5) -> list:
    """
    List available cameras.
    
    Args:
        max_test: Maximum number of camera IDs to test
    
    Returns:
        List of available camera IDs
    """
    available = []
    
    for i in range(max_test):
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(i)
                cap.release()
        except:
            pass
    
    return available


def capture_snapshot(camera_id: int = 0, save_path: Optional[str] = None) -> Optional[np.ndarray]:
    """
    Capture a single snapshot from camera.
    
    Args:
        camera_id: Camera device ID
        save_path: Optional path to save image
    
    Returns:
        Frame as numpy array, or None if failed
    """
    with Camera(camera_id) as cam:
        frame = cam.capture_multiple_frames(num_frames=3)
        
        if frame is not None and save_path:
            try:
                cv2.imwrite(save_path, frame)
                logger.info(f"Snapshot saved to {save_path}")
            except Exception as e:
                logger.error(f"Error saving snapshot: {e}")
        
        return frame
