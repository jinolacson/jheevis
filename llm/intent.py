"""
Intent Classifier
Determines whether user input requires desktop action or conversational response
"""

import logging
from typing import Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass

import config

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Types of user intents."""
    CONVERSATION = "conversation"  # General Q&A, chitchat
    DESKTOP_ACTION = "desktop_action"  # Control apps, windows, system
    WEB_SEARCH = "web_search"  # Search the web
    UNKNOWN = "unknown"


class ActionType(Enum):
    """Specific desktop actions."""
    OPEN_APP = "open_app"
    CLOSE_APP = "close_app"
    MOVE_WINDOW = "move_window"
    RESIZE_WINDOW = "resize_window"
    MINIMIZE_WINDOW = "minimize_window"
    MAXIMIZE_WINDOW = "maximize_window"
    SEARCH_WEB = "search_web"
    TYPE_TEXT = "type_text"
    CLICK = "click"
    SCREENSHOT = "screenshot"
    # System Control
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    SET_VOLUME = "set_volume"
    MUTE = "mute"
    UNMUTE = "unmute"
    BRIGHTNESS_UP = "brightness_up"
    BRIGHTNESS_DOWN = "brightness_down"
    SET_BRIGHTNESS = "set_brightness"
    ENABLE_DND = "enable_dnd"
    DISABLE_DND = "disable_dnd"
    GET_BATTERY = "get_battery"
    SLEEP_SYSTEM = "sleep_system"
    GET_TRASH_COUNT = "get_trash_count"
    EMPTY_TRASH = "empty_trash"
    GET_DATE = "get_date"
    GET_TIME = "get_time"
    GET_WEATHER = "get_weather"
    # File Operations
    SEARCH_FILES = "search_files"
    OPEN_FILE = "open_file"
    FIND_FILE = "find_file"
    RECENT_FILES = "recent_files"
    # Terminal Control
    OPEN_TERMINAL = "open_terminal"
    CLOSE_TERMINAL = "close_terminal"
    CLOSE_CURRENT_TERMINAL = "close_current_terminal"
    NEW_TERMINAL_WINDOW = "new_terminal_window"
    NEW_TERMINAL_TAB = "new_terminal_tab"
    RUN_TERMINAL_COMMAND = "run_terminal_command"
    # Vision/Camera
    WHAT_DO_YOU_SEE = "what_do_you_see"
    WHO_IS_HERE = "who_is_here"
    COUNT_PEOPLE = "count_people"
    DETECT_OBJECTS = "detect_objects"
    TAKE_PICTURE = "take_picture"
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """Represents classified user intent."""
    intent_type: IntentType
    action_type: Optional[ActionType] = None
    app_name: Optional[str] = None
    query: Optional[str] = None
    parameters: Dict[str, Any] = None
    confidence: float = 1.0
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


class IntentClassifier:
    """
    Rule-based intent classifier for voice commands.
    Uses pattern matching to identify user intentions.
    """
    
    # Keywords for different action types
    OPEN_KEYWORDS = ["open", "launch", "start", "run", "show"]
    CLOSE_KEYWORDS = ["close", "quit", "exit", "kill"]
    MOVE_KEYWORDS = ["move", "drag", "position", "place"]
    RESIZE_KEYWORDS = ["resize", "make bigger", "make smaller", "expand", "shrink"]
    MINIMIZE_KEYWORDS = ["minimize", "hide"]
    MAXIMIZE_KEYWORDS = ["maximize", "full screen", "fullscreen"]
    SEARCH_KEYWORDS = ["search", "google", "look up", "find online"]
    TYPE_KEYWORDS = ["type", "write", "enter text"]
    
    # System Control Keywords
    VOLUME_UP_KEYWORDS = ["volume up", "increase volume", "louder", "turn up"]
    VOLUME_DOWN_KEYWORDS = ["volume down", "decrease volume", "quieter", "turn down", "lower volume"]
    SET_VOLUME_KEYWORDS = ["set volume", "volume to", "volume at"]
    MUTE_KEYWORDS = ["mute", "silence"]
    UNMUTE_KEYWORDS = ["unmute", "unsilence"]
    BRIGHTNESS_UP_KEYWORDS = ["brightness up", "increase brightness", "brighter", "brighten"]
    BRIGHTNESS_DOWN_KEYWORDS = ["brightness down", "decrease brightness", "dimmer", "dim"]
    DND_ON_KEYWORDS = ["enable do not disturb", "turn on do not disturb", "dnd on", "do not disturb on"]
    DND_OFF_KEYWORDS = ["disable do not disturb", "turn off do not disturb", "dnd off", "do not disturb off"]
    BATTERY_KEYWORDS = ["battery", "battery status", "battery level", "how much battery"]
    SLEEP_KEYWORDS = ["sleep", "go to sleep", "put to sleep"]
    TRASH_COUNT_KEYWORDS = ["how many items in trash", "trash count", "items in trash", "how full is trash", "check trash"]
    EMPTY_TRASH_KEYWORDS = ["empty trash", "clear trash", "delete trash"]
    DATE_KEYWORDS = ["what's the date", "what is the date", "what date is it", "today's date", "current date", "what day is it"]
    TIME_KEYWORDS = ["what's the time", "what time is it", "current time", "what's the current time"]
    WEATHER_KEYWORDS = ["weather", "what's the weather", "how's the weather", "weather forecast", "is it raining", "temperature"]
    
    # File Search Keywords (check before web search)
    FILE_SEARCH_KEYWORDS = ["find file", "locate file", "where is file", "search file"]
    RECENT_FILES_KEYWORDS = ["recent files", "recently opened", "recent documents", "latest files"]
    
    # Terminal Keywords
    OPEN_TERMINAL_KEYWORDS = ["open terminal", "launch terminal", "start terminal"]
    CLOSE_TERMINAL_KEYWORDS = ["close terminal", "quit terminal"]
    CLOSE_CURRENT_TERMINAL_KEYWORDS = ["close this terminal", "close current terminal", "exit terminal", "close active terminal", "close this window"]
    NEW_TERMINAL_WINDOW_KEYWORDS = ["new terminal window", "open new terminal window", "create terminal window"]
    NEW_TERMINAL_TAB_KEYWORDS = ["new terminal tab", "new tab in terminal", "open terminal tab"]
    RUN_COMMAND_KEYWORDS = ["run command", "execute", "run in terminal"]
    
    # Vision/Camera Keywords
    WHAT_SEE_KEYWORDS = ["what do you see", "what can you see", "what's in front", "describe what you see", "look around", "what are you looking at"]
    WHO_HERE_KEYWORDS = ["who is here", "who's here", "is anyone here", "who is in the room", "is someone here"]
    COUNT_PEOPLE_KEYWORDS = ["how many people", "count people", "how many persons", "number of people"]
    DETECT_OBJECTS_KEYWORDS = ["what objects", "detect objects", "what things", "identify objects"]
    TAKE_PICTURE_KEYWORDS = ["take picture", "take photo", "capture image", "take snapshot", "take a picture"]
    
    # Question keywords (usually conversational)
    QUESTION_KEYWORDS = ["what", "who", "where", "when", "why", "how", "tell me", "explain"]
    
    def __init__(self):
        """Initialize intent classifier."""
        logger.info("Intent classifier initialized")
    
    def classify(self, text: str) -> Intent:
        """
        Classify user input into intent.
        
        Args:
            text: User's command/question
        
        Returns:
            Intent object with classification
        """
        text_lower = text.lower().strip()
        
        # Check for vision/camera actions first (high priority for safety)
        vision_intent = self._check_vision(text_lower)
        if vision_intent:
            return vision_intent
        
        # Check for system control actions
        system_intent = self._check_system_control(text_lower)
        if system_intent:
            return system_intent
        
        # Check for terminal control actions
        terminal_intent = self._check_terminal_control(text_lower)
        if terminal_intent:
            return terminal_intent
        
        # Check for file search actions
        file_intent = self._check_file_search(text_lower)
        if file_intent:
            return file_intent
        
        # Check for desktop actions
        desktop_intent = self._check_desktop_action(text_lower)
        if desktop_intent:
            return desktop_intent
        
        # Check for web search
        search_intent = self._check_web_search(text_lower)
        if search_intent:
            return search_intent
        
        # Check if it's a question (likely conversational)
        if self._is_question(text_lower):
            return Intent(
                intent_type=IntentType.CONVERSATION,
                query=text
            )
        
        # Default to conversation
        return Intent(
            intent_type=IntentType.CONVERSATION,
            query=text
        )
    
    def _check_desktop_action(self, text: str) -> Optional[Intent]:
        """Check if text indicates a desktop action."""
        
        # Open app
        if any(kw in text for kw in self.OPEN_KEYWORDS):
            app_name = self._extract_app_name(text, self.OPEN_KEYWORDS)
            if app_name:
                return Intent(
                    intent_type=IntentType.DESKTOP_ACTION,
                    action_type=ActionType.OPEN_APP,
                    app_name=app_name
                )
        
        # Close app
        if any(kw in text for kw in self.CLOSE_KEYWORDS):
            app_name = self._extract_app_name(text, self.CLOSE_KEYWORDS)
            if app_name:
                return Intent(
                    intent_type=IntentType.DESKTOP_ACTION,
                    action_type=ActionType.CLOSE_APP,
                    app_name=app_name
                )
        
        # Move window
        if any(kw in text for kw in self.MOVE_KEYWORDS):
            app_name = self._extract_app_name(text, self.MOVE_KEYWORDS)
            position = self._extract_position(text)
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.MOVE_WINDOW,
                app_name=app_name,
                parameters={"position": position}
            )
        
        # Minimize
        if any(kw in text for kw in self.MINIMIZE_KEYWORDS):
            app_name = self._extract_app_name(text, self.MINIMIZE_KEYWORDS)
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.MINIMIZE_WINDOW,
                app_name=app_name
            )
        
        # Maximize
        if any(kw in text for kw in self.MAXIMIZE_KEYWORDS):
            app_name = self._extract_app_name(text, self.MAXIMIZE_KEYWORDS)
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.MAXIMIZE_WINDOW,
                app_name=app_name
            )
        
        return None
    
    def _check_vision(self, text: str) -> Optional[Intent]:
        """Check if text indicates a vision/camera action."""
        
        # What do you see
        if any(kw in text for kw in self.WHAT_SEE_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.WHAT_DO_YOU_SEE
            )
        
        # Who is here
        if any(kw in text for kw in self.WHO_HERE_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.WHO_IS_HERE
            )
        
        # Count people
        if any(kw in text for kw in self.COUNT_PEOPLE_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.COUNT_PEOPLE
            )
        
        # Detect objects
        if any(kw in text for kw in self.DETECT_OBJECTS_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.DETECT_OBJECTS
            )
        
        # Take picture
        if any(kw in text for kw in self.TAKE_PICTURE_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.TAKE_PICTURE
            )
        
        return None
    
    def _check_system_control(self, text: str) -> Optional[Intent]:
        """Check if text indicates a system control action."""
        
        # Volume controls
        if any(kw in text for kw in self.VOLUME_UP_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.VOLUME_UP
            )
        
        if any(kw in text for kw in self.VOLUME_DOWN_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.VOLUME_DOWN
            )
        
        if any(kw in text for kw in self.SET_VOLUME_KEYWORDS):
            # Extract volume level
            level = self._extract_number(text)
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.SET_VOLUME,
                parameters={"level": level if level else 50}
            )
        
        if any(kw in text for kw in self.MUTE_KEYWORDS) and not any(kw in text for kw in self.UNMUTE_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.MUTE
            )
        
        if any(kw in text for kw in self.UNMUTE_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.UNMUTE
            )
        
        # Brightness controls
        if any(kw in text for kw in self.BRIGHTNESS_UP_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.BRIGHTNESS_UP
            )
        
        if any(kw in text for kw in self.BRIGHTNESS_DOWN_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.BRIGHTNESS_DOWN
            )
        
        # Do Not Disturb
        if any(kw in text for kw in self.DND_OFF_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.DISABLE_DND
            )
        
        if any(kw in text for kw in self.DND_ON_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.ENABLE_DND
            )
        
        # Battery status
        if any(kw in text for kw in self.BATTERY_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.GET_BATTERY
            )
        
        # Sleep system
        if any(kw in text for kw in self.SLEEP_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.SLEEP_SYSTEM
            )
        
        # Trash management
        if any(kw in text for kw in self.TRASH_COUNT_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.GET_TRASH_COUNT
            )
        
        if any(kw in text for kw in self.EMPTY_TRASH_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.EMPTY_TRASH
            )
        
        # Date and Time
        if any(kw in text for kw in self.DATE_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.GET_DATE
            )
        
        if any(kw in text for kw in self.TIME_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.GET_TIME
            )
        
        # Weather
        if any(kw in text for kw in self.WEATHER_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.GET_WEATHER
            )
        
        return None
    
    def _check_terminal_control(self, text: str) -> Optional[Intent]:
        """Check if text indicates a terminal control action."""
        
        # Open terminal
        if any(kw in text for kw in self.OPEN_TERMINAL_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.OPEN_TERMINAL
            )
        
        # Close current/active terminal (check first - more specific)
        if any(kw in text for kw in self.CLOSE_CURRENT_TERMINAL_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.CLOSE_CURRENT_TERMINAL
            )
        
        # Close terminal app
        if any(kw in text for kw in self.CLOSE_TERMINAL_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.CLOSE_TERMINAL
            )
        
        # New terminal window
        if any(kw in text for kw in self.NEW_TERMINAL_WINDOW_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.NEW_TERMINAL_WINDOW
            )
        
        # New terminal tab
        if any(kw in text for kw in self.NEW_TERMINAL_TAB_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.NEW_TERMINAL_TAB
            )
        
        # Run command in terminal
        if any(kw in text for kw in self.RUN_COMMAND_KEYWORDS):
            # Extract command
            command = text
            for kw in self.RUN_COMMAND_KEYWORDS:
                if kw in text:
                    parts = text.split(kw, 1)
                    if len(parts) > 1:
                        command = parts[1].strip()
                    break
            
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.RUN_TERMINAL_COMMAND,
                query=command
            )
        
        return None
    
    def _check_file_search(self, text: str) -> Optional[Intent]:
        """Check if text indicates a file search action."""
        
        # Recent files
        if any(kw in text for kw in self.RECENT_FILES_KEYWORDS):
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.RECENT_FILES
            )
        
        # File search
        if any(kw in text for kw in self.FILE_SEARCH_KEYWORDS):
            # Extract filename or query
            query = text
            for kw in self.FILE_SEARCH_KEYWORDS:
                if kw in text:
                    parts = text.split(kw, 1)
                    if len(parts) > 1:
                        query = parts[1].strip()
                        # Remove common words
                        query = query.replace("called ", "").replace("named ", "")
                    break
            
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.SEARCH_FILES,
                query=query
            )
        
        # Check if asking to open a specific file
        if "open file" in text or "open the file" in text:
            query = text.replace("open file", "").replace("open the file", "").strip()
            query = query.replace("called ", "").replace("named ", "")
            
            return Intent(
                intent_type=IntentType.DESKTOP_ACTION,
                action_type=ActionType.OPEN_FILE,
                query=query
            )
        
        return None
    
    def _check_web_search(self, text: str) -> Optional[Intent]:
        """Check if text is a web search request."""
        if any(kw in text for kw in self.SEARCH_KEYWORDS):
            # Extract query after search keyword
            query = text
            for kw in self.SEARCH_KEYWORDS:
                if kw in text:
                    parts = text.split(kw, 1)
                    if len(parts) > 1:
                        query = parts[1].strip()
                        # Remove "for" if it starts the query
                        if query.startswith("for "):
                            query = query[4:]
                    break
            
            return Intent(
                intent_type=IntentType.WEB_SEARCH,
                action_type=ActionType.SEARCH_WEB,
                query=query
            )
        
        return None
    
    def _is_question(self, text: str) -> bool:
        """Check if text is a question."""
        # Check for question keywords
        if any(kw in text for kw in self.QUESTION_KEYWORDS):
            return True
        
        # Check if ends with question mark
        if text.endswith("?"):
            return True
        
        return False
    
    def _extract_app_name(self, text: str, keywords: list) -> Optional[str]:
        """Extract app name from command text."""
        # Remove keyword and get remaining text
        for kw in keywords:
            if kw in text:
                parts = text.split(kw, 1)
                if len(parts) > 1:
                    app_text = parts[1].strip()
                    
                    # Clean up common words
                    app_text = app_text.replace("the ", "")
                    app_text = app_text.replace("app ", "")
                    app_text = app_text.replace("application ", "")
                    
                    # Take first few words as app name
                    words = app_text.split()
                    if words:
                        # Capitalize for proper app name
                        app_name = " ".join(words[:3])  # Max 3 words
                        return app_name.title()
        
        return None
    
    def _extract_position(self, text: str) -> Optional[str]:
        """Extract position from text (left, right, center, etc.)."""
        positions = {
            "left": "left",
            "right": "right",
            "center": "center",
            "centre": "center",
            "top": "top",
            "bottom": "bottom",
            "top left": "top-left",
            "top right": "top-right",
            "bottom left": "bottom-left",
            "bottom right": "bottom-right",
        }
        
        text_lower = text.lower()
        for key, value in positions.items():
            if key in text_lower:
                return value
        
        return None
    
    def _extract_number(self, text: str) -> Optional[int]:
        """Extract a number from text."""
        import re
        
        # Look for digits
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        
        # Look for word numbers
        word_to_num = {
            "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10, "twenty": 20, "thirty": 30, "forty": 40,
            "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80,
            "ninety": 90, "hundred": 100
        }
        
        words = text.lower().split()
        for word in words:
            if word in word_to_num:
                return word_to_num[word]
        
        return None


def test_classifier():
    """Test intent classifier."""
    classifier = IntentClassifier()
    
    test_cases = [
        "open safari",
        "close chrome",
        "move firefox to the right",
        "what's the weather today?",
        "search for python tutorials",
        "minimize the terminal",
        "how do I cook pasta?",
        "launch spotify",
    ]
    
    for text in test_cases:
        intent = classifier.classify(text)
        print(f"\n'{text}'")
        print(f"  Intent: {intent.intent_type.value}")
        if intent.action_type:
            print(f"  Action: {intent.action_type.value}")
        if intent.app_name:
            print(f"  App: {intent.app_name}")
        if intent.query:
            print(f"  Query: {intent.query}")
        if intent.parameters:
            print(f"  Parameters: {intent.parameters}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_classifier()
