"""
Screen Context and Window Detection
Uses macOS APIs to understand current desktop state
"""

import logging
from typing import List, Dict, Optional
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
from AppKit import NSWorkspace

logger = logging.getLogger(__name__)


class ScreenContext:
    """
    Captures and analyzes screen state using macOS APIs.
    Provides information about windows and running applications.
    """
    
    @staticmethod
    def get_window_list() -> List[Dict]:
        """
        Get all visible windows with positions and dimensions.
        
        Returns:
            List of window dictionaries with app, x, y, width, height
        """
        window_list = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly,
            kCGNullWindowID
        )
        
        windows = []
        for window in window_list:
            app_name = window.get('kCGWindowOwnerName', '')
            bounds = window.get('kCGWindowBounds', {})
            
            if app_name and bounds:
                windows.append({
                    'app': app_name,
                    'x': int(bounds.get('X', 0)),
                    'y': int(bounds.get('Y', 0)),
                    'width': int(bounds.get('Width', 0)),
                    'height': int(bounds.get('Height', 0)),
                    'window_id': window.get('kCGWindowNumber', 0)
                })
        
        logger.debug(f"Found {len(windows)} visible windows")
        return windows
    
    @staticmethod
    def find_window(app_name: str) -> Optional[Dict]:
        """
        Find window by app name (case-insensitive, partial match).
        
        Args:
            app_name: Application name to search for
        
        Returns:
            Window dictionary or None if not found
        """
        windows = ScreenContext.get_window_list()
        app_lower = app_name.lower()
        
        # Try exact match first
        for window in windows:
            if window['app'].lower() == app_lower:
                logger.debug(f"Found window (exact): {window['app']}")
                return window
        
        # Try partial match
        for window in windows:
            if app_lower in window['app'].lower():
                logger.debug(f"Found window (partial): {window['app']}")
                return window
        
        logger.debug(f"No window found for: {app_name}")
        return None
    
    @staticmethod
    def get_running_apps() -> List[str]:
        """
        Get list of currently running applications.
        
        Returns:
            List of application names
        """
        workspace = NSWorkspace.sharedWorkspace()
        apps = workspace.runningApplications()
        app_names = [app.localizedName() for app in apps if app.localizedName()]
        
        logger.debug(f"Found {len(app_names)} running apps")
        return sorted(app_names)
    
    @staticmethod
    def get_frontmost_app() -> Optional[str]:
        """
        Get name of the currently active (frontmost) application.
        
        Returns:
            Application name or None
        """
        workspace = NSWorkspace.sharedWorkspace()
        active_app = workspace.frontmostApplication()
        
        if active_app:
            app_name = active_app.localizedName()
            logger.debug(f"Frontmost app: {app_name}")
            return app_name
        
        return None
    
    @staticmethod
    def is_app_running(app_name: str) -> bool:
        """
        Check if an application is currently running.
        
        Args:
            app_name: Application name to check
        
        Returns:
            True if running
        """
        running_apps = ScreenContext.get_running_apps()
        app_lower = app_name.lower()
        
        # Check exact match
        if app_name in running_apps:
            return True
        
        # Check partial match
        for running_app in running_apps:
            if app_lower in running_app.lower():
                return True
        
        return False
    
    @staticmethod
    def get_screen_info() -> Dict:
        """
        Get screen dimensions and information.
        
        Returns:
            Dictionary with screen info
        """
        from AppKit import NSScreen
        
        main_screen = NSScreen.mainScreen()
        if main_screen:
            frame = main_screen.frame()
            visible_frame = main_screen.visibleFrame()
            
            return {
                'width': int(frame.size.width),
                'height': int(frame.size.height),
                'visible_width': int(visible_frame.size.width),
                'visible_height': int(visible_frame.size.height),
                'x': int(frame.origin.x),
                'y': int(frame.origin.y)
            }
        
        return {}
    
    @staticmethod
    def describe_screen() -> str:
        """
        Get human-readable description of current screen state.
        
        Returns:
            Text description of windows and apps
        """
        windows = ScreenContext.get_window_list()
        running_apps = ScreenContext.get_running_apps()
        frontmost = ScreenContext.get_frontmost_app()
        
        description = []
        description.append(f"Currently {len(running_apps)} apps are running.")
        
        if frontmost:
            description.append(f"The active app is {frontmost}.")
        
        if windows:
            visible_apps = list(set(w['app'] for w in windows))
            description.append(f"Visible windows: {', '.join(visible_apps[:5])}")
        
        return " ".join(description)


def test_screen_context():
    """Test screen context functions."""
    print("=== Screen Context Test ===\n")
    
    # Get all windows
    print("Visible Windows:")
    windows = ScreenContext.get_window_list()
    for window in windows[:10]:  # Show first 10
        print(f"  {window['app']}: {window['width']}x{window['height']} at ({window['x']}, {window['y']})")
    print()
    
    # Get running apps
    print("Running Applications:")
    apps = ScreenContext.get_running_apps()
    for app in apps[:15]:  # Show first 15
        print(f"  - {app}")
    print()
    
    # Get frontmost app
    frontmost = ScreenContext.get_frontmost_app()
    print(f"Active App: {frontmost}\n")
    
    # Test finding a window
    if frontmost:
        window = ScreenContext.find_window(frontmost)
        if window:
            print(f"Found window: {window}\n")
    
    # Screen description
    description = ScreenContext.describe_screen()
    print(f"Description: {description}\n")
    
    # Screen info
    screen_info = ScreenContext.get_screen_info()
    print(f"Screen: {screen_info}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_screen_context()
