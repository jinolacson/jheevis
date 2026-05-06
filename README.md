# Jheevis MLX - Voice Assistant for macOS

**A JARVIS-inspired, 100% offline voice assistant built with Apple MLX for Apple Silicon.**

Jheevis is a full-featured desktop AI assistant that runs entirely on-device—no cloud, no API calls, no compromises on privacy. Built with Apple's MLX framework, it leverages the Neural Engine in M-series chips for fast, powerful AI capabilities including speech recognition, natural language understanding, computer vision, and JARVIS-style voice synthesis.

## ✨ What Makes Jheevis Special

- **🔒 100% Private**: All AI processing happens locally on your Mac—no data leaves your device
- **🎤 JARVIS Voice**: British professional tone using MeloTTS, matching Iron Man's AI assistant
- **👁️ Computer Vision**: Can see and identify people/objects through your camera
- **🛠️ Full System Control**: Control volume, brightness, apps, files, terminal—everything by voice
- **⚡ Apple Silicon Optimized**: Built specifically for M1/M2/M3/M4 with Metal acceleration
- **🌐 Real-Time Data**: Accurate weather, date, time—no LLM hallucinations

**Quick Example:**
```
You: "Hey Jheevis"
Jheevis: "Yes, sir?"
You: "What do you see?"
Jheevis: "I can see one person, a laptop, and a coffee cup on the desk."
You: "What's the weather?"
Jheevis: "In San Francisco, it's 18°C with partly cloudy skies."
You: "Open Terminal and run git status"
Jheevis: "Opening Terminal and executing git status."
```

## Features

✅ **Speech-to-Text**: Whisper MLX (large-v3-turbo) for fast, accurate transcription  
✅ **Wake Word Detection**: Activate with "Hey Jheevis" or custom phrase  
✅ **Natural Language Understanding**: Llama 3.2 3B (4-bit quantized) for conversation  
✅ **Desktop Control**: Open/close apps, move windows, web search  
✅ **Screen Understanding**: Knows what apps are running and visible  
✅ **System Control**: Volume, brightness, Do Not Disturb, battery status, sleep  
✅ **File Search**: Find files using Spotlight, open files, view recent files  
✅ **Terminal Control**: Open/close Terminal, create windows/tabs, run commands  
✅ **Computer Vision**: See and identify people/objects using camera (YOLOv11)  
✅ **Real-Time Data**: Accurate date, time, weather, trash count (no hallucinations)  
✅ **Text-to-Speech**: MeloTTS JARVIS-style British voice (switchable to macOS voices)  
✅ **Continuous Conversation**: Multi-turn dialogue with context  
✅ **100% Offline**: All processing on-device, no cloud required  
✅ **Apple Silicon Optimized**: Leverages MLX for Metal acceleration  

> **NEW:** System Control and File Search features added! See [docs/NEW_FEATURES.md](docs/NEW_FEATURES.md) for details.  
> **NEW:** Terminal Control features added! See [docs/TERMINAL_CONTROL.md](docs/TERMINAL_CONTROL.md).  
> **NEW:** Computer Vision features added! Jheevis can now see and identify objects/people. See [docs/VISION_FEATURES.md](docs/VISION_FEATURES.md).  
> **NEW:** MeloTTS JARVIS voice integrated! British professional tone matching Iron Man's AI assistant.  

## Requirements

- **macOS** (Apple Silicon recommended: M1/M2/M3/M4)
- **Python 3.11.9** (recommended) - native ARM, not Rosetta
  - Python 3.9-3.12 should work
  - **Avoid Python 3.14+** (missing _lzma module in some builds)
- **Microphone and speakers/headphones**
- **Camera** (for vision features)
- **~6GB disk space** (models + dependencies)
- **8GB+ RAM** (16GB recommended)

## Installation

### 1. Install Python (Using pyenv - Recommended)

If you don't have pyenv, install it first:

