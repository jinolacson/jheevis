# New Features: System Control & File Search & Terminal Control & Vision

## 🎯 Features Implemented

### 1. System Control (Volume, Brightness, Do Not Disturb)

#### Volume Control
Control your Mac's volume with voice commands:

**Commands:**
- "Volume up" / "Turn up the volume" / "Louder"
- "Volume down" / "Turn down the volume" / "Quieter"
- "Set volume to 50" (0-100)
- "Mute"
- "Unmute"

**Examples:**
```
User: "Hey Jheevis, volume up"
Jheevis: "Turning up the volume"

User: "Set volume to 30"
Jheevis: "Setting volume to 30"

User: "Mute"
Jheevis: "Muting"
```

#### Brightness Control
Adjust screen brightness (requires `brightness` tool):

**Commands:**
- "Brightness up" / "Make it brighter" / "Brighten"
- "Brightness down" / "Make it dimmer" / "Dim"

**Installation Required:**
```bash
brew install brightness
```

**Examples:**
```
User: "Brightness up"
Jheevis: "Increasing brightness"

User: "Make it dimmer"
Jheevis: "Decreasing brightness"
```

#### Do Not Disturb
Toggle Do Not Disturb mode:

**Commands:**
- "Enable do not disturb" / "Turn on do not disturb" / "DND on"
- "Disable do not disturb" / "Turn off do not disturb" / "DND off"

**Setup Required:**
Create Shortcuts in macOS:
1. Open Shortcuts app
2. Create "Enable Do Not Disturb" shortcut
3. Create "Disable Do Not Disturb" shortcut

**Examples:**
```
User: "Enable do not disturb"
Jheevis: "Enabling Do Not Disturb"

User: "Turn off do not disturb"
Jheevis: "Disabling Do Not Disturb"
```

#### Battery Status
Check battery level and charging status:

**Commands:**
- "Battery" / "Battery status" / "Battery level" / "How much battery"

**Examples:**
```
User: "What's my battery level?"
Jheevis: "Battery is at 85% and charging"

User: "Battery status"
Jheevis: "Battery is at 42% and not charging"
```

#### System Sleep
Put your Mac to sleep:

**Commands:**
- "Sleep" / "Go to sleep" / "Put to sleep"

**Examples:**
```
User: "Put the system to sleep"
Jheevis: "Putting the system to sleep"
[System goes to sleep]
```

---

### 2. File Search

Search for files on your Mac using Spotlight:

#### Search Files
Find files by name or content:

**Commands:**
- "Find file [filename]"
- "Search file [filename]"
- "Locate file [filename]"
- "Where is file [filename]"

**Examples:**
```
User: "Find file config.py"
Jheevis: "Found config.py in /Users/jino/Projects/jheevis"

User: "Search file requirements.txt"
Jheevis: "Found 3 files: requirements.txt, requirements-dev.txt, requirements-test.txt"
```

#### Open File
Find and open a file:

**Commands:**
- "Open file [filename]"
- "Open the file [filename]"

**Examples:**
```
User: "Open file main.py"
Jheevis: "Opening main.py"
[File opens in default application]
```

#### Recent Files
View recently modified files:

**Commands:**
- "Recent files"
- "Recently opened"
- "Recent documents"
- "Latest files"

**Examples:**
```
User: "Show me recent files"
Jheevis: "Your recent files include: config.py, main.py, test_new_features.py"
```

---

### 3. Terminal Control

Control macOS Terminal application with voice commands:

#### Open/Close Terminal
Launch or quit the Terminal app:

**Commands:**
- "Open Terminal" / "Launch Terminal"
- "Close Terminal" / "Quit Terminal" - Closes all Terminal windows
- "Close this terminal" / "Exit terminal" / "Close current terminal" - Closes only the active window/tab

**Examples:**
```
User: "Open Terminal"
Jheevis: "Opening Terminal"
[Terminal application launches]

User: "Close this terminal"
Jheevis: "Closing current Terminal window"
[Only the active Terminal window closes]

User: "Close Terminal"
Jheevis: "Closing Terminal"
[Terminal application quits completely]
```

#### New Terminal Window
Create a new Terminal window:

**Commands:**
- "New Terminal window"
- "Open new Terminal window"
- "Create Terminal window"

**Examples:**
```
User: "New Terminal window"
Jheevis: "Opening new Terminal window"
[New Terminal window appears]
```

#### New Terminal Tab
Create a new tab in the current Terminal window:

