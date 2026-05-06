"""
Audio Utilities
Helper functions for audio recording and playback
"""

import sounddevice as sd
import numpy as np
import logging
from typing import Optional

import config

logger = logging.getLogger(__name__)


def record_audio(duration: float = 5.0, sample_rate: int = config.SAMPLE_RATE) -> np.ndarray:
    """
    Record audio from microphone.
    
    Args:
        duration: Recording duration in seconds
        sample_rate: Sample rate in Hz
    
    Returns:
        Audio data as numpy array
    """
    logger.debug(f"Recording {duration}s of audio at {sample_rate}Hz...")
    
    try:
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=config.CHANNELS,
            dtype='int16'
        )
        sd.wait()
        
        # Flatten if stereo
        if audio.ndim > 1:
            audio = audio.flatten()
        
        max_amplitude = np.max(np.abs(audio))
        logger.debug(f"Recorded {len(audio)} samples (max amplitude: {max_amplitude})")
        
        return audio
    
    except Exception as e:
        logger.error(f"Recording error: {e}")
        return np.array([], dtype=np.int16)


def play_audio(audio: np.ndarray, sample_rate: int = config.PLAYBACK_SAMPLE_RATE):
    """
    Play audio through speakers.
    
    Args:
        audio: Audio data as numpy array
        sample_rate: Sample rate in Hz
    """
    logger.debug(f"Playing {len(audio)} samples at {sample_rate}Hz...")
    
    try:
        # Ensure audio is in correct format
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)
        
        # Normalize if needed
        max_val = np.max(np.abs(audio))
        if max_val > 1.0:
            audio = audio / max_val
        
        sd.play(audio, sample_rate)
        sd.wait()
        
        logger.debug("Playback complete")
    
    except Exception as e:
        logger.error(f"Playback error: {e}")


def play_beep(frequency: int = 800, duration: float = 0.2):
    """
    Play a beep sound.
    
    Args:
        frequency: Frequency in Hz
        duration: Duration in seconds
    """
    try:
        sample_rate = config.PLAYBACK_SAMPLE_RATE
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.3 * np.sin(2 * np.pi * frequency * t)
        
        sd.play(audio, sample_rate)
        sd.wait()
    
    except Exception as e:
        logger.error(f"Beep error: {e}")


def get_microphone_devices() -> list:
    """
    Get list of available microphone devices.
    
    Returns:
        List of device dictionaries
    """
    try:
        devices = sd.query_devices()
        mics = []
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                mics.append({
                    'index': i,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': int(device['default_samplerate'])
                })
        
        return mics
    
    except Exception as e:
        logger.error(f"Error querying devices: {e}")
        return []


def set_default_microphone(device_index: int):
    """
    Set default input device.
    
    Args:
        device_index: Device index from get_microphone_devices()
    """
    try:
        sd.default.device[0] = device_index
        logger.info(f"Set default microphone to device {device_index}")
    
    except Exception as e:
        logger.error(f"Error setting microphone: {e}")


def test_audio():
    """Test audio utilities."""
    print("=== Audio Utilities Test ===\n")
    
    # List microphones
    print("Available Microphones:")
    mics = get_microphone_devices()
    for mic in mics:
        print(f"  [{mic['index']}] {mic['name']}")
        print(f"      {mic['channels']} channels, {mic['sample_rate']}Hz")
    print()
    
    # Play beep
    print("Playing beep...")
    play_beep()
    print()
    
    # Record audio
    print("Recording 3 seconds...")
    audio = record_audio(duration=3.0)
    print(f"Recorded {len(audio)} samples\n")
    
    # Play back
    print("Playing back recording...")
    # Convert to float for playback
    audio_float = audio.astype(np.float32) / 32768.0
    play_audio(audio_float, sample_rate=config.SAMPLE_RATE)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_audio()