```bash
# Install pyenv
brew install pyenv

# Add to your shell profile (~/.zshrc or ~/.bash_profile)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc
```

Install Python 3.11.9:

```bash
# Install Python 3.11.9 (tested and working)
pyenv install 3.11.9

# Set it for this project
cd /path/to/jheevis
pyenv local 3.11.9

# Verify native ARM installation
python -c "import platform; print(platform.processor())"
# Should output: "arm"
```

**Alternative: Using Conda**

```bash
# Create native ARM environment
CONDA_SUBDIR=osx-arm64 conda create -n jheevis python=3.11 -c conda-forge
conda activate jheevis
```

### 2. Create Virtual Environment

```bash
cd jheevis
python -m venv venv
source venv/bin/activate  # On macOS/Linux
```

**Verify you're in the venv:**
```bash
which python
# Should show: /path/to/jheevis/venv/bin/python
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**⏱️ Installation Time:**
- First time: 10-20 minutes (large ML packages)
- Includes: MLX, Whisper, Transformers, PyTorch, YOLO, MeloTTS, PyObjC

**Packages Installed:**
- `mlx` - Apple Silicon ML framework
- `mlx-lm` - Language models for MLX
- `mlx-whisper` - Speech recognition
- `ultralytics` - YOLOv11 object detection
- `transformers` - Hugging Face models
- `melotts` - JARVIS-style voice synthesis
- `pyobjc` - macOS system control
- And more...

### 4. Download NLTK Data (Required for MeloTTS)

```bash
python -m nltk.downloader averaged_perceptron_tagger_eng cmudict
```

### 5. Grant System Permissions

**Required Permissions:**

1. **Microphone Access**
   - System Settings → Privacy & Security → Microphone
   - Enable for Terminal/iTerm/VS Code (wherever you run Jheevis)

2. **Accessibility Access** (for system control)
   - System Settings → Privacy & Security → Accessibility
   - Add Terminal/iTerm/VS Code
   - This allows volume, brightness, window control, etc.

3. **Camera Access** (for vision features)
   - System Settings → Privacy & Security → Camera
   - Enable for Terminal/iTerm/VS Code
   - Required for "What do you see?" commands

**macOS will prompt for these on first use - click "Allow"**

### 6. Download Models (First Run)

On first run, Jheevis will download AI models (~4-6GB):

```bash
python main.py
```

**Models Downloaded:**
- **Whisper Large-v3-Turbo** (~1.5GB) - Speech-to-text
- **Llama 3.2 3B 4-bit** (~1.8GB) - Language understanding
- **YOLOv11n** (~6MB) - Object detection
- **MeloTTS Models** (~300MB) - Voice synthesis

**Storage Location:** `~/.cache/huggingface/hub/`

**⏱️ Download Time:** 5-15 minutes depending on internet speed

## Quick Start

### Running Jheevis

```bash
# Activate virtual environment
source venv/bin/activate