**Commands:**
- "New Terminal tab"
- "New tab in Terminal"
- "Open Terminal tab"

**Examples:**
```
User: "New Terminal tab"
Jheevis: "Opening new Terminal tab"
[New tab created in current Terminal window]
```

#### Run Terminal Command
Execute a command in a new Terminal window:

**Commands:**
- "Run command [command]"
- "Execute [command]"
- "Run in Terminal [command]"

**Examples:**
```
User: "Run command ls -la"
Jheevis: "Running command: ls -la"
[New Terminal window opens with command executed]

User: "Execute python main.py"
Jheevis: "Running command: python main.py"
[Command runs in new Terminal window]
```

---

### 4. Vision & Object Detection

See and understand the world through your camera with AI-powered object detection:

#### Scene Understanding
Ask Jheevis to describe what it sees:

**Commands:**
- "What do you see?"
- "What can you see?"
- "What's in front of you?"
- "Describe what you see"

**Examples:**
```
User: "What do you see?"
Jheevis: "I see one person and a laptop"

User: "What's in front of you?"
Jheevis: "I see 2 people, a keyboard, and a monitor"
```

#### People Detection
Detect if people are present:

**Commands:**
- "Who is here?"
- "Is anyone here?"
- "How many people?"
- "Count people"

**Examples:**
```
User: "Who is here?"
Jheevis: "I see one person"

User: "How many people?"
Jheevis: "I see 3 people"
```

#### Object Detection
Identify all visible objects:

**Commands:**
- "What objects do you see?"
- "Detect objects"
- "Identify objects"

**Examples:**
```
User: "Detect objects"
Jheevis: "I see one laptop, one mouse, and 2 books"
```

#### Photo Capture
Take and save photos:

**Commands:**
- "Take a picture"
- "Take a photo"
- "Capture image"

**Examples:**
```
User: "Take a picture"
Jheevis: "Picture saved to jheevis_photo_20260505_143022.jpg"
[Photo saved to Desktop]
```

**Technical Details:**
- Uses YOLO (YOLOv11) for object detection
- Detects 80+ object classes (people, laptops, phones, etc.)
- 100% local processing - no cloud
- Auto-downloads model on first use (~10MB)
- Privacy-focused: camera only accessed on command

---

## 🏗️ Implementation Details

### Files Created

1. **`desktop/system_control.py`** - System control module
   - Volume management (get, set, up, down, mute, unmute)
   - Brightness control (up, down, set)
   - Do Not Disturb toggle
   - Battery status
   - System sleep

2. **`desktop/file_search.py`** - File search module
   - Spotlight integration (mdfind)
   - File search by name/content
   - Recent files tracking
   - File opening and revealing

3. **`test_new_features.py`** - Test suite for system control and file search features

4. **`test_terminal_control.py`** - Test suite for terminal control features

5. **`test_vision.py`** - Test suite for vision and camera features

6. **`vision/camera.py`** - Camera access and frame capture module

7. **`vision/detector.py`** - YOLO-based object detection module

8. **`vision/__init__.py`** - Vision module initialization

### Files Modified

1. **`llm/intent.py`**
   - Added new ActionType enums for system control, file operations, terminal control, and vision
   - Added keyword lists for all new commands
   - Added `_check_system_control()` method
   - Added `_check_terminal_control()` method
   - Added `_check_file_search()` method
   - Added `_check_vision()` method
   - Added `_extract_number()` helper method

2. **`desktop/actions.py`**
   - Imported SystemController, FileSearcher, Camera, and ObjectDetector
   - Added system control action methods
   - Added file search action methods
   - Added terminal control methods (open, close, new window, new tab, run command)
   - Added vision methods (what_do_you_see, who_is_here, count_people, detect_objects, take_picture)

3. **`main.py`**
   - Updated `_handle_desktop_action()` to handle all new action types
   - Added handlers for volume, brightness, DND, battery, file search, terminal control, and vision

4. **`requirements.txt`**
   - Added opencv-python for camera access
   - Added ultralytics for YOLO object detection
   - Added pillow for image processing

---

## 🧪 Testing

Run the test suite:

```bash
cd /Users/jino/Projects/jheevis

# Test system control and file search
python test_new_features.py

# Test terminal control
python test_terminal_control.py

# Test vision and camera (requires camera access)
python test_vision.py
```

This will test:
- Intent classification for all new commands
- System control functionality (volume, battery)
- File search functionality (search, find, recent)
- Terminal control (open, close, new window/tab, run commands)
- Vision capabilities (camera access, object detection, scene description)

