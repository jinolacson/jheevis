"""
MLX LLM Integration
Language model for conversation and command understanding
"""

import mlx.core as mx
from mlx_lm import load, generate
import logging
from typing import Optional, Tuple, Any

import config

logger = logging.getLogger(__name__)


class MLXLanguageModel:
    """
    Wrapper for MLX-optimized language models.
    Handles loading, caching, and text generation.
    """
    
    def __init__(
        self,
        model_name: str = config.LLM_MODEL,
        max_tokens: int = config.LLM_MAX_TOKENS,
        temperature: float = config.LLM_TEMPERATURE
    ):
        """
        Initialize MLX LLM.
        
        Args:
            model_name: Model identifier (e.g., 'mlx-community/Llama-3.2-3B-Instruct-4bit')
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1, higher is more random)
        """
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        self.model = None
        self.tokenizer = None
        
        logger.info(f"Initializing LLM: {model_name}")
    
    def load_model(self):
        """Load the model and tokenizer."""
        if self.model is not None and self.tokenizer is not None:
            logger.debug("Model already loaded")
            return
        
        logger.info("Loading model... (this may take a moment)")
        self.model, self.tokenizer = load(self.model_name)
        logger.info("Model loaded successfully")
    
    def generate_response(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: float = config.LLM_TOP_P,
        stop_tokens: Optional[list] = None
    ) -> str:
        """
        Generate text response from prompt.
        
        Args:
            prompt: Input prompt
            max_tokens: Override max tokens
            temperature: Override temperature
            top_p: Nucleus sampling parameter
            stop_tokens: List of stop tokens
        
        Returns:
            Generated text
        """
        # Ensure model is loaded
        self.load_model()
        
        # Use instance settings if not overridden
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature or self.temperature
        
        logger.debug(f"Generating response (max_tokens={max_tokens}, temp={temperature})")
        
        try:
            # Generate using MLX LM
            response = generate(
                model=self.model,
                tokenizer=self.tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                verbose=False
            )
            
            # Clean up response
            response = response.strip()
            
            logger.debug(f"Generated: '{response[:100]}...'")
            return response
        
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return ""
    
    def chat_completion(
        self,
        messages: list,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate response in chat format.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
                     Example: [{"role": "user", "content": "Hello"}]
            max_tokens: Override max tokens
            temperature: Override temperature
        
        Returns:
            Assistant's response
        """
        # Convert messages to prompt format
        prompt = self._format_chat_prompt(messages)
        
        # Generate response
        response = self.generate_response(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response
    
    def _format_chat_prompt(self, messages: list) -> str:
        """
        Format messages into Llama-style chat prompt.
        
        Args:
            messages: List of message dictionaries
        
        Returns:
            Formatted prompt string
        """
        # Llama 3 chat template
        prompt = ""
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                prompt += f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{content}<|eot_id|>"
            elif role == "user":
                prompt += f"<|start_header_id|>user<|end_header_id|>\n\n{content}<|eot_id|>"
            elif role == "assistant":
                prompt += f"<|start_header_id|>assistant<|end_header_id|>\n\n{content}<|eot_id|>"
        
        # Add assistant header for response
        prompt += "<|start_header_id|>assistant<|end_header_id|>\n\n"
        
        return prompt
    
    def unload_model(self):
        """Unload model from memory."""
        self.model = None
        self.tokenizer = None
        logger.info("Model unloaded")


def test_llm():
    """Test LLM generation."""
    llm = MLXLanguageModel()
    
    # Test simple generation
    print("Testing simple generation...")
    response = llm.generate_response("What is the capital of France? Answer briefly:")
    print(f"Response: {response}\n")
    
    # Test chat completion
    print("Testing chat completion...")
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Keep answers brief."},
        {"role": "user", "content": "What's 2+2?"}
    ]
    response = llm.chat_completion(messages)
    print(f"Response: {response}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_llm()
