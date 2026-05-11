"""
Text-to-Speech Synthesizer
Converts text to speech audio
Currently using macOS built-in TTS (can be upgraded to MeloTTS later)
"""

import subprocess
import logging
import sounddevice as sd
import numpy as np
from typing import Optional

import config

logger = logging.getLogger(__name__)


class TTSSynthesizer:
    """
    Text-to-Speech wrapper.
    Uses macOS built-in 'say' command for simplicity.
    Can be extended to use MeloTTS for better quality and customization.
    """
    
    def __init__(
        self,
        voice: str = "Daniel",  # "Daniel" = JARVIS-like British male voice
        rate: int = 165,  # Measured, sophisticated pace like JARVIS (165-170 ideal)
        use_melo: bool = False  # Set True to use MeloTTS for ultra-natural speech
    ):
        """
        Initialize TTS synthesizer.
        
        Args:
            voice: Voice name (run 'say -v ?' to list available voices)
            rate: Speaking rate in words per minute
            use_melo: Use MeloTTS for more natural speech (requires: pip install melo-tts)
        """
        self.voice = voice
        self.rate = rate
        self.use_melo = use_melo
        self.melo_tts = None
        self.current_process = None  # Track current TTS process for interruption
        self.interrupted = False  # Flag to track interruption
        
        if use_melo:
            try:
                from tts.melo.melo_tts import MeloTTS
                self.melo_tts = MeloTTS(
                    language=config.TTS_LANGUAGE,
                    speaker=config.TTS_SPEAKER,
                    speed=config.TTS_SPEED
                )
                logger.info("TTS initialized: MeloTTS (natural human-like speech)")
            except ImportError:
                logger.warning("MeloTTS not installed, falling back to macOS voices. Install with: pip install melo-tts")
                self.use_melo = False
            except Exception as e:
                logger.error(f"Failed to load MeloTTS: {e}, using macOS voices")
                self.use_melo = False
        
        if not self.use_melo:
            logger.info(f"TTS initialized: macOS voice={voice}, rate={rate}wpm")
    
    def speak(self, text: str, wait: bool = True) -> bool:
        """
        Speak text using TTS.
        
        Args:
            text: Text to speak
            wait: Whether to wait for speech to complete
        
        Returns:
            True if successful
        """
        if not text or not config.ENABLE_TTS:
            return False
        
        logger.info(f"Speaking: '{text[:50]}...'")
        
        # Reset interrupt flag
        self.interrupted = False
        
        # Use MeloTTS if enabled
        if self.use_melo and self.melo_tts:
            return self.melo_tts.speak(text, wait=wait, interrupt_flag=lambda: self.interrupted)
        
        # Otherwise use macOS built-in
        try:
            cmd = ['say', '-v', self.voice, '-r', str(self.rate), text]
            
            if wait:
                self.current_process = subprocess.Popen(cmd)
                self.current_process.wait()
                self.current_process = None
            else:
                self.current_process = subprocess.Popen(cmd)
            
            return True
        
        except Exception as e:
            logger.error(f"TTS error: {e}")
            self.current_process = None
            return False
    
    def speak_async(self, text: str) -> bool:
        """
        Speak text asynchronously (non-blocking).
        
        Args:
            text: Text to speak
        
        Returns:
            True if started successfully
        """
        return self.speak(text, wait=False)
    
    def save_to_file(self, text: str, filename: str) -> bool:
        """
        Save speech to audio file.
        
        Args:
            text: Text to convert
            filename: Output file path (.aiff format)
        
        Returns:
            True if successful
        """
        logger.info(f"Saving TTS to file: {filename}")
        
        try:
            cmd = ['say', '-v', self.voice, '-r', str(self.rate), '-o', filename, text]
            subprocess.run(cmd, check=True)
            return True
        
        except Exception as e:
            logger.error(f"Error saving TTS: {e}")
            return False
    
    def list_voices(self) -> list:
        """
        Get list of available voices.
        
        Returns:
            List of voice names
        """
        try:
            result = subprocess.run(['say', '-v', '?'], capture_output=True, text=True)
            voices = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    # Format: "Voice Name    language    # description"
                    parts = line.split()
                    if parts:
                        voices.append(parts[0])
            return voices
        except Exception as e:
            logger.error(f"Error listing voices: {e}")
            return []
    
    def stop(self) -> bool:
        """
        Stop any currently playing speech immediately.
        
        Returns:
            True if successfully stopped
        """
        try:
            # Set interrupt flag
            self.interrupted = True
            
            # Stop MeloTTS if using it
            if self.use_melo and self.melo_tts:
                sd.stop()  # Stop sounddevice playback
                logger.info("Stopped MeloTTS playback")
            
            # Stop macOS 'say' process
            if self.current_process and self.current_process.poll() is None:
                self.current_process.terminate()
                try:
                    self.current_process.wait(timeout=0.5)
                except:
                    self.current_process.kill()
                self.current_process = None
                logger.info("Stopped macOS TTS")
            
            # Also use killall as backup to force stop all 'say' processes
            subprocess.run(['killall', 'say'], stderr=subprocess.DEVNULL)
            
            return True
        
        except Exception as e:
            logger.error(f"Error stopping TTS: {e}")
            return False
    
    def stop(self):
        """Stop current speech."""
        try:
            subprocess.run(['killall', 'say'], stderr=subprocess.DEVNULL)
            logger.debug("Stopped TTS")
        except Exception:
            pass


def test_tts():
    """Test TTS synthesizer."""
    tts = TTSSynthesizer()
    
    print("=== TTS Test ===\n")
    
    # List available voices
    print("Available voices:")
    voices = tts.list_voices()
    for voice in voices[:10]:  # Show first 10
        print(f"  - {voice}")
    print()
    
    # Test speaking
    print("Speaking test message...")
    tts.speak("Hello! I am Jheevis, your AI assistant. How can I help you today?")
    
    print("\nTesting async speech...")
    tts.speak_async("This is an asynchronous test.")
    
    import time
    time.sleep(3)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_tts()
