# Jheevis Improvement Plan

## 🎯 Overview
This document outlines planned improvements and new features for Jheevis, the offline voice assistant.

---

## 📋 Planned Features

### 1. **Conversational Context & Follow-ups**
**Status:** Planned  
**Priority:** High

**Current State:**
- Each command is processed independently
- No memory of previous conversation

**Improvement:**
- Add conversation history tracking
- Enable follow-up questions without repeating context
- Implement proactive suggestions

**Example Flow:**
```
User: "What's the date today?"
Jarvis: "Today is Tuesday, May 6th, 2026. Would you like me to tell you the weather as well, sir?"
User: "Yes"
Jarvis: "Absolutely. The weather today is 18°C with partly cloudy skies in San Francisco."
```

**Implementation:**
- Add `ConversationManager` class to track context
- Store last 5-10 interactions in memory
- Implement context-aware intent classification
- Add proactive suggestion logic (weather after date, related files after search, etc.)

---

### 2. **Identity & Self-Awareness Responses**
**Status:** Planned  
**Priority:** Medium

**Current State:**
- No personalized responses about creator/purpose

**Improvement:**
- Add personality responses for common questions
- Maintain JARVIS-style professional British tone

**Example Responses:**
```
User: "Who created you?"
Jarvis: "I was developed by Jino, an AI developer and software engineer with extensive experience in machine learning and voice systems. He designed me to be your personal desktop assistant, sir."

User: "Who is your boss?"
Jarvis: "You are, sir. I serve at your command."

User: "What can you do?"
Jarvis: "I can assist with system control, file management, terminal operations, and even see through my camera for object detection. I'm constantly learning and improving to serve you better."
```

**Implementation:**
- Add `IDENTITY_KEYWORDS` to `llm/intent.py`
- Create `_handle_identity_question()` in `main.py`
- Add personality responses to `config.py`
- Keep responses concise and JARVIS-like

---

### 3. **Hand Gesture Window Control**
**Status:** Planned  
**Priority:** High  
**Complexity:** High

**Current State:**
- Window control via voice commands only
- No gesture recognition

**Improvement:**
- Real-time hand tracking using camera
- Gesture-based window manipulation
- Smooth window dragging/resizing

**Gestures:**
- ✊ **Fist**: Grab window
- 👆 **Point + Move**: Drag window
- 🤏 **Pinch + Spread**: Resize window
- ✋ **Open Palm**: Release window
- 👌 **OK Sign**: Minimize window

**Implementation:**
```python
# New files to create:
vision/hand_tracker.py    # MediaPipe hand detection
vision/gesture_recognizer.py  # Gesture classification
desktop/window_controller.py  # Window manipulation via Accessibility API

# Technical Stack:
- MediaPipe (hand landmark detection)
- PyAutoGUI (mouse control)
- Quartz (macOS window management)
- PyObjC (Accessibility API)
```

**Challenges:**
- Accessibility permissions required
- Smooth gesture recognition (avoid jitter)
- Multi-hand support
- Performance (60fps camera feed)

---

### 4. **Computer Vision Reasoning**
**Status:** Partially Implemented  
**Priority:** High

**Current State:**
- Basic object detection (YOLOv11)
- Simple scene description
- People counting

**Improvement:**
- Enhanced scene understanding
- Contextual reasoning about objects
- Activity recognition
- Explain relationships between objects

**Example Interactions:**
```
User: "Jheevis"
Jarvis: "Yes, sir?"
User: "Can you check what's on my desk?"
Jarvis: "Certainly. I can see a laptop, a coffee cup, and what appears to be a notebook. The laptop is open and positioned in the center. Would you like me to elaborate on anything specific?"

User: "What am I doing?"
Jarvis: "Based on what I see, you appear to be working on your laptop, sir. Your hands are on the keyboard."

User: "Is anyone behind me?"
Jarvis: "No, sir. I don't detect anyone else in the frame. You're alone."
```

**Implementation:**
- Integrate vision-language model (e.g., LLaVA or MobileVLM)
- Add scene understanding prompts
- Implement object relationship detection
- Add activity classification
- Use multi-frame analysis for better context

**Technical Requirements:**
- Vision-Language Model (consider MobileVLM for on-device)
- Enhanced prompting for scene description
- Temporal analysis (compare frames over time)

---

### 5. **Proactive Assistance**
**Status:** Planned  
**Priority:** Medium

**Improvement:**
- Jheevis suggests related actions
- Context-aware recommendations
- Smart reminders

