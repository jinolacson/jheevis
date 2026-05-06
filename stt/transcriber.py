"""
Speech-to-Text using Whisper MLX
Fast, accurate transcription optimized for Apple Silicon
"""

import mlx_whisper
import numpy as np
import logging
from typing import Optional, Dict, Any

import config

logger = logging.getLogger(__name__)


class WhisperTranscriber:
    """
    Wrapper for MLX Whisper speech recognition.
    Provides efficient transcription using Apple Silicon optimization.
    """
    
    def __init__(
        self,
        model_name: str = config.WHISPER_MODEL,
        language: Optional[str] = config.WHISPER_LANGUAGE
    ):
        """
        Initialize Whisper transcriber.
        
        Args:
            model_name: Model identifier (e.g., 'mlx-community/whisper-large-v3-turbo')
            language: Language code ('en', 'es', etc.) or None for auto-detection
        """
        self.model_name = model_name
        self.language = language
        
        logger.info(f"Whisper model: {model_name}")
        if language:
            logger.info(f"Language: {language}")
        else:
            logger.info("Language: auto-detect")
    
    def transcribe(
        self,
        audio: np.ndarray,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> str:
        """
        Transcribe audio to text.
        
        Args:
            audio: Audio data as numpy array (int16 or float32)
            language: Override language setting
            task: 'transcribe' or 'translate' (to English)
        
        Returns:
            Transcribed text
        """
        # Check if audio is empty or too short
        if len(audio) == 0:
            logger.warning("Empty audio provided")
            return ""
        
        # Convert int16 to float32 if needed
        if audio.dtype == np.int16:
            audio = audio.astype(np.float32) / 32768.0
        
        # Check audio amplitude (threshold to filter noise)
        max_amplitude = np.max(np.abs(audio))
        if max_amplitude < 0.03:  # Balanced threshold
            logger.debug(f"Audio too quiet (max amplitude: {max_amplitude:.4f})")
            return ""
        
        # Check if audio has actual variation (not just noise)
        audio_std = np.std(audio)
        if audio_std < 0.005:  # Reduced to allow more speech
            logger.debug(f"Audio has no variation (std: {audio_std:.4f})")
            return ""
        
        duration = len(audio) / config.SAMPLE_RATE
        logger.debug(f"Transcribing {duration:.2f}s of audio...")
        
        try:
            # Use language parameter if provided, else use instance setting
            lang = language or self.language
            
            # Prepare kwargs
            kwargs: Dict[str, Any] = {
                "path_or_hf_repo": self.model_name,
                "fp16": config.USE_FLOAT16
            }
            
            if lang:
                kwargs["language"] = lang
            
            if task != "transcribe":
                kwargs["task"] = task
            
            # Transcribe using MLX Whisper
            result = mlx_whisper.transcribe(audio, **kwargs)
            
            # Extract text
            text = result.get("text", "").strip()
            
            # Detect hallucinations (Whisper repeating words/phrases)
            if text and self._is_hallucination(text):
                logger.info(f"Filtering background noise (transcribed as: '{text[:50]}...')")
                return ""
            
            if text:
                logger.info(f"Transcribed: '{text}'")
            else:
                logger.debug("No speech detected in audio")
            
            return text
        
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
    
    def _is_hallucination(self, text: str) -> bool:
        """
        Detect if transcription is a hallucination (repetitive words/phrases).
        
        Args:
            text: Transcribed text
        
        Returns:
            True if likely a hallucination
        """
        if not text or len(text) < 10:
            return False
        
        text_lower = text.lower().strip()
        
        # Common Whisper hallucinations for silence/noise
        common_hallucinations = [
            "thank you", "thanks for watching", "subscribe",
            "like and subscribe", "see you next time",
            "thank you for watching", "bye", "goodbye",
            "you", "i'll", "i will", "turn it on",
            "the", "a", "and", "but", "or",
            "uh", "um", "ah", "hmm",
        ]
        
        # Check if entire text is a common hallucination
        if text_lower in common_hallucinations:
            logger.debug(f"Filtered common noise phrase: '{text}'")
            return True
        
        # Check if text is very short and generic (likely noise)
        words = text.split()
        if len(words) <= 3:
            # Single or two-word phrases are often hallucinations
            for phrase in common_hallucinations:
                if text_lower == phrase or text_lower.startswith(phrase):
                    logger.debug(f"Filtered short noise phrase: '{text}'")
                    return True
        
        words = text_lower.split()
        
        # Check for very short transcriptions with repetition
        if len(words) <= 3:
            unique_words = set(words)
            if len(unique_words) == 1:  # All same word
                return True
        
        # Check for excessive repetition (>50% repeated words)
        if len(words) > 5:
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            max_count = max(word_counts.values())
            if max_count > len(words) * 0.5:  # More than 50% repetition
                logger.debug(f"High repetition detected: {max_count}/{len(words)} words")
                return True
        
        # Check for consecutive repetitions (same word 3+ times in a row)
        for i in range(len(words) - 2):
            if words[i] == words[i+1] == words[i+2]:
                logger.debug(f"Consecutive repetition detected: '{words[i]}'")
                return True
        
        return False
    
    def transcribe_with_timestamps(
        self,
        audio: np.ndarray,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe with word-level timestamps.
        
        Args:
            audio: Audio data as numpy array
            language: Language code or None
        
        Returns:
            Dictionary with 'text', 'segments', and 'language'
        """
        # Convert int16 to float32 if needed
        if audio.dtype == np.int16:
            audio = audio.astype(np.float32) / 32768.0
        
        try:
            lang = language or self.language
            
            kwargs: Dict[str, Any] = {
                "path_or_hf_repo": self.model_name,
                "fp16": config.USE_FLOAT16,
                "word_timestamps": True
            }
            
            if lang:
                kwargs["language"] = lang
            
            result = mlx_whisper.transcribe(audio, **kwargs)
            
            return result
        
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return {"text": "", "segments": [], "language": ""}


def test_transcriber():
    """Test transcriber with recorded audio."""
    import sounddevice as sd
    
    print("Recording 5 seconds of audio...")
    audio = sd.rec(
        int(5 * config.SAMPLE_RATE),
        samplerate=config.SAMPLE_RATE,
        channels=1,
        dtype='int16'
    )
    sd.wait()
    audio = audio.flatten()
    
    print("Transcribing...")
    transcriber = WhisperTranscriber()
    text = transcriber.transcribe(audio)
    
    print(f"\nResult: {text}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_transcriber()