# Run assistant
python main.py
```

**First Run:**
- Models download automatically
- Initialization takes ~30-60 seconds
- You'll see: "Listening for wake word..."

### Basic Commands

**Wake up Jheevis:**
```
"Hey Jheevis"
```

**Try these commands:**

**System Control:**
```
"Volume up"
"Brightness down"
"What's my battery level?"
"What time is it?"
"What's the weather?"
"How many items in trash?"
```

**File & Apps:**
```
"Open Safari"
"Find file config.py"
"Recent files"
"Close Chrome"
```

**Terminal:**
```
"Open Terminal"
"New Terminal window"
"Run command ls -la"
```

**Computer Vision:**
```
"What do you see?"
"Who is here?"
"How many people?"
"Take a picture"
```

**Conversation:**
```
"What's the capital of France?"
"Tell me a joke"
"Explain machine learning"
```

### Voice Settings

**Default Voice:** MeloTTS British (JARVIS-style)

To switch back to macOS voices, edit `main.py`:
```python
synthesizer = TTSSynthesizer(use_melo=False)  # Change to False
```

**Available MeloTTS Voices:**
- `EN-BR` - British (JARVIS-style, default)
- `EN-US` - American
- `EN-AU` - Australian
- `EN-INDIA` - Indian

Edit in `config.py`:
```python
TTS_SPEAKER = "EN-BR"  # Change to desired accent
TTS_SPEED = 0.9        # 0.5 (slow) to 2.0 (fast)
```

## Usage

### Wake Word

By default, Jheevis uses **"Hey Jheevis"** as the wake word. Alternatives:
- "Jheevis"
- "Hey computer"

To disable wake word (always listening), edit [config.py](config.py):
```python
ENABLE_WAKE_WORD = False
```

## 🎯 All Voice Commands

### System Control

| Command Examples | Action |
|-----------------|--------|
| "Volume up" / "Louder" / "Turn up" / "Increase volume" | Increase system volume |
| "Volume down" / "Quieter" / "Turn down" / "Lower volume" / "Decrease volume" | Decrease system volume |
| "Set volume to 50" / "Volume to 75" / "Volume at 30" | Set volume to specific level (0-100) |
| "Mute" / "Silence" | Mute system audio |
| "Unmute" / "Unsilence" | Unmute system audio |
| "Brightness up" / "Brighter" / "Brighten" / "Increase brightness" | Increase screen brightness |
| "Brightness down" / "Dimmer" / "Dim" / "Decrease brightness" | Decrease brightness |
| "Enable do not disturb" / "Turn on do not disturb" / "DND on" | Enable Do Not Disturb mode |
| "Disable do not disturb" / "Turn off do not disturb" / "DND off" | Disable Do Not Disturb mode |
| "Battery" / "Battery status" / "Battery level" / "How much battery" | Check battery status |
| "Sleep" / "Go to sleep" / "Put to sleep" | Put system to sleep |
| "How many items in trash?" / "Trash count" / "Check trash" / "How full is trash?" | Check number of items in trash |
| "Empty trash" / "Clear trash" / "Delete trash" | Empty the trash bin |
| "What's the date?" / "What date is it?" / "Today's date" / "What day is it?" | Get current date |
| "What time is it?" / "What's the time?" / "Current time" | Get current time |
| "Weather" / "What's the weather?" / "How's the weather?" / "Temperature" | Get current weather |

### File Operations

| Command Examples | Action |
|-----------------|--------|
| "Find file config.py" / "Locate file main.py" / "Where is file app.py" / "Search file test.py" | Search for a specific file |
| "Open file main.py" / "Open file requirements.txt" | Find and open a file |
| "Recent files" / "Recently opened" / "Recent documents" / "Latest files" | Show recently modified files |

### Terminal Control

| Command Examples | Action |
|-----------------|--------|
| "Open Terminal" / "Launch Terminal" / "Start Terminal" | Launch Terminal application |
| "Close Terminal" / "Quit Terminal" | Quit Terminal application (all windows) |
| "Close this terminal" / "Close current terminal" / "Exit terminal" / "Close active terminal" / "Close this window" | Close current active Terminal window/tab |
| "New terminal window" / "Open new terminal window" / "Create terminal window" | Create a new Terminal window |
| "New terminal tab" / "New tab in terminal" / "Open terminal tab" | Create a new tab in Terminal |
| "Run command ls -la" / "Execute npm start" / "Run in terminal python app.py" | Execute command in new Terminal window |

### Computer Vision (Camera)

| Command Examples | Action |
|-----------------|--------|
| "What do you see?" / "What can you see?" / "What's in front?" / "Describe what you see" / "Look around" / "What are you looking at?" | Describe visible objects and people |
| "Who is here?" / "Who's here?" / "Is anyone here?" / "Who is in the room?" / "Is someone here?" | Detect if people are present |
| "How many people?" / "Count people" / "How many persons?" / "Number of people" | Count people in camera view |
| "What objects?" / "Detect objects" / "What things?" / "Identify objects" | List all detected objects |
| "Take picture" / "Take photo" / "Capture image" / "Take snapshot" / "Take a picture" | Capture and save a photo |

### Desktop/App Control

| Command Examples | Action |
|-----------------|--------|
| "Open Safari" / "Launch Chrome" / "Start Firefox" / "Run Spotify" / "Show Finder" | Launch or activate application |
| "Close Chrome" / "Quit Safari" / "Exit Terminal" / "Kill Spotify" | Quit application |
| "Move Chrome to the right" / "Move Firefox left" / "Position Safari center" | Reposition window (left/right/center/top/bottom/top-left/top-right/bottom-left/bottom-right) |
| "Minimize Terminal" / "Hide Finder" | Minimize window |
| "Maximize Spotify" / "Full screen Safari" / "Fullscreen Chrome" | Maximize window to fullscreen |
| "Resize Chrome make bigger" / "Make Safari smaller" / "Expand window" / "Shrink Terminal" | Resize window |
| "Screenshot" | Take a screenshot |
| "Type hello world" / "Write some text" / "Enter text" | Type text in active window |

### Web Search

| Command Examples | Action |
|-----------------|--------|
| "Search for Python tutorials" / "Google MLX documentation" / "Look up recipe for pasta" / "Find online machine learning" | Search the web |

### Conversational Queries

Ask Jheevis anything:
- "What's the weather today?"
- "What's the capital of France?"
- "How do I cook rice?"
- "Tell me a joke"
- "Explain quantum physics"
- "What apps are currently running?"
- "What time is it?"

### Assistant Control

| Command | Action |
|---------|--------|
| "Hey Jheevis" | Wake word - activate listening |
| "Go to sleep" | Sleep mode (requires wake word to reactivate) |
| "Goodbye" / "Quit" / "Exit" | Shut down assistant |

---

**💡 Pro Tips:**
- Commands are **flexible** - you can phrase them naturally! For example:
  - "Turn up the volume" = "Make it louder" = "Volume up"
  - "Is someone here?" = "Who's in the room?" = "Who is here?"
- Use **natural language** - Jheevis understands context and variations
- For **file operations**, you can use partial names: "Find file config" will find "config.py"
- For **apps**, fuzzy matching works: "Open Chrome" works even if the exact name is "Google Chrome"
- **Camera commands** require camera permissions - grant access when prompted
- **Weather data** uses wttr.in API - no API key needed, works offline-first

**📖 For detailed documentation:**
- System Control & File Search: [docs/NEW_FEATURES.md](docs/NEW_FEATURES.md)
- Terminal Control: [docs/TERMINAL_CONTROL.md](docs/TERMINAL_CONTROL.md)  
- Computer Vision: [docs/VISION_FEATURES.md](docs/VISION_FEATURES.md)
- Future Plans: [docs/IMPROVEMENT_PLAN.md](docs/IMPROVEMENT_PLAN.md)

## Configuration

Edit [config.py](config.py) to customize:

### Models

```python
WHISPER_MODEL = "mlx-community/whisper-large-v3-turbo"  # STT model
LLM_MODEL = "mlx-community/Llama-3.2-3B-Instruct-4bit"  # LLM model
```

**Alternative models**:
- Whisper: `whisper-medium`, `whisper-small` (faster, less accurate)
- LLM: `Phi-3-mini-4k-instruct-8bit` (smaller, faster)

### Wake Word

```python
WAKE_WORD = "hey jheevis"
WAKE_WORD_ALTERNATIVES = ["jheevis", "hey computer"]
WAKE_WORD_THRESHOLD = 0.8  # Similarity threshold (0-1)
```

### Voice Settings

```python
# In tts/synthesizer.py
voice = "Samantha"  # Female voice
# voice = "Alex"    # Male voice
rate = 200          # Speaking speed (words per minute)
```

List available voices:
```bash
say -v ?
```

### Audio Settings

```python
SAMPLE_RATE = 16000         # Hz (Whisper standard)
VAD_MODE = 3                # Aggressiveness (0-3)
VAD_PADDING_DURATION = 300  # ms silence before stopping
```

## Project Structure

```
jheevis/
├── main.py                 # Main orchestrator
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── README.md              # This file
├── docs/                  # Documentation
│   ├── IMPROVEMENT_PLAN.md
│   ├── NEW_FEATURES.md    # System control & file search
│   ├── TERMINAL_CONTROL.md
│   └── VISION_FEATURES.md
├── tests/                 # Test scripts
│   ├── test_vision.py
│   ├── test_terminal_control.py
│   ├── test_new_features.py
│   ├── debug_vision.py
│   └── preview_camera.py
├── stt/                   # Speech-to-Text
│   ├── vad.py            # Voice Activity Detection
│   ├── transcriber.py    # Whisper MLX wrapper
│   └── wake_word.py      # Wake word detection
├── llm/                   # Language Model
│   ├── model.py          # MLX LLM loader
│   ├── history.py        # Conversation history
│   └── intent.py         # Intent classification
├── desktop/               # Desktop Control
│   ├── screen.py         # Screen context (Quartz API)
│   ├── actions.py        # Action executor (AppleScript)
│   ├── system_control.py # System control (volume, brightness, etc.)
│   └── file_search.py    # Spotlight file search
├── vision/                # Computer Vision
│   ├── camera.py         # Camera access
│   └── detector.py       # YOLO object detection
├── tts/                   # Text-to-Speech
│   ├── synthesizer.py    # TTS wrapper
│   └── melo/             # MeloTTS integration
│       └── melo_tts.py   # JARVIS-style voice
└── utils/                 # Utilities
    └── audio.py          # Audio helpers
