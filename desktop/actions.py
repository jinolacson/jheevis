"""
Desktop Action Executor
Performs desktop control actions using macOS APIs and AppleScript
"""

import subprocess
import logging
import time
from typing import Optional, Dict, Tuple, List, Any
from difflib import get_close_matches

from desktop.screen import ScreenContext
from desktop.system_control import SystemController
from desktop.file_search import FileSearcher
from vision.camera import Camera
from vision.detector import ObjectDetector
from vision.scene_analyzer import SceneAnalyzer
import config

logger = logging.getLogger(__name__)


class ActionExecutor:
    """
    Executes desktop control actions on macOS.
    Uses AppleScript, Cocoa APIs, and shell commands.
    """
    
    def __init__(self):
        """Initialize action executor."""
        self.screen = ScreenContext()
        self.system = SystemController()
        self.files = FileSearcher()
        self.camera = Camera()
        self.detector = ObjectDetector(confidence=0.25)  # Lower confidence for better detection
        self.scene_analyzer = SceneAnalyzer(self.detector)  # Enhanced scene understanding
        logger.info("Action executor initialized with enhanced vision")
    
    def open_app(self, app_name: str) -> bool:
        """
        Open or activate an application.
        
        Args:
            app_name: Name of application to open
        
        Returns:
            True if successful
        """
        # Fuzzy match app name
        matched_app = self._fuzzy_match_app(app_name)
        if matched_app:
            app_name = matched_app
        
        logger.info(f"Opening app: {app_name}")
        
        try:
            script = f'tell application "{app_name}" to activate'
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully opened: {app_name}")
                return True
            else:
                logger.error(f"Failed to open {app_name}: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"Error opening app: {e}")
            return False
    
    def close_app(self, app_name: str) -> bool:
        """
        Close an application.
        
        Args:
            app_name: Name of application to close
        
        Returns:
            True if successful
        """
        matched_app = self._fuzzy_match_app(app_name)
        if matched_app:
            app_name = matched_app
        
        logger.info(f"Closing app: {app_name}")
        
        try:
            script = f'tell application "{app_name}" to quit'
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully closed: {app_name}")
                return True
            else:
                logger.error(f"Failed to close {app_name}: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"Error closing app: {e}")
            return False
    
    def move_window(
        self,
        app_name: str,
        position: Optional[str] = None,
        x: Optional[int] = None,
        y: Optional[int] = None,
        animate: bool = True
    ) -> bool:
        """
        Move window to a position.
        
        Args:
            app_name: Application name
            position: Named position ('left', 'right', 'center', 'top-left', etc.)
            x: X coordinate (overrides position)
            y: Y coordinate (overrides position)
            animate: Whether to animate movement
        
        Returns:
            True if successful
        """
        matched_app = self._fuzzy_match_app(app_name)
        if matched_app:
            app_name = matched_app
        
        # Get screen dimensions
        screen_info = self.screen.get_screen_info()
        screen_width = screen_info.get('width', 1920)
        screen_height = screen_info.get('height', 1080)
        
        # Calculate position if named position provided
        if position and x is None and y is None:
            x, y = self._calculate_position(position, screen_width, screen_height)
        
        if x is None or y is None:
            logger.error("No valid position specified")
            return False
        
        logger.info(f"Moving {app_name} to ({x}, {y})")
        
        try:
            if animate and config.WINDOW_ANIMATION_DURATION > 0:
                # Get current window position
                window = self.screen.find_window(app_name)
                if window:
                    start_x, start_y = window['x'], window['y']
                    self._move_window_animated(app_name, (start_x, start_y), (x, y))
                else:
                    # Fallback to direct move
                    self._move_window_direct(app_name, x, y)
            else:
                self._move_window_direct(app_name, x, y)
            
            return True
        
        except Exception as e:
            logger.error(f"Error moving window: {e}")
            return False
    
    def _move_window_direct(self, app_name: str, x: int, y: int):
        """Move window directly without animation."""
        script = f'''
        tell application "System Events"
            tell process "{app_name}"
                set position of window 1 to {{{x}, {y}}}
            end tell
        end tell
        '''
        subprocess.run(['osascript', '-e', script], capture_output=True, timeout=5)
        logger.debug(f"Moved {app_name} to ({x}, {y})")
    
    def _move_window_animated(
        self,
        app_name: str,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int]
    ):
        """Animate window movement."""
        start_x, start_y = from_pos
        end_x, end_y = to_pos
        
        steps = config.WINDOW_ANIMATION_STEPS
        duration = config.WINDOW_ANIMATION_DURATION
        delay = duration / steps
        
        for i in range(steps + 1):
            # Ease-out cubic
            progress = i / steps
            eased = 1 - (1 - progress) ** 3
            
            # Interpolate position
            current_x = int(start_x + (end_x - start_x) * eased)
            current_y = int(start_y + (end_y - start_y) * eased)
            
            # Move window
            self._move_window_direct(app_name, current_x, current_y)
            
            if i < steps:
                time.sleep(delay)
    
    def minimize_window(self, app_name: str) -> bool:
        """Minimize application window."""
        matched_app = self._fuzzy_match_app(app_name)
        if matched_app:
            app_name = matched_app
        
        logger.info(f"Minimizing: {app_name}")
        
        try:
            script = f'''
            tell application "System Events"
                tell process "{app_name}"
                    set miniaturized of window 1 to true
                end tell
            end tell
            '''
            subprocess.run(['osascript', '-e', script], capture_output=True, timeout=5)
            return True
        except Exception as e:
            logger.error(f"Error minimizing window: {e}")
            return False
    
    def maximize_window(self, app_name: str) -> bool:
        """Maximize application window (fullscreen)."""
        matched_app = self._fuzzy_match_app(app_name)
        if matched_app:
            app_name = matched_app
        
        logger.info(f"Maximizing: {app_name}")
        
        try:
            # Get screen dimensions
            screen_info = self.screen.get_screen_info()
            width = screen_info.get('visible_width', 1920)
            height = screen_info.get('visible_height', 1080)
            
            script = f'''
            tell application "System Events"
                tell process "{app_name}"
                    set position of window 1 to {{0, 0}}
                    set size of window 1 to {{{width}, {height}}}
                end tell
            end tell
            '''
            subprocess.run(['osascript', '-e', script], capture_output=True, timeout=5)
            return True
        except Exception as e:
            logger.error(f"Error maximizing window: {e}")
            return False
    
    def search_web(self, query: str, browser: str = "Safari") -> bool:
        """
        Open browser and search for query.
        
        Args:
            query: Search query
            browser: Browser to use (default: Safari)
        
        Returns:
            True if successful
        """
        logger.info(f"Searching web: '{query}' in {browser}")
        
        try:
            # URL encode query
            import urllib.parse
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            
            script = f'''
            tell application "{browser}"
                activate
                delay 0.5
                
                if (count of windows) = 0 then
                    make new document
                end if
                
                tell window 1
                    set current tab to (make new tab with properties {{URL:"{search_url}"}})
                end tell
            end tell
            '''
            subprocess.run(['osascript', '-e', script], capture_output=True, timeout=10)
            return True
        except Exception as e:
            logger.error(f"Error searching web: {e}")
            return False
    
    def type_text(self, text: str) -> bool:
        """
        Type text in current application.
        
        Args:
            text: Text to type
        
        Returns:
            True if successful
        """
        logger.info(f"Typing text: '{text[:50]}...'")
        
        try:
            # Escape special characters
            text = text.replace('"', '\\"')
            
            script = f'''
            tell application "System Events"
                keystroke "{text}"
            end tell
            '''
            subprocess.run(['osascript', '-e', script], capture_output=True, timeout=5)
            return True
        except Exception as e:
            logger.error(f"Error typing text: {e}")
            return False
    
    def _calculate_position(
        self,
        position: str,
        screen_width: int,
        screen_height: int
    ) -> Tuple[int, int]:
        """Calculate x, y coordinates from named position."""
        # Standard window size (can be adjusted)
        window_width = screen_width // 2
        window_height = screen_height // 2
        
        positions = {
            "left": (0, screen_height // 4),
            "right": (screen_width // 2, screen_height // 4),
            "center": (screen_width // 4, screen_height // 4),
            "top": (screen_width // 4, 0),
            "bottom": (screen_width // 4, screen_height // 2),
            "top-left": (0, 0),
            "top-right": (screen_width // 2, 0),
            "bottom-left": (0, screen_height // 2),
            "bottom-right": (screen_width // 2, screen_height // 2),
        }
        
        return positions.get(position, (screen_width // 4, screen_height // 4))
    
    # =========================
    # SYSTEM CONTROL ACTIONS
    # =========================
    
    def volume_up(self, amount: int = 10) -> bool:
        """Increase system volume."""
        return self.system.volume_up(amount)
    
    def volume_down(self, amount: int = 10) -> bool:
        """Decrease system volume."""
        return self.system.volume_down(amount)
    
    def set_volume(self, level: int) -> bool:
        """Set system volume to specific level (0-100)."""
        return self.system.set_volume(level)
    
    def mute(self) -> bool:
        """Mute system volume."""
        return self.system.mute()
    
    def unmute(self) -> bool:
        """Unmute system volume."""
        return self.system.unmute()
    
    def brightness_up(self) -> bool:
        """Increase screen brightness."""
        return self.system.brightness_up()
    
    def brightness_down(self) -> bool:
        """Decrease screen brightness."""
        return self.system.brightness_down()
    
    def set_brightness(self, level: float) -> bool:
        """Set screen brightness (0.0-1.0 or 0-100)."""
        return self.system.set_brightness(level)
    
    def enable_dnd(self) -> bool:
        """Enable Do Not Disturb mode."""
        return self.system.enable_dnd()
    
    def disable_dnd(self) -> bool:
        """Disable Do Not Disturb mode."""
        return self.system.disable_dnd()
    
    def get_battery_status(self) -> Dict[str, Any]:
        """Get battery status information."""
        return self.system.get_battery_status()
    
    def sleep_system(self) -> bool:
        """Put system to sleep."""
        return self.system.sleep_system()
    
    def get_trash_count(self) -> Optional[int]:
        """Get number of items in trash."""
        return self.system.get_trash_count()
    
    def empty_trash(self) -> bool:
        """Empty the trash."""
        return self.system.empty_trash()
    
    def get_current_date(self) -> str:
        """Get current date."""
        return self.system.get_current_date()
    
    def get_current_time(self) -> str:
        """Get current time."""
        return self.system.get_current_time()
    
    def get_weather(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Get weather information."""
        return self.system.get_weather(location)
    
    # =========================
    # FILE SEARCH ACTIONS
    # =========================
    
    def search_files(
        self,
        query: str,
        limit: int = 5,
        file_type: Optional[str] = None,
        location: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for files.
        
        Args:
            query: Search query
            limit: Maximum results
            file_type: Filter by file type
            location: Search location
        
        Returns:
            List of matching files
        """
        return self.files.search(query, limit=limit, file_type=file_type, location=location)
    
    def find_file(self, filename: str) -> Optional[str]:
        """
        Find a specific file by name.
        
        Args:
            filename: Name of file to find
        
        Returns:
            Full path to file, or None if not found
        """
        return self.files.find_file(filename)
    
    def open_file_by_name(self, filename: str) -> bool:
        """
        Find and open a file by name.
        
        Args:
            filename: Name of file to open
        
        Returns:
            True if successful
        """
        file_path = self.find_file(filename)
        if file_path:
            return self.files.open_file(file_path)
        
        logger.warning(f"File not found: {filename}")
        return False
    
    def get_recent_files(self, days: int = 7, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recently modified files.
        
        Args:
            days: Number of days to look back
            limit: Maximum results
        
        Returns:
            List of recent files
        """
        return self.files.search_recent(days=days, limit=limit)
    
    def reveal_file_in_finder(self, filename: str) -> bool:
        """
        Find a file and reveal it in Finder.
        
        Args:
            filename: Name of file to reveal
        
        Returns:
            True if successful
        """
        file_path = self.find_file(filename)
        if file_path:
            return self.files.reveal_in_finder(file_path)
        
        logger.warning(f"File not found: {filename}")
        return False
    
    # =========================
    # TERMINAL CONTROL ACTIONS
    # =========================
    
    def open_terminal(self) -> bool:
        """
        Open Terminal application.
        
        Returns:
            True if successful
        """
        logger.info("Opening Terminal")
        return self.open_app("Terminal")
    
    def close_terminal(self) -> bool:
        """
        Close Terminal application (quits all windows).
        
        Returns:
            True if successful
        """
        logger.info("Closing Terminal")
        return self.close_app("Terminal")
    
    def close_current_terminal(self) -> bool:
        """
        Close the current active Terminal window or tab.
        
        Returns:
            True if successful
        """
        logger.info("Closing current Terminal window/tab")
        
        try:
            script = '''
            tell application "Terminal"
                if (count of windows) > 0 then
                    close front window
                    return true
                else
                    return false
                end if
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and 'true' in result.stdout.lower():
                logger.info("Current Terminal window closed")
                return True
            else:
                logger.warning("No Terminal window to close")
                return False
        
        except Exception as e:
            logger.error(f"Error closing current Terminal: {e}")
            return False
    
    def new_terminal_window(self) -> bool:
        """
        Open a new Terminal window.
        
        Returns:
            True if successful
        """
        logger.info("Opening new Terminal window")
        
        try:
            script = '''
            tell application "Terminal"
                activate
                do script ""
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logger.info("New Terminal window created")
                return True
            else:
                logger.error(f"Failed to create Terminal window: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"Error creating Terminal window: {e}")
            return False
    
    def new_terminal_tab(self) -> bool:
        """
        Open a new Terminal tab in the current window.
        
        Returns:
            True if successful
        """
        logger.info("Opening new Terminal tab")
        
        try:
            script = '''
            tell application "Terminal"
                activate
                tell application "System Events"
                    keystroke "t" using command down
                end tell
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logger.info("New Terminal tab created")
                return True
            else:
                logger.error(f"Failed to create Terminal tab: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"Error creating Terminal tab: {e}")
            return False
    
    def run_terminal_command(self, command: str) -> bool:
        """
        Run a command in a new Terminal window.
        
        Args:
            command: Command to execute
        
        Returns:
            True if successful
        """
        logger.info(f"Running command in Terminal: '{command}'")
        
        try:
            # Escape command for AppleScript
            escaped_command = command.replace('\\', '\\\\').replace('"', '\\"')
            
            script = f'''
            tell application "Terminal"
                activate
                do script "{escaped_command}"
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logger.info(f"Command executed in Terminal")
                return True
            else:
                logger.error(f"Failed to execute command: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"Error executing Terminal command: {e}")
            return False
    
    # =========================
    # VISION/CAMERA ACTIONS
    # =========================
    
    def what_do_you_see(self) -> Dict[str, Any]:
        """
        Capture image and describe what's visible with enhanced scene understanding.
        
        Returns:
            Dictionary with description and detections
        """
        logger.info("Capturing image to see what's visible")
        
        try:
            # Capture multiple frames for better analysis
            frame = self.camera.capture_multiple_frames(num_frames=3)
            
            if frame is None:
                logger.error("Failed to capture frame")
                return {
                    'success': False,
                    'description': "I couldn't access the camera"
                }
            
            # Use enhanced scene analyzer
            context = self.scene_analyzer.analyze_scene(frame, use_history=True)
            
            result = {
                'success': True,
                'description': context.description,
                'activity': context.activity,
                'people_count': context.people_count,
                'detections': context.objects,
                'relationships': context.relationships,
                'num_objects': len(context.objects),
                'confidence': context.confidence
            }
            
            logger.info(f"Vision result: {context.description}")
            return result
        
        except Exception as e:
            logger.error(f"Error in what_do_you_see: {e}")
            return {
                'success': False,
                'description': "I encountered an error accessing the camera"
            }
    
    def who_is_here(self) -> Dict[str, Any]:
        """
        Detect if people are present.
        
        Returns:
            Dictionary with people count and result
        """
        logger.info("Checking for people")
        
        try:
            # Capture frame
            frame = self.camera.capture_multiple_frames(num_frames=3)
            
            if frame is None:
                return {
                    'success': False,
                    'count': 0,
                    'message': "I couldn't access the camera"
                }
            
            # Detect people
            people = self.detector.detect_people(frame)
            count = len(people)
            
            # Generate message
            if count == 0:
                message = "I don't see anyone"
            elif count == 1:
                message = "I see one person"
            else:
                message = f"I see {count} people"
            
            result = {
                'success': True,
                'count': count,
                'message': message,
                'people': people
            }
            
            logger.info(f"People detection: {message}")
            return result
        
        except Exception as e:
            logger.error(f"Error in who_is_here: {e}")
            return {
                'success': False,
                'count': 0,
                'message': "I encountered an error accessing the camera"
            }
    
    def count_people(self) -> Dict[str, Any]:
        """
        Count number of people visible.
        
        Returns:
            Dictionary with count and message
        """
        # Reuse who_is_here which does the same thing
        return self.who_is_here()
    
    def detect_objects(self) -> Dict[str, Any]:
        """
        Detect and list all visible objects.
        
        Returns:
            Dictionary with objects and counts
        """
        logger.info("Detecting objects")
        
        try:
            # Capture frame
            frame = self.camera.capture_multiple_frames(num_frames=3)
            
            if frame is None:
                return {
                    'success': False,
                    'objects': {},
                    'message': "I couldn't access the camera"
                }
            
            # Get object counts
            counts = self.detector.get_object_counts(frame)
            
            # Generate message
            if not counts:
                message = "I don't see any objects clearly"
            else:
                items = []
                for obj, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
                    if count == 1:
                        items.append(f"one {obj}")
                    else:
                        items.append(f"{count} {obj}s")
                
                if len(items) == 1:
                    message = f"I see {items[0]}"
                elif len(items) == 2:
                    message = f"I see {items[0]} and {items[1]}"
                else:
                    message = f"I see {', '.join(items[:-1])}, and {items[-1]}"
            
            result = {
                'success': True,
                'objects': counts,
                'message': message,
                'total': sum(counts.values())
            }
            
            logger.info(f"Object detection: {message}")
            return result
        
        except Exception as e:
            logger.error(f"Error in detect_objects: {e}")
            return {
                'success': False,
                'objects': {},
                'message': "I encountered an error accessing the camera"
            }
    
    def take_picture(self, save_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Take a picture and optionally save it.
        
        Args:
            save_path: Optional path to save image
        
        Returns:
            Dictionary with result and path
        """
        logger.info(f"Taking picture (save_path: {save_path})")
        
        try:
            import time
            from pathlib import Path
            import cv2
            
            # Capture frame
            frame = self.camera.capture_multiple_frames(num_frames=3)
            
            if frame is None:
                return {
                    'success': False,
                    'message': "I couldn't access the camera"
                }
            
            # Generate default path if not provided
            if save_path is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                save_path = str(Path.home() / "Desktop" / f"jheevis_photo_{timestamp}.jpg")
            
            # Save image
            cv2.imwrite(save_path, frame)
            
            result = {
                'success': True,
                'path': save_path,
                'message': f"Picture saved to {Path(save_path).name}"
            }
            
            logger.info(f"Picture saved: {save_path}")
            return result
        
        except Exception as e:
            logger.error(f"Error taking picture: {e}")
            return {
                'success': False,
                'message': "I encountered an error taking the picture"
            }
    
    def get_activity_summary(self) -> Dict[str, Any]:
        """
        Get a summary of recent activity from scene analysis.
        
        Returns:
            Dictionary with activity summary
        """
        logger.info("Getting activity summary")
        
        try:
            summary = self.scene_analyzer.get_activity_summary()
            
            result = {
                'success': True,
                'summary': summary,
                'message': summary
            }
            
            logger.info(f"Activity summary: {summary}")
            return result
        
        except Exception as e:
            logger.error(f"Error getting activity summary: {e}")
            return {
                'success': False,
                'message': "I don't have any activity history yet"
            }
    
    def analyze_scene_detailed(self) -> Dict[str, Any]:
        """
        Perform detailed scene analysis with relationships and context.
        
        Returns:
            Dictionary with comprehensive scene analysis
        """
        logger.info("Performing detailed scene analysis")
        
        try:
            # Capture frame
            frame = self.camera.capture_multiple_frames(num_frames=5)
            
            if frame is None:
                return {
                    'success': False,
                    'message': "I couldn't access the camera"
                }
            
            # Analyze scene with history
            context = self.scene_analyzer.analyze_scene(frame, use_history=True)
            
            # Build detailed message
            message = context.description
            
            # Add relationships if available
            if context.relationships:
                message += " Regarding spatial layout: " + ". ".join(context.relationships[:3]) + "."
            
            # Add activity insight
            if context.activity not in ['idle', 'present']:
                activity_name = context.activity.replace('_', ' ')
                message += f" It appears you're {activity_name}."
            
            result = {
                'success': True,
                'message': message,
                'description': context.description,
                'activity': context.activity,
                'people_count': context.people_count,
                'relationships': context.relationships,
                'num_objects': len(context.objects),
                'confidence': context.confidence
            }
            
            logger.info(f"Detailed analysis: {message}")
            return result
        
        except Exception as e:
            logger.error(f"Error in detailed scene analysis: {e}")
            return {
                'success': False,
                'message': "I encountered an error analyzing the scene"
            }
    
    def _fuzzy_match_app(self, app_name: str) -> Optional[str]:
        """
        Fuzzy match app name against running applications.
        
        Args:
            app_name: Approximate app name
        
        Returns:
            Matched app name or None
        """
        running_apps = self.screen.get_running_apps()
        
        # Try exact match first
        if app_name in running_apps:
            return app_name
        
        # Try case-insensitive match
        for app in running_apps:
            if app.lower() == app_name.lower():
                return app
        
        # Try partial match (contains)
        app_lower = app_name.lower()
        for app in running_apps:
            if app_lower in app.lower() or app.lower() in app_lower:
                logger.debug(f"Partial match '{app_name}' to '{app}'")
                return app
        
        # Try fuzzy match with lower threshold
        matches = get_close_matches(
            app_name,
            running_apps,
            n=1,
            cutoff=0.4  # Lowered from 0.6 to be more forgiving
        )
        
        if matches:
            logger.debug(f"Fuzzy matched '{app_name}' to '{matches[0]}'")
            return matches[0]
        
        logger.warning(f"No match found for app: {app_name}")
        return None


def test_executor():
    """Test action executor."""
    executor = ActionExecutor()
    
    print("=== Action Executor Test ===\n")
    
    # Test opening an app
    print("Opening Safari...")
    executor.open_app("Safari")
    time.sleep(2)
    
    # Test moving window
    print("Moving Safari to the right...")
    executor.move_window("Safari", position="right")
    time.sleep(2)
    
    # Test web search
    print("Searching for 'Python programming'...")
    executor.search_web("Python programming")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_executor()
