"""
Configuration for Jheevis MLX Voice Assistant
"""

# =========================
# MODEL CONFIGURATION
# =========================

# Speech-to-Text (Whisper MLX)
WHISPER_MODEL = "mlx-community/whisper-large-v3-turbo"
WHISPER_LANGUAGE = "en"  # or None for auto-detection

# Large Language Model (MLX LLM)
LLM_MODEL = "mlx-community/Llama-3.2-3B-Instruct-4bit"
LLM_MAX_TOKENS = 512
LLM_TEMPERATURE = 0.7
LLM_TOP_P = 0.9

# Text-to-Speech (MeloTTS)
TTS_LANGUAGE = "EN"  # Options: EN, EN_US, EN_AU, EN_NEWEST, etc.
TTS_SPEAKER = "EN-US"  # EN-BR for British accent (JARVIS-like), or EN-US for American
TTS_SPEED = 0.9  # 0.9 = slower, more sophisticated like JARVIS (0.8-1.2 range)
TTS_SAMPLE_RATE = 44100


# =========================
# AUDIO CONFIGURATION
# =========================

# Microphone Input
SAMPLE_RATE = 16000  # Hz (standard for Whisper)
CHANNELS = 1  # Mono
CHUNK_SIZE = 160  # 10ms chunks for VAD (16000 Hz / 100)
AUDIO_FORMAT = "int16"

# Voice Activity Detection (WebRTC VAD)
VAD_MODE = 2  # Aggressiveness mode (0-3) - balanced setting
VAD_FRAME_DURATION = 10  # ms (must be 10, 20, or 30)
VAD_PADDING_DURATION = 400  # ms of silence before stopping recording
VAD_MIN_AUDIO_LENGTH = 0.6  # seconds (minimum speech duration - balanced)

# Audio Playback
PLAYBACK_SAMPLE_RATE = 44100  # Hz (for TTS output)


# =========================
# WAKE WORD CONFIGURATION
# =========================

WAKE_WORD = "hey jheevis"  # Set to None to disable wake word
WAKE_WORD_ALTERNATIVES = ["jheevis", "hey computer"]
WAKE_WORD_THRESHOLD = 0.8  # Similarity threshold for fuzzy matching


# =========================
# CONVERSATION CONFIGURATION
# =========================

# System Prompt for LLM
SYSTEM_PROMPT = """You are Jheevis, a sophisticated British AI assistant inspired by JARVIS from Iron Man.
You're polite, professional, calm, and occasionally charming with dry British wit.
Speak with understated elegance - you're helpful but never servile, intelligent but never condescending.
Use proper grammar and British phrases occasionally ("Certainly, sir", "Right away", "Very well").
Keep responses concise (1-2 sentences) but refined. Be warm yet professional.
When performing actions, acknowledge them with calm efficiency: "Opening Safari now" or "Adjusting volume, sir".
Avoid American slang or overly casual language. Think: calm, capable, trustworthy.

IMPORTANT: Do NOT answer questions about current date, time, weather, or trash count - these are handled by system actions.
If asked, the system will provide the real-time information automatically."""

# Conversation History
MAX_HISTORY_LENGTH = 20  # Maximum number of messages to keep in context
SAVE_HISTORY = False  # Whether to persist history to disk


# =========================
# DESKTOP CONTROL CONFIGURATION
# =========================

# Window Management
WINDOW_ANIMATION_DURATION = 0.3  # seconds
WINDOW_ANIMATION_STEPS = 20

# App Names Fuzzy Matching
FUZZY_MATCH_THRESHOLD = 0.6  # Minimum similarity score
FUZZY_MATCH_CUTOFF = 3  # Max number of suggestions


# =========================
# LOGGING CONFIGURATION
# =========================

LOG_LEVEL = "DEBUG"  # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True
LOG_FILE = "jheevis.log"


# =========================
# PERFORMANCE CONFIGURATION
# =========================

# MLX Settings
USE_FLOAT16 = True  # Use FP16 for faster inference on Apple Silicon
CACHE_MODELS = True  # Cache loaded models in memory


# =========================
# FEATURE FLAGS
# =========================

ENABLE_WAKE_WORD = False  # Disabled for easier testing - always listening
ENABLE_DESKTOP_CONTROL = True
ENABLE_SCREEN_UNDERSTANDING = True
ENABLE_VOICE_FEEDBACK = False  # Disabled - no beep sound
ENABLE_TTS = True  # Disable for text-only mode


# =========================
# ARC REACTOR UI
# =========================

ENABLE_ARC_REACTOR = True  # Show Arc Reactor UI (JARVIS-style visual indicator)
ARC_REACTOR_SIZE = 300  # Window size in pixels
ARC_REACTOR_POSITION = "bottom-right"  # Position on screen
