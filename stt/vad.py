"""
Voice Activity Detection using WebRTC VAD
Detects when user is speaking and when they stop
"""

import webrtcvad
import pyaudio
import numpy as np
from collections import deque
from typing import Callable, Optional
import logging

import config

logger = logging.getLogger(__name__)


class VoiceActivityDetector:
    """
    Real-time voice activity detection using WebRTC VAD.
    Monitors audio stream and triggers callbacks when speech starts/stops.
    """
    
    def __init__(
        self,
        sample_rate: int = config.SAMPLE_RATE,
        frame_duration: int = config.VAD_FRAME_DURATION,
        mode: int = config.VAD_MODE,
        padding_duration: int = config.VAD_PADDING_DURATION
    ):
        """
        Initialize VAD.
        
        Args:
            sample_rate: Audio sample rate in Hz (8000, 16000, 32000, or 48000)
            frame_duration: Frame duration in ms (10, 20, or 30)
            mode: Aggressiveness mode (0-3, higher is more aggressive)
            padding_duration: Milliseconds of silence before stopping
        """
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration
        self.mode = mode
        self.padding_duration = padding_duration
        
        # WebRTC VAD
        self.vad = webrtcvad.Vad(mode)
        
        # Audio parameters
        self.frame_size = int(sample_rate * frame_duration / 1000)  # samples per frame
        self.padding_frames = int(padding_duration / frame_duration)
        
        # State tracking
        self.is_speaking = False
        self.voiced_frames = deque(maxlen=1000)  # Buffer for voiced frames
        self.unvoiced_frame_count = 0
        
        # PyAudio
        self.audio = pyaudio.PyAudio()
        self.stream: Optional[pyaudio.Stream] = None
        
        logger.info(f"VAD initialized: {sample_rate}Hz, {frame_duration}ms frames, mode {mode}")
    
    def start_listening(
        self,
        on_speech_start: Optional[Callable] = None,
        on_speech_end: Optional[Callable[[np.ndarray], None]] = None,
        on_frame: Optional[Callable[[bytes, bool], None]] = None
    ):
        """
        Start listening to microphone and detect voice activity.
        
        Args:
            on_speech_start: Callback when speech is detected
            on_speech_end: Callback when speech ends (receives audio data)
            on_frame: Callback for each audio frame (receives frame data and is_speech flag)
        """
        logger.info("Starting voice activity detection...")
        
        # Open audio stream
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=config.CHANNELS,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.frame_size
        )
        
        try:
            while True:
                # Read frame
                frame = self.stream.read(self.frame_size, exception_on_overflow=False)
                
                # Check if frame contains speech
                is_speech = self.vad.is_speech(frame, self.sample_rate)
                
                # Trigger frame callback if provided
                if on_frame:
                    on_frame(frame, is_speech)
                
                # Handle speech detection
                if is_speech:
                    self.voiced_frames.append(frame)
                    
                    if not self.is_speaking:
                        self.is_speaking = True
                        self.unvoiced_frame_count = 0
                        logger.debug("Speech started")
                        if on_speech_start:
                            on_speech_start()
                    else:
                        self.unvoiced_frame_count = 0
                else:
                    # Track silence
                    if self.is_speaking:
                        self.unvoiced_frame_count += 1
                        
                        # Check if enough silence to consider speech ended
                        if self.unvoiced_frame_count >= self.padding_frames:
                            self.is_speaking = False
                            
                            # Extract audio data
                            audio_data = self._extract_audio()
                            
                            # Only trigger callback if we have sufficient audio
                            min_frames = int(config.VAD_MIN_AUDIO_LENGTH * 1000 / self.frame_duration)
                            if len(self.voiced_frames) >= min_frames:
                                # Additional check: ensure audio has meaningful content
                                if len(audio_data) > 0:
                                    max_amplitude = np.max(np.abs(audio_data))
                                    # Balanced threshold for int16 audio
                                    if max_amplitude > 300:  # Lowered to allow real speech
                                        logger.debug(f"Speech ended ({len(self.voiced_frames)} frames, amplitude: {max_amplitude})")
                                        if on_speech_end:
                                            on_speech_end(audio_data)
                                    else:
                                        logger.debug(f"Audio too quiet, ignoring (amplitude: {max_amplitude})")
                                else:
                                    logger.debug("Empty audio data, ignoring")
                            
                            # Clear buffer
                            self.voiced_frames.clear()
                            self.unvoiced_frame_count = 0
        
        except KeyboardInterrupt:
            logger.info("Stopping voice activity detection...")
        finally:
            self.stop_listening()
    
    def _extract_audio(self) -> np.ndarray:
        """Extract audio data from voiced frames buffer."""
        if not self.voiced_frames:
            return np.array([], dtype=np.int16)
        
        # Concatenate all frames
        audio_bytes = b''.join(self.voiced_frames)
        
        # Convert to numpy array
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
        
        return audio_array
    
    def stop_listening(self):
        """Stop the audio stream."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        logger.info("VAD stopped")
    
    def __del__(self):
        """Cleanup on deletion."""
        self.stop_listening()
        if hasattr(self, 'audio'):
            self.audio.terminate()


def test_vad():
    """Test VAD by printing when speech is detected."""
    
    def on_start():
        print("🎤 Speech detected!")
    
    def on_end(audio: np.ndarray):
        duration = len(audio) / config.SAMPLE_RATE
        print(f"✅ Speech ended ({duration:.2f}s, {len(audio)} samples)")
    
    vad = VoiceActivityDetector()
    print("Listening... (Press Ctrl+C to stop)")
    vad.start_listening(on_speech_start=on_start, on_speech_end=on_end)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_vad()
