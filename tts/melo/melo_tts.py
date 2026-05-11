"""
MeloTTS Integration for Natural Speech
High-quality, human-like text-to-speech
"""

import logging
import os
import numpy as np
import sounddevice as sd
import tempfile
import soundfile as sf

logger = logging.getLogger(__name__)


class MeloTTS:
    """
    MeloTTS wrapper for natural-sounding speech.
    Significantly better quality than macOS built-in voices.
    """
    
    def __init__(self, language: str = "EN", speaker: str = "EN-BR", speed: float = 0.9):
        """
        Initialize MeloTTS.
        
        Args:
            language: Language code (EN, EN_US, etc.)
            speaker: Speaker ID (EN-BR for British, EN-US for American)
            speed: Speech speed multiplier (0.9 for JARVIS-like pace)
        """
        self.language = language
        self.speaker = speaker
        self.speed = speed
        self.model = None
        
        try:
            from melo.api import TTS
            
            # Initialize TTS model
            self.model = TTS(language=language, device='auto')
            speaker_ids = self.model.hps.data.spk2id
            
            logger.info(f"MeloTTS initialized: {language}, available speakers: {speaker_ids}")
            
        except ImportError:
            logger.error("MeloTTS not installed. Run: pip install git+https://github.com/myshell-ai/MeloTTS.git")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize MeloTTS: {e}")
            raise
    
    def speak(self, text: str, wait: bool = True, interrupt_flag=None) -> bool:
        """
        Speak text using MeloTTS.
        
        Args:
            text: Text to speak
            wait: Whether to wait for completion
            interrupt_flag: Callable that returns True if interrupted
        
        Returns:
            True if successful
        """
        if not self.model:
            logger.error("MeloTTS not initialized")
            return False
        
        try:
            # Get speaker ID - spk2id is a dict-like object
            speaker_ids = dict(self.model.hps.data.spk2id)
            speaker_id = speaker_ids.get(self.speaker, list(speaker_ids.values())[0])
            
            # Generate audio in memory using temp file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = tmp.name
            
            # Generate to temp file
            self.model.tts_to_file(
                text=text,
                speaker_id=speaker_id,
                speed=self.speed,
                output_path=tmp_path,
                quiet=True
            )
            
            # Load and play audio
            audio, sr = sf.read(tmp_path)
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            # Play audio
            sd.play(audio, samplerate=sr)
            
            if wait:
                # Wait with interrupt checking
                if interrupt_flag:
                    # Check interrupt flag periodically (every 50ms)
                    import time
                    try:
                        while True:
                            if interrupt_flag():
                                sd.stop()
                                logger.info("Speech interrupted")
                                return False
                            # Check if playback is still active
                            try:
                                if not sd.get_stream().active:
                                    break
                            except:
                                # Stream ended or error
                                break
                            time.sleep(0.05)
                    except Exception as e:
                        logger.debug(f"Interrupt check error: {e}")
                        sd.stop()
                else:
                    sd.wait()
            
            return True
            
        except Exception as e:
            logger.error(f"MeloTTS speak error: {e}")
            return False
    
    def save_to_file(self, text: str, filename: str) -> bool:
        """
        Save speech to audio file.
        
        Args:
            text: Text to convert
            filename: Output file path (.wav)
        
        Returns:
            True if successful
        """
        if not self.model:
            return False
        
        try:
            # Get speaker ID - spk2id is a dict-like object
            speaker_ids = dict(self.model.hps.data.spk2id)
            speaker_id = speaker_ids.get(self.speaker, list(speaker_ids.values())[0])
            
            self.model.tts_to_file(
                text=text,
                speaker_id=speaker_id,
                speed=self.speed,
                output_path=filename,
                quiet=True
            )
            logger.info(f"Saved audio to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Save to file error: {e}")
            return False


if __name__ == "__main__":
    # Test MeloTTS
    logging.basicConfig(level=logging.INFO)
    
    try:
        print("Testing MeloTTS with JARVIS-like British voice...")
        tts = MeloTTS(language="EN", speaker="EN-BR", speed=0.9)
        tts.speak("Good morning, sir. All systems operational. How may I assist you today?")
        print("✅ MeloTTS test complete!")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure MeloTTS is installed: pip install git+https://github.com/myshell-ai/MeloTTS.git")