**Examples:**
```
User: "Find my presentation file"
Jarvis: "I found 'Q2_Presentation.pptx'. Would you like me to open it, sir?"

User: "What's the weather?"
Jarvis: "18°C with rain expected this afternoon. Shall I remind you to bring an umbrella before you leave?"

User: "Open terminal"
Jarvis: "Terminal opened, sir. I notice you frequently run 'git status' first. Would you like me to execute it?"
```

---

### 6. **Enhanced Natural Language Understanding**
**Status:** Planned  
**Priority:** Medium

**Improvement:**
- Better handling of ambiguous commands
- Multi-step command parsing
- Clarification questions when uncertain

**Examples:**
```
User: "Open Safari and search women"
Jarvis: "Opening Safari and searching for 'women', sir."
[Executes both actions sequentially]

User: "Make it louder"
Jarvis: "Increasing volume to 75%, sir."
[Remembers context from previous audio interaction]

User: "Close it"
Jarvis: "Closing Safari, sir."
[Knows "it" refers to last opened app]
```

---

### 7. **Screen Reading & OCR**
**Status:** Planned  
**Priority:** Low

**Improvement:**
- Read text from screen
- Extract information from images
- Help with accessibility

**Examples:**
```
User: "What does the error message say?"
Jarvis: "The error reads: 'Connection timeout. Please check your network settings.'"

User: "Read my notifications"
Jarvis: "You have 3 notifications, sir. Slack: 2 unread messages. Calendar: Meeting in 15 minutes. Mail: New email from John."
```

**Implementation:**
- macOS Accessibility API for UI elements
- Tesseract OCR for text extraction
- Screenshot analysis with vision model

---

## 🔧 Technical Improvements

### 1. **Performance Optimization**
- [ ] Reduce model loading time (cache models in memory)
- [ ] Optimize camera frame processing (skip frames if needed)
- [ ] Parallel processing for multi-step commands
- [ ] Background model warm-up on startup

### 2. **Error Handling**
- [ ] Graceful degradation when camera unavailable
- [ ] Better error messages for failed actions
- [ ] Retry logic for transient failures
- [ ] Offline mode indicators

### 3. **Configuration & Customization**
- [ ] User-configurable wake word
- [ ] Adjustable voice speed/pitch
- [ ] Custom command aliases
- [ ] Personalized responses

### 4. **Testing & Reliability**
- [ ] Unit tests for all modules
- [ ] Integration tests for voice pipeline
- [ ] Camera/vision test suite
- [ ] Performance benchmarks

---

## 📊 Implementation Priority

### Phase 1 (Immediate - Next 2 Weeks)
1. ✅ Date/Time/Weather features (COMPLETED)
2. 🔄 Conversational context & follow-ups
3. 🔄 Identity/personality responses
4. 🔄 Enhanced vision reasoning

### Phase 2 (Short-term - 1 Month)
1. Hand gesture window control (high complexity)
2. Proactive assistance
3. Multi-step command parsing
4. Performance optimization

### Phase 3 (Long-term - 2-3 Months)
1. Screen reading & OCR
2. Advanced activity recognition
3. Custom wake word
4. Full test coverage

---

## 🎨 User Experience Improvements

### Voice Interaction
- [ ] More natural pauses in speech
- [ ] Emotion/tone variation (excited, concerned, neutral)
- [ ] Interrupt handling (stop speaking when user talks)

### Visual Feedback
- [ ] System tray indicator (listening/processing/speaking)
- [ ] Optional overlay for responses
- [ ] Camera preview window (when vision active)

### Accessibility
- [ ] Keyboard shortcuts for commands
- [ ] Text-based command input (fallback)
- [ ] Adjustable speech rate
- [ ] Visual indicators for hearing-impaired users

---

## 📝 Notes

### Development Guidelines
- Maintain 100% offline capability
- Keep privacy-first approach (no data leaves device)
- Optimize for Apple Silicon (MLX framework)
- Professional JARVIS-style personality
- Graceful error handling

### Testing Priorities
1. Test all new features on real M-series Mac
2. Verify camera/vision performance (60fps target)
3. Benchmark model inference times
4. Test conversation context accuracy

---

## 🚀 Future Ideas (Brainstorming)

- **Calendar Integration**: "What's on my schedule today?"
- **Email Management**: "Read my latest emails"
- **Code Assistant**: "Explain this code" (screen analysis)
- **Meeting Transcription**: Real-time transcription using Whisper
- **Focus Mode**: Auto-enable DND, close distractions
- **Smart Home**: Control HomeKit devices (if available)
- **Clipboard History**: "What did I copy 5 minutes ago?"
- **Quick Notes**: "Jheevis, take a note"

---

**Last Updated:** May 6, 2026  
**Version:** 1.0  
**Maintainer:** Jino
