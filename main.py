"""
Jheevis MLX - Voice Assistant
Full-featured AI assistant using MLX for Apple Silicon

Features:
- Speech-to-Text (Whisper MLX)
- Wake word detection ("hey jheevis")
- Natural language understanding (Llama 3.2)
- Desktop control (window management, app launching)
- Text-to-Speech (macOS built-in)
- Continuous conversation with context
"""

import logging
import sys
from enum import Enum
from typing import Optional
import numpy as np

# Local imports
import config
from stt.vad import VoiceActivityDetector
from stt.transcriber import WhisperTranscriber
from stt.wake_word import WakeWordDetector
from llm.model import MLXLanguageModel
from llm.history import ConversationHistory
from llm.intent import IntentClassifier, IntentType, ActionType
from desktop.screen import ScreenContext
from desktop.actions import ActionExecutor
from tts.synthesizer import TTSSynthesizer
from utils.audio import play_beep

# Arc Reactor UI
if config.ENABLE_ARC_REACTOR:
    from PyQt6.QtWidgets import QApplication
    from arc_reactor import ArcReactorUI

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(config.LOG_FILE) if config.LOG_TO_FILE else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)


class State(Enum):
    """Assistant states."""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"


class JheevisClient:
    """
    Main orchestrator for Jheevis voice assistant.
    Coordinates all components: VAD, STT, LLM, TTS, Desktop Control.
    """
    
    def __init__(self):
        """Initialize Jheevis client."""
        logger.info("="*60)
        logger.info("Initializing Jheevis MLX Voice Assistant")
        logger.info("="*60)
        
        self.state = State.IDLE
        
        # Initialize components
        logger.info("Loading components...")
        
        # Speech-to-Text
        self.vad = VoiceActivityDetector()
        self.transcriber = WhisperTranscriber()
        self.wake_word = WakeWordDetector()
        
        # Language Model
        self.llm = MLXLanguageModel()
        self.history = ConversationHistory()
        self.intent_classifier = IntentClassifier()
        
        # Desktop Control
        self.screen = ScreenContext()
        self.executor = ActionExecutor()
        
        # Text-to-Speech (MeloTTS for natural JARVIS-like voice)
        self.tts = TTSSynthesizer(use_melo=True)
        
        # Arc Reactor UI
        self.reactor_ui = None
        if config.ENABLE_ARC_REACTOR:
            try:
                self.qt_app = QApplication.instance()
                if self.qt_app is None:
                    self.qt_app = QApplication([])
                
                self.reactor_ui = ArcReactorUI(size=config.ARC_REACTOR_SIZE)
                self.reactor_ui.show()
                logger.info("✓ Arc Reactor UI initialized")
            except Exception as e:
                logger.warning(f"Arc Reactor UI failed to load: {e}")
                self.reactor_ui = None
        
        # State
        self.is_awake = not config.ENABLE_WAKE_WORD  # If no wake word, always awake
        self.should_stop = False
        
        logger.info("All components initialized")
        logger.info("="*60)
    
    def start(self):
        """Start the voice assistant."""
        logger.info("Starting Jheevis...")
        
        if config.ENABLE_WAKE_WORD:
            logger.info(f"Wake word: '{config.WAKE_WORD}'")
            self.speak("Good morning, sir. Jheevis initialized. Say the wake word to begin.")
        else:
            logger.info("Wake word disabled - always listening")
            self.speak("Good morning, sir. All systems operational. How may I assist you today?")
        
        # Set reactor to idle state
        if self.reactor_ui:
            self.reactor_ui.set_state('idle')
        
        # Define frame callback to process Qt events
        def process_qt_events(frame, is_speech):
            """Process Qt events on each audio frame"""
            if self.reactor_ui and hasattr(self, 'qt_app') and self.qt_app:
                self.qt_app.processEvents()
        
        # Start VAD loop
        try:
            self.vad.start_listening(
                on_speech_start=self._on_speech_start,
                on_speech_end=self._on_speech_end,
                on_frame=process_qt_events
            )
        except KeyboardInterrupt:
            logger.info("\n👋 Shutting down...")
        finally:
            if self.reactor_ui:
                self.reactor_ui.close()
    
    def _on_speech_start(self):
        """Callback when speech is detected."""
        if self.state == State.IDLE:
            self.state = State.LISTENING
            
            if self.reactor_ui:
                self.reactor_ui.set_state('listening')
            
            print("🎤 Listening...")  # Visual feedback for user
            
            if config.ENABLE_VOICE_FEEDBACK:
                play_beep()
            
            logger.debug("👂 Listening...")
    
    def _on_speech_end(self, audio: np.ndarray):
        """Callback when speech ends."""
        if self.state != State.LISTENING:
            return
        print("🔄 Processing...")  # Visual feedback for user
        
        self.state = State.PROCESSING
        if self.reactor_ui:
            self.reactor_ui.set_state('processing')
        
        logger.debug("🔄 Processing...")
        
        try:
            # Transcribe audio
            text = self.transcriber.transcribe(audio)
            
            if not text:
                logger.debug("No speech detected")
                self.state = State.IDLE
                return
            
            logger.info(f"User said: '{text}'")
            
            # Check for interrupt commands (highest priority)
            interrupt_keywords = ["stop it", "stop jheevis", "jheevis stop", "stop that"]
            if any(keyword in text.lower() for keyword in interrupt_keywords):
                logger.info("🛑 Interrupt detected - stopping execution")
                # Stop any ongoing TTS
                self.tts.stop()
                # Small delay to let audio system fully stop
                import time
                time.sleep(0.2)
                # Quick response
                self.speak("Oh, sorry sir.")
                self.state = State.IDLE
                if self.reactor_ui:
                    self.reactor_ui.set_state('idle')
                return
            
            # Check for wake word if not awake
            if not self.is_awake:
                if self.wake_word.detect(text):
                    self.is_awake = True
                    self.speak("Yes?")
                    logger.info("✅ Wake word detected - now awake")
                    
                    # Extract command after wake word
                    command = self.wake_word.extract_command(text)
                    if command and command.lower() not in ["hey jheevis", "jheevis", "hey computer"]:
                        # Process the command
                        self._process_command(command)
                    else:
                        # Just wake word, wait for next command
                        pass
                else:
                    logger.debug("❌ No wake word detected")
                
                self.state = State.IDLE
                return
            
            # Process command if awake
            self._process_command(text)
        
        except Exception as e:
            logger.error(f"Error processing speech: {e}", exc_info=True)
            if self.reactor_ui:
                self.reactor_ui.set_state('error')
                import time
                time.sleep(1)  # Show error state briefly
            self.speak("Sorry, I encountered an error.")
            self.state = State.ERROR
        
        finally:
            # Reset to idle
            self.state = State.IDLE
            if self.reactor_ui:
                self.reactor_ui.set_state('idle')
    
    def _process_command(self, text: str):
        """
        Process user command.
        
        Args:
            text: Transcribed user command
        """
        # Check for interrupt commands (highest priority)
        interrupt_keywords = ["stop it", "stop jheevis", "jheevis stop", "stop that", "ok stop", "please stop", "enough", "that's enough"]
        if any(keyword in text.lower() for keyword in interrupt_keywords):
            logger.info("🛑 Interrupt detected - stopping execution")
            self.tts.stop()
            # Small delay to let audio system fully stop
            import time
            time.sleep(0.2)
            self.speak("Oh, sorry sir.")
            return
        
        # Check for exit commands
        if any(word in text.lower() for word in ["goodbye", "exit", "quit", "stop listening"]):
            self.speak("Goodbye!")
            self.should_stop = True
            return
        
        # Check for sleep command
        if config.ENABLE_WAKE_WORD and any(word in text.lower() for word in ["go to sleep", "sleep", "stop"]):
            self.is_awake = False
            self.speak("Going to sleep. Say the wake word when you need me.")
            logger.info("💤 Going to sleep")
            return
        
        # Classify intent
        intent = self.intent_classifier.classify(text)
        logger.info(f"Intent: {intent.intent_type.value}")
        
        # Handle based on intent type
        if intent.intent_type == IntentType.DESKTOP_ACTION:
            self._handle_desktop_action(intent)
        
        elif intent.intent_type == IntentType.WEB_SEARCH:
            self._handle_web_search(intent)
        
        elif intent.intent_type == IntentType.CONVERSATION:
            self._handle_conversation(text)
        
        else:
            self._handle_conversation(text)
    
    def _handle_desktop_action(self, intent):
        """Handle desktop control actions."""
        action = intent.action_type
        app_name = intent.app_name
        
        logger.info(f"Desktop action: {action.value} on {app_name}")
        
        success = False
        response = ""
        
        # Window Management Actions
        if action == ActionType.OPEN_APP:
            success = self.executor.open_app(app_name)
            response = f"Opening {app_name}" if success else f"Sorry, I couldn't open {app_name}"
        
        elif action == ActionType.CLOSE_APP:
            success = self.executor.close_app(app_name)
            response = f"Closing {app_name}" if success else f"Sorry, I couldn't close {app_name}"
        
        elif action == ActionType.MOVE_WINDOW:
            position = intent.parameters.get("position")
            success = self.executor.move_window(app_name, position=position)
            response = f"Moving {app_name} to {position}" if success else f"Sorry, I couldn't move {app_name}"
        
        elif action == ActionType.MINIMIZE_WINDOW:
            success = self.executor.minimize_window(app_name)
            response = f"Minimizing {app_name}" if success else f"Sorry, I couldn't minimize {app_name}"
        
        elif action == ActionType.MAXIMIZE_WINDOW:
            success = self.executor.maximize_window(app_name)
            response = f"Maximizing {app_name}" if success else f"Sorry, I couldn't maximize {app_name}"
        
        # Volume Control Actions
        elif action == ActionType.VOLUME_UP:
            success = self.executor.volume_up()
            response = "Turning up the volume" if success else "Sorry, I couldn't change the volume"
        
        elif action == ActionType.VOLUME_DOWN:
            success = self.executor.volume_down()
            response = "Turning down the volume" if success else "Sorry, I couldn't change the volume"
        
        elif action == ActionType.SET_VOLUME:
            level = intent.parameters.get("level", 50)
            success = self.executor.set_volume(level)
            response = f"Setting volume to {level}" if success else "Sorry, I couldn't set the volume"
        
        elif action == ActionType.MUTE:
            success = self.executor.mute()
            response = "Muting" if success else "Sorry, I couldn't mute"
        
        elif action == ActionType.UNMUTE:
            success = self.executor.unmute()
            response = "Unmuting" if success else "Sorry, I couldn't unmute"
        
        # Brightness Control Actions
        elif action == ActionType.BRIGHTNESS_UP:
            success = self.executor.brightness_up()
            response = "Increasing brightness" if success else "Sorry, I couldn't change brightness"
        
        elif action == ActionType.BRIGHTNESS_DOWN:
            success = self.executor.brightness_down()
            response = "Decreasing brightness" if success else "Sorry, I couldn't change brightness"
        
        # Do Not Disturb Actions
        elif action == ActionType.ENABLE_DND:
            success = self.executor.enable_dnd()
            response = "Enabling Do Not Disturb" if success else "Sorry, I couldn't enable Do Not Disturb"
        
        elif action == ActionType.DISABLE_DND:
            success = self.executor.disable_dnd()
            response = "Disabling Do Not Disturb" if success else "Sorry, I couldn't disable Do Not Disturb"
        
        # System Info Actions
        elif action == ActionType.GET_BATTERY:
            battery_info = self.executor.get_battery_status()
            if battery_info and battery_info.get('percentage'):
                percent = battery_info['percentage']
                charging = "charging" if battery_info.get('charging') else "not charging"
                response = f"Battery is at {percent}% and {charging}"
                success = True
            else:
                response = "Sorry, I couldn't get battery status"
        
        elif action == ActionType.SLEEP_SYSTEM:
            response = "Putting the system to sleep"
            self.speak(response)
            success = self.executor.sleep_system()
            return  # Exit early since system is sleeping
        
        # Trash Management Actions
        elif action == ActionType.GET_TRASH_COUNT:
            count = self.executor.get_trash_count()
            if count is not None:
                if count == 0:
                    response = "The trash is empty"
                elif count == 1:
                    response = "There is 1 item in the trash"
                else:
                    response = f"There are {count} items in the trash"
                success = True
            else:
                response = "Sorry, I couldn't check the trash"
        
        elif action == ActionType.EMPTY_TRASH:
            count = self.executor.get_trash_count()
            if count and count > 0:
                response = f"Emptying {count} items from trash"
                self.speak(response)
                success = self.executor.empty_trash()
                if success:
                    response = "Trash emptied successfully"
                else:
                    response = "Sorry, I couldn't empty the trash"
            else:
                response = "The trash is already empty"
                success = True
        
        # Date & Time Actions
        elif action == ActionType.GET_DATE:
            date_str = self.executor.get_current_date()
            response = f"Today is {date_str}"
            success = True
        
        elif action == ActionType.GET_TIME:
            time_str = self.executor.get_current_time()
            response = f"It's {time_str}"
            success = True
        
        # Weather Action
        elif action == ActionType.GET_WEATHER:
            weather = self.executor.get_weather()
            if weather and weather.get('temperature_c'):
                location = weather.get('location', 'your location')
                temp_c = weather['temperature_c']
                temp_f = weather['temperature_f']
                condition = weather['condition']
                response = f"In {location}, it's {temp_c}°C or {temp_f}°F with {condition.lower()}"
                success = True
            else:
                response = "Sorry, I couldn't get the weather information"
        
        # File Search Actions
        elif action == ActionType.SEARCH_FILES:
            query = intent.query
            files = self.executor.search_files(query, limit=5)
            
            if files:
                if len(files) == 1:
                    response = f"Found {files[0]['name']} in {files[0]['directory']}"
                else:
                    file_names = [f['name'] for f in files[:3]]
                    response = f"Found {len(files)} files: {', '.join(file_names)}"
                success = True
            else:
                response = f"Sorry, I couldn't find any files matching {query}"
        
        elif action == ActionType.OPEN_FILE:
            filename = intent.query
            success = self.executor.open_file_by_name(filename)
            response = f"Opening {filename}" if success else f"Sorry, I couldn't find {filename}"
        
        elif action == ActionType.RECENT_FILES:
            files = self.executor.get_recent_files(days=7, limit=5)
            
            if files:
                file_names = [f['name'] for f in files[:3]]
                response = f"Your recent files include: {', '.join(file_names)}"
                success = True
            else:
                response = "I couldn't find any recent files"
        
        # Terminal Control Actions
        elif action == ActionType.OPEN_TERMINAL:
            success = self.executor.open_terminal()
            response = "Opening Terminal" if success else "Sorry, I couldn't open Terminal"
        
        elif action == ActionType.CLOSE_TERMINAL:
            success = self.executor.close_terminal()
            response = "Closing Terminal" if success else "Sorry, I couldn't close Terminal"
        
        elif action == ActionType.CLOSE_CURRENT_TERMINAL:
            success = self.executor.close_current_terminal()
            response = "Closing current Terminal window" if success else "Sorry, I couldn't close the Terminal window"
        
        elif action == ActionType.NEW_TERMINAL_WINDOW:
            success = self.executor.new_terminal_window()
            response = "Opening new Terminal window" if success else "Sorry, I couldn't open a new Terminal window"
        
        elif action == ActionType.NEW_TERMINAL_TAB:
            success = self.executor.new_terminal_tab()
            response = "Opening new Terminal tab" if success else "Sorry, I couldn't open a new Terminal tab"
        
        elif action == ActionType.RUN_TERMINAL_COMMAND:
            command = intent.query
            success = self.executor.run_terminal_command(command)
            response = f"Running command: {command}" if success else f"Sorry, I couldn't run the command"
        
        # Vision/Camera Actions
        elif action == ActionType.WHAT_DO_YOU_SEE:
            result = self.executor.what_do_you_see()
            response = result.get('description', "I couldn't see anything")
            success = result.get('success', False)
        
        elif action == ActionType.WHO_IS_HERE:
            result = self.executor.who_is_here()
            response = result.get('message', "I couldn't check")
            success = result.get('success', False)
        
        elif action == ActionType.COUNT_PEOPLE:
            result = self.executor.count_people()
            response = result.get('message', "I couldn't count people")
            success = result.get('success', False)
        
        elif action == ActionType.DETECT_OBJECTS:
            result = self.executor.detect_objects()
            response = result.get('message', "I couldn't detect objects")
            success = result.get('success', False)
        
        elif action == ActionType.TAKE_PICTURE:
            result = self.executor.take_picture()
            response = result.get('message', "I couldn't take a picture")
            success = result.get('success', False)
        
        # Enhanced Vision Actions
        elif action == ActionType.ANALYZE_SCENE:
            result = self.executor.analyze_scene_detailed()
            response = result.get('message', "I couldn't analyze the scene")
            success = result.get('success', False)
        
        elif action == ActionType.WHAT_AM_I_DOING:
            result = self.executor.what_do_you_see()
            # Focus on activity in response
            activity = result.get('activity', 'unknown')
            if activity in ['working', 'eating', 'reading', 'phone_use']:
                activity_name = activity.replace('_', ' ')
                response = f"You appear to be {activity_name}, sir."
            else:
                response = result.get('description', "I couldn't determine your activity")
            success = result.get('success', False)
        
        elif action == ActionType.GET_ACTIVITY:
            result = self.executor.get_activity_summary()
            response = result.get('message', "I don't have any activity history yet")
            success = result.get('success', False)
        
        # Speak response
        self.speak(response)
        
        # Add to history
        self.history.add_user_message(f"[Action: {action.value}]")
        self.history.add_assistant_message(response)
        
        # Offer proactive suggestion if enabled and action was successful
        if success and config.ENABLE_PROACTIVE_SUGGESTIONS:
            self._maybe_offer_suggestion(action, intent)
    
    def _handle_web_search(self, intent):
        """Handle web search."""
        query = intent.query
        logger.info(f"Web search: '{query}'")
        
        success = self.executor.search_web(query)
        
        if success:
            response = f"Searching for {query}"
        else:
            response = f"Sorry, I couldn't search for {query}"
        
        self.speak(response)
        self.history.add_user_message(f"Search for: {query}")
        self.history.add_assistant_message(response)
    
    def _maybe_offer_suggestion(self, action: ActionType, intent):
        """
        Offer proactive suggestions after completing an action.
        
        Args:
            action: The action that was just completed
            intent: The intent object with action details
        """
        import random
        
        # Only suggest sometimes (based on config)
        if random.random() > config.PROACTIVE_SUGGESTION_CHANCE:
            return
        
        # Define contextual suggestions based on action
        suggestions = {
            ActionType.GET_TIME: [
                "Would you like me to check the weather as well, sir?",
                "Shall I tell you today's date as well?"
            ],
            ActionType.GET_DATE: [
                "Would you like to know the time as well, sir?",
                "Shall I check the weather forecast?"
            ],
            ActionType.GET_WEATHER: [
                "Would you like me to check the time as well?",
                "Shall I tell you the current date?"
            ],
            ActionType.OPEN_APP: [
                "Shall I maximize the window for you, sir?",
                "Would you like me to move it to a specific position?"
            ],
            ActionType.VOLUME_UP: [
                "Would you like me to adjust the brightness as well?",
            ],
            ActionType.VOLUME_DOWN: [
                "Would you like me to adjust the brightness as well?",
            ],
            ActionType.SET_BRIGHTNESS: [
                "Shall I adjust the volume as well, sir?",
            ],
            ActionType.WHAT_DO_YOU_SEE: [
                "Would you like me to take a picture of this, sir?",
                "Shall I count how many people are present?"
            ],
            ActionType.WHO_IS_HERE: [
                "Would you like me to take a picture, sir?",
            ],
            ActionType.GET_TRASH_COUNT: [
                "Shall I empty the trash for you, sir?",
            ],
            ActionType.FIND_FILE: [
                "Would you like me to open it for you?",
            ],
            ActionType.OPEN_TERMINAL: [
                "Would you like me to run a specific command, sir?",
            ]
        }
        
        # Get suggestions for this action
        action_suggestions = suggestions.get(action, [])
        
        if action_suggestions:
            # Pick a random suggestion
            suggestion = random.choice(action_suggestions)
            
            # Small delay before speaking suggestion (feels more natural)
            import time
            time.sleep(0.3)
            
            # Speak the suggestion
            self.speak(suggestion)
            
            # Add to history
            self.history.add_assistant_message(suggestion)
            
            logger.debug(f"Offered proactive suggestion: {suggestion}")
    
    def _handle_conversation(self, text: str):
        """Handle conversational interaction."""
        logger.info("Conversational response")
        
        # Add user message to history
        self.history.add_user_message(text)
        
        # Get context for screen understanding
        screen_context = ""
        if config.ENABLE_SCREEN_UNDERSTANDING:
            screen_context = f"\n\nCurrent screen state: {self.screen.describe_screen()}"
        
        # Get conversation count to inform LLM about context
        exchange_count = self.history.get_conversation_count()
        context_note = ""
        if exchange_count > 0:
            context_note = f"\n\n[Note: This is exchange #{exchange_count + 1} in an ongoing conversation. You have full context of previous messages.]"
        
        # Generate response using LLM
        messages = self.history.get_messages()
        
        # Add context notes to last message if available
        if messages:
            additional_context = context_note + screen_context
            if additional_context:
                messages[-1]["content"] += additional_context
        
        response = self.llm.chat_completion(messages)
        
        # Clean up response
        response = response.strip()
        
        # Limit response length for natural speech
        sentences = response.split('. ')
        if len(sentences) > 3:
            response = '. '.join(sentences[:3]) + '.'
        
        logger.info(f"Response: '{response}'")
        
        # Add to history
        self.history.add_assistant_message(response)
        
        # Speak response
        self.speak(response)
    
    def speak(self, text: str):
        """
        Speak text using TTS.
        
        Args:
            text: Text to speak
        """
        if not text:
            return
        
        self.state = State.SPEAKING
        if self.reactor_ui:
            self.reactor_ui.set_state('speaking')
        
        logger.debug(f"🔊 Speaking: '{text}'")
        
        self.tts.speak(text)
        
        self.state = State.IDLE
        if self.reactor_ui:
            self.reactor_ui.set_state('idle')
    
    def stop(self):
        """Stop the assistant."""
        logger.info("Stopping Jheevis...")
        self.vad.stop_listening()
        self.should_stop = True


def main():
    """Main entry point."""
    print("""
    ╔════════════════════════════════════════╗
    ║         JHEEVIS MLX ASSISTANT          ║
    ║  Voice-Controlled AI for macOS         ║
    ╚════════════════════════════════════════╝
    """)
    
    try:
        # Create and start client
        client = JheevisClient()
        client.start()
    
    except KeyboardInterrupt:
        logger.info("\n\nReceived interrupt signal")
        print("\n\n👋 Goodbye!")
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