---

## 📝 Usage Examples

### Complete Voice Interactions

```
# System Control
User: "Hey Jheevis, what's my battery?"
Jheevis: "Battery is at 78% and charging"

User: "Volume down"
Jheevis: "Turning down the volume"

User: "Enable do not disturb"
Jheevis: "Enabling Do Not Disturb"

# File Search
User: "Find file requirements.txt"
Jheevis: "Found requirements.txt in /Users/jino/Projects/jheevis"

User: "Open file config.py"
Jheevis: "Opening config.py"

User: "Show me recent files"
Jheevis: "Your recent files include: main.py, config.py, test_new_features.py"

# Terminal Control
User: "Open Terminal"
Jheevis: "Opening Terminal"

User: "New Terminal window"
Jheevis: "Opening new Terminal window"

User: "Run command ls -la"
Jheevis: "Running command: ls -la"

# Vision & Camera
User: "What do you see?"
Jheevis: "I see one person and a laptop"

User: "Who is here?"
Jheevis: "I see 2 people"

User: "Take a picture"
Jheevis: "Picture saved to jheevis_photo_20260505_143022.jpg"

# Combined
User: "Turn up the volume and find file main.py"
Jheevis: "Turning up the volume"
[Then separately] "Found main.py in /Users/jino/Projects/jheevis"
```

---

## 🎯 Next Steps

### Potential Enhancements

1. **System Monitoring**
   - CPU usage
   - Memory usage
   - Disk space
   - Network status

2. **Advanced File Operations**
   - Create/delete files
   - Move/copy files
   - Rename files
   - File content preview

3. **Clipboard Integration**
   - Copy to clipboard
   - Read clipboard
   - Clipboard history

4. **Calendar & Reminders**
   - Check calendar events
   - Create reminders
   - Set timers

5. **Application-Specific Control**
   - Spotify controls
   - Browser tab management
   - Email integration

---

## 🐛 Known Issues

1. **Brightness Control**: Requires `brightness` CLI tool (`brew install brightness`)
2. **Do Not Disturb**: Requires manual Shortcuts setup
3. **File Search**: Uses Spotlight, so files must be indexed

---

## 📚 API Reference

### SystemController

```python
from desktop.system_control import SystemController

system = SystemController()

# Volume
current = system.get_volume()  # Returns 0-100
system.set_volume(50)
system.volume_up(10)
system.volume_down(10)
system.mute()
system.unmute()

# Brightness
system.brightness_up()
system.brightness_down()
system.set_brightness(0.5)  # 0.0-1.0 or 0-100

# Do Not Disturb
system.enable_dnd()
system.disable_dnd()

# Battery
battery = system.get_battery_status()
# Returns: {'charging': bool, 'percentage': int, 'raw': str}

# System
system.sleep_system()
```

### FileSearcher

```python
from desktop.file_search import FileSearcher

files = FileSearcher()

# Search
results = files.search("config", limit=10)
results = files.search_by_name("main.py", limit=5)
recent = files.search_recent(days=7, limit=10)

# Find and open
path = files.find_file("config.py")
files.open_file(path)
files.reveal_in_finder(path)

# Get info
info = files.get_file_info(path)
# Returns: {path, name, directory, size, created, modified, ...}
```

### Terminal Control (ActionExecutor)

```python
from desktop.actions import ActionExecutor

executor = ActionExecutor()

# Open/Close Terminal
executor.open_terminal()
executor.close_terminal()  # Quits Terminal app (all windows)
executor.close_current_terminal()  # Closes only the active window/tab

# Create new windows/tabs
executor.new_terminal_window()
executor.new_terminal_tab()

# Run commands
executor.run_terminal_command("ls -la")
executor.run_terminal_command("python main.py")
executor.run_terminal_command("cd ~/Projects && git status")
```

---

## ✅ Summary

**Implemented:**
- ✅ Volume control (up, down, set, mute, unmute)
- ✅ Brightness control (up, down)
- ✅ Do Not Disturb toggle
- ✅ Battery status check
- ✅ System sleep
- ✅ File search by name/content
- ✅ Open files by name
- ✅ Recent files listing
- ✅ Terminal control (open, close, new window, new tab, run commands)
- ✅ Computer vision (camera access, object detection, people detection)
- ✅ Scene description in natural language
- ✅ Photo capture and saving
- ✅ Intent classification for all commands
- ✅ Integration with main assistant

**Ready to use:** 
Just say "Hey Jheevis" followed by any of the commands above!