```

## Testing Individual Components

Test modules independently (from project root):

```bash
# Activate virtual environment first
source venv/bin/activate

# Test Voice Activity Detection
python stt/vad.py

# Test Whisper transcription
python stt/transcriber.py

# Test LLM
python llm/model.py

# Test Desktop Control
python desktop/screen.py
python desktop/actions.py

# Test System Control
python tests/test_new_features.py

# Test Terminal Control
python tests/test_terminal_control.py

# Test Computer Vision
python tests/test_vision.py
python tests/debug_vision.py

# Test Camera Preview (opens window)
python tests/preview_camera.py

# Test MeloTTS Voice
python tts/melo/melo_tts.py

# Test TTS
python tts/synthesizer.py

# Test Audio Utils
python utils/audio.py
```

## Troubleshooting

### "No module named 'mlx'"

**Cause:** Using Rosetta (x86) Python instead of native ARM Python.

**Fix:**
```bash
# Check your Python architecture
python -c "import platform; print(platform.processor())"
# Should output: "arm" (NOT "i386")

# If i386, install native Python with pyenv (see Installation)
```

### "ModuleNotFoundError: No module named '_lzma'"

**Cause:** Python 3.14+ has build issues with pyenv on some systems.

**Fix:**
```bash
# Downgrade to Python 3.11.9 (tested and stable)
pyenv install 3.11.9
pyenv local 3.11.9

# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### "Ultralytics not installed" / Vision features not working

**Cause:** Requirements.txt not fully installed, or old virtual environment.

**Fix:**
```bash
# Reinstall requirements
source venv/bin/activate
pip install --upgrade ultralytics opencv-python pillow

# Verify installation
python -c "from ultralytics import YOLO; print('✓ YOLO installed')"
```

### "I don't see anyone" / Vision detection too sensitive

**Cause:** YOLO confidence threshold too high or low.

**Fix:** Edit `desktop/actions.py` line 26:
```python
# Lower threshold for more detections (default: 0.25)
self.detector = ObjectDetector(confidence=0.20)

# Higher threshold for fewer false positives
self.detector = ObjectDetector(confidence=0.35)
```

### "Microphone not found" / No audio input

**Cause:** Missing microphone permissions.

**Fix:**
1. System Settings → Privacy & Security → Microphone
2. Enable for Terminal/iTerm/VS Code
3. Restart the app after granting permission

**Verify:**
```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
# Should list your microphone
```

### "Can't control apps" / System control not working

**Cause:** Missing Accessibility permissions.

**Fix:**
1. System Settings → Privacy & Security → Accessibility
2. Click the lock icon and authenticate
3. Click "+" and add Terminal/iTerm/VS Code
4. Restart the assistant

