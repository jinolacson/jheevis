"""
System Control Module
Controls macOS system settings: volume, brightness, Do Not Disturb
"""

import subprocess
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class SystemController:
    """
    Controls macOS system settings using AppleScript and shell commands.
    Handles volume, brightness, Do Not Disturb, and other system functions.
    """
    
    def __init__(self):
        """Initialize system controller."""
        logger.info("System controller initialized")
    
    # =========================
    # VOLUME CONTROL
    # =========================
    
    def get_volume(self) -> Optional[int]:
        """
        Get current system volume (0-100).
        
        Returns:
            Volume level as integer, or None if error
        """
        try:
            script = 'output volume of (get volume settings)'
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                volume = int(result.stdout.strip())
                logger.debug(f"Current volume: {volume}")
                return volume
            return None
        
        except Exception as e:
            logger.error(f"Error getting volume: {e}")
            return None
    
    def set_volume(self, level: int) -> bool:
        """
        Set system volume.
        
        Args:
            level: Volume level (0-100)
        
        Returns:
            True if successful
        """
        # Clamp to valid range
        level = max(0, min(100, level))
        
        logger.info(f"Setting volume to {level}")
        
        try:
            script = f'set volume output volume {level}'
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                logger.info(f"Volume set to {level}")
                return True
            else:
                logger.error(f"Failed to set volume: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
            return False
    
    def volume_up(self, amount: int = 10) -> bool:
        """
        Increase volume by amount.
        
        Args:
            amount: Amount to increase (default 10)
        
        Returns:
            True if successful
        """
        current = self.get_volume()
        if current is not None:
            new_level = min(100, current + amount)
            return self.set_volume(new_level)
        return False
    
    def volume_down(self, amount: int = 10) -> bool:
        """
        Decrease volume by amount.
        
        Args:
            amount: Amount to decrease (default 10)
        
        Returns:
            True if successful
        """
        current = self.get_volume()
        if current is not None:
            new_level = max(0, current - amount)
            return self.set_volume(new_level)
        return False
    
    def mute(self) -> bool:
        """
        Mute system volume.
        
        Returns:
            True if successful
        """
        logger.info("Muting volume")
        
        try:
            script = 'set volume output muted true'
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                logger.info("Volume muted")
                return True
            return False
        
        except Exception as e:
            logger.error(f"Error muting: {e}")
            return False
    
    def unmute(self) -> bool:
        """
        Unmute system volume.
        
        Returns:
            True if successful
        """
        logger.info("Unmuting volume")
        
        try:
            script = 'set volume output muted false'
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                logger.info("Volume unmuted")
                return True
            return False
        
        except Exception as e:
            logger.error(f"Error unmuting: {e}")
            return False
    
    # =========================
    # BRIGHTNESS CONTROL
    # =========================
    
    def get_brightness(self) -> Optional[float]:
        """
        Get current screen brightness (0.0-1.0).
        
        Returns:
            Brightness level as float, or None if error
        """
        try:
            # Use python to read brightness via CoreDisplay framework
            script = """
import Quartz
brightness = Quartz.CoreGraphics.CGDisplayCopyDisplayMode(Quartz.CoreGraphics.CGMainDisplayID())
print(brightness)
"""
            # Alternative: use brightness command-line tool if installed
            # For now, we'll use AppleScript workaround
            
            # Note: Direct brightness reading requires additional permissions
            # This is a placeholder - actual implementation may vary
            logger.warning("Brightness reading not fully implemented")
            return None
        
        except Exception as e:
            logger.error(f"Error getting brightness: {e}")
            return None
    
    def set_brightness(self, level: float) -> bool:
        """
        Set screen brightness.
        
        Args:
            level: Brightness level (0.0-1.0 or 0-100)
        
        Returns:
            True if successful
        """
        # Normalize to 0-1 range
        if level > 1.0:
            level = level / 100.0
        
        level = max(0.0, min(1.0, level))
        
        logger.info(f"Setting brightness to {level}")
        
        try:
            # Using brightness command-line tool (requires installation)
            # brew install brightness
            result = subprocess.run(
                ['brightness', str(level)],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                logger.info(f"Brightness set to {level}")
                return True
            else:
                logger.warning("Brightness tool not found. Install with: brew install brightness")
                return False
        
        except FileNotFoundError:
            logger.error("Brightness command not found. Install with: brew install brightness")
            return False
        except Exception as e:
            logger.error(f"Error setting brightness: {e}")
            return False
    
    def brightness_up(self, amount: float = 0.1) -> bool:
        """
        Increase brightness.
        
        Args:
            amount: Amount to increase (0.0-1.0)
        
        Returns:
            True if successful
        """
        # Simulate key press for brightness up
        return self._send_key_code(144)  # F15 mapped to brightness up
    
    def brightness_down(self, amount: float = 0.1) -> bool:
        """
        Decrease brightness.
        
        Args:
            amount: Amount to decrease (0.0-1.0)
        
        Returns:
            True if successful
        """
        # Simulate key press for brightness down
        return self._send_key_code(145)  # F14 mapped to brightness down
    
    # =========================
    # DO NOT DISTURB
    # =========================
    
    def enable_dnd(self) -> bool:
        """
        Enable Do Not Disturb mode.
        
        Returns:
            True if successful
        """
        logger.info("Enabling Do Not Disturb")
        
        try:
            # macOS 12+ (Monterey and later)
            script = '''
            tell application "System Events"
                tell process "SystemUIServer"
                    tell (menu bar item 1 of menu bar 1 where description is "Notification Center")
                        click
                        delay 0.5
                    end tell
                end tell
            end tell
            '''
            
            # Alternative: Use shortcuts if available
            # For macOS 12+, use Focus modes via shortcuts
            subprocess.run(
                ['shortcuts', 'run', 'Enable Do Not Disturb'],
                capture_output=True,
                timeout=3
            )
            
            logger.info("Do Not Disturb enabled")
            return True
        
        except Exception as e:
            logger.error(f"Error enabling DND: {e}")
            logger.info("You may need to create a Shortcut named 'Enable Do Not Disturb'")
            return False
    
    def disable_dnd(self) -> bool:
        """
        Disable Do Not Disturb mode.
        
        Returns:
            True if successful
        """
        logger.info("Disabling Do Not Disturb")
        
        try:
            subprocess.run(
                ['shortcuts', 'run', 'Disable Do Not Disturb'],
                capture_output=True,
                timeout=3
            )
            
            logger.info("Do Not Disturb disabled")
            return True
        
        except Exception as e:
            logger.error(f"Error disabling DND: {e}")
            return False
    
    # =========================
    # ADDITIONAL SYSTEM CONTROLS
    # =========================
    
    def get_battery_status(self) -> Dict[str, Any]:
        """
        Get battery status and charge level.
        
        Returns:
            Dictionary with battery info
        """
        try:
            result = subprocess.run(
                ['pmset', '-g', 'batt'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # Parse output
                info = {
                    'charging': 'AC Power' in output or 'charging' in output.lower(),
                    'percentage': None,
                    'time_remaining': None,
                    'raw': output
                }
                
                # Extract percentage
                if '%' in output:
                    for part in output.split():
                        if '%' in part:
                            # Remove % and any trailing semicolons
                            percentage_str = part.replace('%', '').replace(';', '').strip()
                            try:
                                info['percentage'] = int(percentage_str)
                            except ValueError:
                                logger.warning(f"Could not parse percentage: {part}")
                            break
                
                logger.debug(f"Battery status: {info}")
                return info
            
            return {}
        
        except Exception as e:
            logger.error(f"Error getting battery status: {e}")
            return {}
    
    def sleep_system(self) -> bool:
        """
        Put system to sleep.
        
        Returns:
            True if successful
        """
        logger.info("Putting system to sleep")
        
        try:
            subprocess.run(['pmset', 'sleepnow'], timeout=2)
            return True
        except Exception as e:
            logger.error(f"Error sleeping system: {e}")
            return False
    
    # =========================
    # TRASH MANAGEMENT
    # =========================
    
    def get_trash_count(self) -> Optional[int]:
        """
        Get number of items in trash.
        
        Returns:
            Number of items in trash, or None if error
        """
        try:
            script = '''
            tell application "Finder"
                count of items in trash
            end tell
            '''
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0:
                count = int(result.stdout.strip())
                logger.debug(f"Trash contains {count} items")
                return count
            return None
        
        except Exception as e:
            logger.error(f"Error getting trash count: {e}")
            return None
    
    def empty_trash(self) -> bool:
        """
        Empty the trash.
        
        Returns:
            True if successful
        """
        logger.info("Emptying trash")
        
        try:
            script = '''
            tell application "Finder"
                empty trash
            end tell
            '''
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=10  # May take longer if trash is large
            )
            
            if result.returncode == 0:
                logger.info("Trash emptied successfully")
                return True
            else:
                logger.error(f"Failed to empty trash: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"Error emptying trash: {e}")
            return False
    
    # =========================
    # DATE & TIME
    # =========================
    
    def get_current_date(self) -> str:
        """
        Get current date in human-readable format.
        
        Returns:
            Formatted date string
        """
        now = datetime.now()
        # Format: "Monday, May 6th, 2026"
        day_suffix = self._get_day_suffix(now.day)
        formatted = now.strftime(f"%A, %B {now.day}{day_suffix}, %Y")
        logger.debug(f"Current date: {formatted}")
        return formatted
    
    def get_current_time(self) -> str:
        """
        Get current time in human-readable format.
        
        Returns:
            Formatted time string
        """
        now = datetime.now()
        # Format: "3:45 PM"
        formatted = now.strftime("%I:%M %p")
        logger.debug(f"Current time: {formatted}")
        return formatted
    
    def _get_day_suffix(self, day: int) -> str:
        """Get suffix for day (st, nd, rd, th)."""
        if 10 <= day % 100 <= 20:
            return 'th'
        else:
            return {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    
    # =========================
    # WEATHER
    # =========================
    
    def get_weather(self, location: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current weather information.
        Uses wttr.in service (no API key required).
        
        Args:
            location: Location name (defaults to auto-detect)
        
        Returns:
            Dictionary with weather info
        """
        try:
            import urllib.request
            import json
            
            # Use wttr.in - simple weather API
            if location:
                url = f"https://wttr.in/{location}?format=j1"
            else:
                url = "https://wttr.in/?format=j1"
            
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
            
            current = data['current_condition'][0]
            area = data['nearest_area'][0]
            
            weather_info = {
                'location': f"{area['areaName'][0]['value']}, {area['country'][0]['value']}",
                'temperature_c': current['temp_C'],
                'temperature_f': current['temp_F'],
                'condition': current['weatherDesc'][0]['value'],
                'feels_like_c': current['FeelsLikeC'],
                'feels_like_f': current['FeelsLikeF'],
                'humidity': current['humidity'],
                'wind_speed': current['windspeedKmph'],
                'raw': data
            }
            
            logger.debug(f"Weather: {weather_info['condition']}, {weather_info['temperature_c']}°C")
            return weather_info
        
        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            return {}
    
    def _send_key_code(self, key_code: int) -> bool:
        """
        Send a key code using AppleScript.
        
        Args:
            key_code: macOS key code
        
        Returns:
            True if successful
        """
        try:
            script = f'tell application "System Events" to key code {key_code}'
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            return result.returncode == 0
        
        except Exception as e:
            logger.error(f"Error sending key code: {e}")
            return False


# Convenience functions
def set_volume(level: int) -> bool:
    """Set system volume (0-100)."""
    controller = SystemController()
    return controller.set_volume(level)


def volume_up(amount: int = 10) -> bool:
    """Increase volume."""
    controller = SystemController()
    return controller.volume_up(amount)


def volume_down(amount: int = 10) -> bool:
    """Decrease volume."""
    controller = SystemController()
    return controller.volume_down(amount)


def mute() -> bool:
    """Mute system."""
    controller = SystemController()
    return controller.mute()


def get_battery() -> Dict[str, Any]:
    """Get battery status."""
    controller = SystemController()
    return controller.get_battery_status()
