"""
Wake Word Detection
Detects trigger phrases like "hey jheevis" to activate the assistant
"""

import logging
from typing import List, Optional
from difflib import SequenceMatcher

import config

logger = logging.getLogger(__name__)


class WakeWordDetector:
    """
    Detects wake words in transcribed text using fuzzy matching.
    Simple implementation based on string similarity.
    """
    
    def __init__(
        self,
        wake_word: str = config.WAKE_WORD,
        alternatives: List[str] = None,
        threshold: float = config.WAKE_WORD_THRESHOLD
    ):
        """
        Initialize wake word detector.
        
        Args:
            wake_word: Primary wake word phrase
            alternatives: Alternative wake words
            threshold: Similarity threshold (0-1)
        """
        self.wake_word = wake_word.lower() if wake_word else None
        self.alternatives = [alt.lower() for alt in (alternatives or config.WAKE_WORD_ALTERNATIVES)]
        self.threshold = threshold
        
        self.all_wake_words = [self.wake_word] + self.alternatives if self.wake_word else self.alternatives
        
        logger.info(f"Wake words: {self.all_wake_words}")
        logger.info(f"Threshold: {threshold}")
    
    def detect(self, text: str) -> bool:
        """
        Check if text contains a wake word.
        
        Args:
            text: Transcribed text to check
        
        Returns:
            True if wake word detected
        """
        if not self.all_wake_words:
            # No wake word configured - always return True
            return True
        
        text_lower = text.lower().strip()
        
        # Check for exact matches first
        for wake_word in self.all_wake_words:
            if wake_word in text_lower:
                logger.info(f"Wake word detected (exact): '{wake_word}'")
                return True
        
        # Check for fuzzy matches
        for wake_word in self.all_wake_words:
            similarity = self._similarity(wake_word, text_lower)
            if similarity >= self.threshold:
                logger.info(f"Wake word detected (fuzzy): '{wake_word}' (similarity: {similarity:.2f})")
                return True
        
        logger.debug(f"No wake word in: '{text}'")
        return False
    
    def extract_command(self, text: str) -> Optional[str]:
        """
        Extract the command part after the wake word.
        
        Args:
            text: Full transcribed text
        
        Returns:
            Command text without wake word, or None if no wake word
        """
        text_lower = text.lower().strip()
        
        # Find the wake word and extract command after it
        for wake_word in self.all_wake_words:
            if wake_word in text_lower:
                # Split on wake word and take everything after
                parts = text_lower.split(wake_word, 1)
                if len(parts) > 1:
                    command = parts[1].strip()
                    if command:
                        logger.debug(f"Extracted command: '{command}'")
                        return command
                
                # If nothing after wake word, return original text
                # (user might say just "hey jheevis")
                return text.strip()
        
        # No wake word found - return original text
        return text.strip()
    
    def _similarity(self, a: str, b: str) -> float:
        """
        Calculate similarity between two strings.
        
        Args:
            a: First string
            b: Second string
        
        Returns:
            Similarity score (0-1)
        """
        # Use SequenceMatcher for fuzzy matching
        matcher = SequenceMatcher(None, a, b)
        return matcher.ratio()
    
    def is_enabled(self) -> bool:
        """Check if wake word detection is enabled."""
        return bool(self.all_wake_words) and config.ENABLE_WAKE_WORD


def test_wake_word():
    """Test wake word detection."""
    detector = WakeWordDetector()
    
    test_cases = [
        "hey jheevis what's the weather",
        "jheevis open safari",
        "hey computer play music",
        "what time is it",  # Should not match
        "hey jheevas",  # Fuzzy match
        "hey jheevis",  # Just wake word
    ]
    
    for text in test_cases:
        detected = detector.detect(text)
        if detected:
            command = detector.extract_command(text)
            print(f"✅ '{text}' → Command: '{command}'")
        else:
            print(f"❌ '{text}' → No wake word")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_wake_word()