### "Camera not found" / Vision features fail

**Cause:** Missing camera permissions.

**Fix:**
1. System Settings → Privacy & Security → Camera
2. Enable for Terminal/iTerm/VS Code
3. Check camera availability:
```bash
python tests/preview_camera.py
```

### Models download slowly

**Cause:** Large model files (~4-6GB total).

**Fix:**
- Be patient, first download takes 5-15 minutes
- Use fast internet connection
- Models cache in `~/.cache/huggingface/hub/`
- Subsequent runs load instantly from cache

**Manual download:**
```bash
# Pre-download models
huggingface-cli download mlx-community/whisper-large-v3-turbo
huggingface-cli download mlx-community/Llama-3.2-3B-Instruct-4bit
```

### "ModelWrapper" error / Corrupted model cache

**Cause:** Interrupted download or corrupted cache.

**Fix:**
```bash
# Clear Llama model cache
rm -rf ~/.cache/huggingface/hub/models--mlx-community--Llama-3.2-3B-Instruct-4bit

# Restart assistant to re-download
python main.py
```

### High CPU/Memory usage

**Cause:** Large models running on-device.

**Fix:** Reduce model sizes in `config.py`:
```python
# Smaller, faster models
WHISPER_MODEL = "mlx-community/whisper-small"
LLM_MODEL = "mlx-community/Llama-3.2-1B-Instruct-4bit"
```

**Expected Resource Usage:**
- **RAM:** ~4-6GB (with 3B model)
- **GPU:** ~2GB (Metal)
- **CPU:** 10-30% idle, 60-100% during inference

### Low transcription accuracy

**Cause:** Whisper model too small, or VAD too aggressive.

**Fix:**
1. Use larger Whisper model in `config.py`:
```python
WHISPER_MODEL = "mlx-community/whisper-large-v3"  # Best accuracy
```

2. Adjust VAD sensitivity in `config.py`:
```python
VAD_MODE = 2  # Less aggressive (0=least, 3=most)
VAD_PADDING_DURATION = 500  # Longer pause detection (ms)
```

3. Speak clearly and reduce background noise

### MeloTTS voice sounds robotic / Wrong accent

**Cause:** Wrong speaker or speed setting.

**Fix:** Edit `config.py`:
```python
TTS_SPEAKER = "EN-BR"  # British (JARVIS-style)
# TTS_SPEAKER = "EN-US"  # American
# TTS_SPEAKER = "EN-AU"  # Australian

TTS_SPEED = 0.9  # Adjust 0.5 (slow) to 2.0 (fast)
```

**Test voices:**
```bash
python tts/melo/melo_tts.py
```

### "Transformers version conflict" warning

**Cause:** MeloTTS requires transformers 4.x, but mlx-lm needs 5.x.

**Fix:** This is normal, ignore the warning. We upgraded transformers to 5.7.0 for mlx-lm compatibility, and MeloTTS still works despite the warning.

```bash
# Verify both work:
python -c "from melo.api import TTS; print('✓ MeloTTS OK')"
python -c "from mlx_lm import load; print('✓ MLX-LM OK')"
```

### NLTK data missing

**Cause:** MeloTTS requires NLTK data for text processing.

