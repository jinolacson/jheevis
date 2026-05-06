"""
Conversation History Manager
Maintains chat context for multi-turn conversations
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import json

import config

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Represents a single message in conversation."""
    role: str  # 'system', 'user', or 'assistant'
    content: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        """Create from dictionary."""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat()))
        )


class ConversationHistory:
    """
    Manages conversation history with context window management.
    """
    
    def __init__(
        self,
        system_prompt: str = config.SYSTEM_PROMPT,
        max_length: int = config.MAX_HISTORY_LENGTH
    ):
        """
        Initialize conversation history.
        
        Args:
            system_prompt: System message to set assistant behavior
            max_length: Maximum number of messages to keep
        """
        self.system_prompt = system_prompt
        self.max_length = max_length
        self.messages: List[Message] = []
        
        # Add system message
        if system_prompt:
            self.messages.append(Message(role="system", content=system_prompt))
        
        logger.info(f"Conversation history initialized (max length: {max_length})")
    
    def add_user_message(self, content: str):
        """Add user message to history."""
        msg = Message(role="user", content=content)
        self.messages.append(msg)
        self._trim_history()
        logger.debug(f"User: {content}")
    
    def add_assistant_message(self, content: str):
        """Add assistant message to history."""
        msg = Message(role="assistant", content=content)
        self.messages.append(msg)
        self._trim_history()
        logger.debug(f"Assistant: {content}")
    
    def add_system_message(self, content: str):
        """Add system message to history."""
        msg = Message(role="system", content=content)
        self.messages.append(msg)
        self._trim_history()
        logger.debug(f"System: {content}")
    
    def get_messages(self) -> List[Dict]:
        """
        Get all messages as list of dictionaries.
        
        Returns:
            List of message dicts with 'role' and 'content'
        """
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]
    
    def get_context(self) -> str:
        """
        Get conversation context as formatted string.
        
        Returns:
            Formatted conversation history
        """
        lines = []
        for msg in self.messages:
            role_label = msg.role.upper()
            lines.append(f"{role_label}: {msg.content}")
        return "\n".join(lines)
    
    def clear(self):
        """Clear all messages except system prompt."""
        system_messages = [msg for msg in self.messages if msg.role == "system"]
        self.messages = system_messages
        logger.info("Conversation history cleared")
    
    def _trim_history(self):
        """Trim history to max length, keeping system messages."""
        if len(self.messages) <= self.max_length:
            return
        
        # Keep system messages and most recent messages
        system_messages = [msg for msg in self.messages if msg.role == "system"]
        other_messages = [msg for msg in self.messages if msg.role != "system"]
        
        # Calculate how many non-system messages to keep
        max_other = self.max_length - len(system_messages)
        
        if len(other_messages) > max_other:
            # Keep only most recent
            other_messages = other_messages[-max_other:]
            logger.debug(f"Trimmed history to {len(other_messages)} messages")
        
        self.messages = system_messages + other_messages
    
    def save_to_file(self, filename: str):
        """Save conversation to JSON file."""
        data = {
            "system_prompt": self.system_prompt,
            "messages": [msg.to_dict() for msg in self.messages]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Conversation saved to {filename}")
    
    def load_from_file(self, filename: str):
        """Load conversation from JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        self.system_prompt = data.get("system_prompt", "")
        self.messages = [Message.from_dict(msg) for msg in data.get("messages", [])]
        
        logger.info(f"Conversation loaded from {filename} ({len(self.messages)} messages)")
    
    def get_last_user_message(self) -> Optional[str]:
        """Get the most recent user message."""
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg.content
        return None
    
    def get_last_assistant_message(self) -> Optional[str]:
        """Get the most recent assistant message."""
        for msg in reversed(self.messages):
            if msg.role == "assistant":
                return msg.content
        return None
    
    def __len__(self) -> int:
        """Get number of messages."""
        return len(self.messages)


def test_history():
    """Test conversation history."""
    history = ConversationHistory(system_prompt="You are a helpful assistant.")
    
    # Add some messages
    history.add_user_message("What's the weather?")
    history.add_assistant_message("I don't have access to weather data.")
    history.add_user_message("What's 2+2?")
    history.add_assistant_message("2+2 equals 4.")
    
    # Print context
    print("Conversation context:")
    print(history.get_context())
    print()
    
    # Get messages for LLM
    messages = history.get_messages()
    print("Messages for LLM:")
    for msg in messages:
        print(f"  {msg['role']}: {msg['content']}")
    print()
    
    # Test trimming
    print(f"Total messages: {len(history)}")
    
    # Save and load
    history.save_to_file("test_conversation.json")
    
    new_history = ConversationHistory()
    new_history.load_from_file("test_conversation.json")
    print(f"Loaded {len(new_history)} messages")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_history()