**Fix:**
```bash
python -m nltk.downloader averaged_perceptron_tagger_eng cmudict
```

### Assistant not responding / Frozen

**Cause:** Model inference taking too long, or waiting for input.

**Debug:**
1. Check logs: `tail -f jheevis.log`
2. Test individual components:
```bash
python tests/test_vision.py
python tests/debug_vision.py
```

3. Reduce model size (see "High CPU/Memory usage")

### Wake word not detected

**Cause:** Threshold too high, or background noise.

**Fix:** Edit `config.py`:
```python
WAKE_WORD_THRESHOLD = 0.7  # Lower for easier activation (0-1)
# Default: 0.8
```

**Disable wake word for testing:**
```python
ENABLE_WAKE_WORD = False  # Always listening
```

## Performance

Benchmarks on M1 MacBook Pro (16GB):

- **Whisper Large-v3-Turbo**: ~300ms for 5s audio
- **Llama 3.2 3B (4-bit)**: ~40-60 tokens/second
- **Total Response Time**: 1-2 seconds (speech end → TTS start)
- **Memory Usage**: ~4GB RAM, ~2GB GPU

## Roadmap

- [x] **MeloTTS Integration**: ✅ JARVIS-style British voice
- [x] **Computer Vision**: ✅ YOLO object and people detection
- [x] **System Control**: ✅ Volume, brightness, DND, battery, sleep
- [x] **File Search**: ✅ Spotlight integration
- [x] **Terminal Control**: ✅ Open/close, new window/tab, run commands
- [x] **Real-Time Data**: ✅ Date, time, weather, trash count
- [ ] **Hand Gesture Control**: Window manipulation via camera gestures
- [ ] **Enhanced Vision**: Vision-language model for scene understanding
- [ ] **Conversational Context**: Follow-up questions, proactive suggestions
- [ ] **Screen Reading/OCR**: Read text from screen, accessibility features
- [ ] **Function Calling**: Calendar, email, file operations
- [ ] **Persistent Memory**: Long-term conversation history
- [ ] **Multi-language Support**: Beyond English
- [ ] **Fine-tuning**: Custom voice, personalized responses
- [ ] **GUI Interface**: Status display, settings panel

See [docs/IMPROVEMENT_PLAN.md](docs/IMPROVEMENT_PLAN.md) for detailed roadmap and implementation plans.

## Advanced Usage

### Custom System Prompt

Edit [config.py](config.py):
```python
SYSTEM_PROMPT = """You are Jheevis, a sarcastic AI assistant.
You help with tasks but make witty remarks."""
```

### Disable Features

```python
ENABLE_WAKE_WORD = False         # Always listening
ENABLE_DESKTOP_CONTROL = False   # Conversation only
ENABLE_SCREEN_UNDERSTANDING = False
ENABLE_TTS = False               # Text-only mode
```

### Conversation History

Save/load conversations:
```python
# In llm/history.py
history.save_to_file("conversation.json")
history.load_from_file("conversation.json")
```

### Custom Wake Word

Any phrase works:
```python
WAKE_WORD = "hey assistant"
WAKE_WORD_ALTERNATIVES = ["assistant", "hey there"]
```

## Credits

- **Huw Prosser**: Original [jarvis-mlx](https://github.com/huwprosser/jarvis-mlx) implementation
- **Apple MLX**: [MLX framework](https://github.com/ml-explore/mlx) for Apple Silicon
- **OpenAI**: Whisper speech recognition
- **Meta**: Llama language models
- **MyShell**: [MeloTTS](https://github.com/myshell-ai/MeloTTS) for JARVIS-style voice synthesis
- **Ultralytics**: YOLOv11 for object detection

## License

MIT License - Feel free to modify and extend!

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review logs in `jheevis.log`
3. Test individual components
4. Open an issue with logs and system info

---

**Enjoy your personal Jheevis! 🤖**
