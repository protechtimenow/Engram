"""
================================================================================
[Engram Neural Hashing Implementation]

Enhanced neural hashing module for optimized context retention and computational efficiency.
Integrates with the existing Engram architecture for improved memory management.
================================================================================
"""

import torch
from typing import Dict, List
import numpy as np
from dataclasses import dataclass

from enum import Enum, auto

class TokenType(Enum):
    GENERAL = auto()
    FINANCIAL_ENTITY = auto()
    SENTIMENT = auto()
    MARKET_DATA = auto()

@dataclass
class NeuralHashConfig:
    # Dynamic prime configuration for hashing
    primes: List[int] = None
    financial_primes: List[int] = None
    max_context_length: int = 8192
    hash_window_size: int = 3
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    financial_keywords: List[str] = None
    
    def __post_init__(self):
        if self.primes is None:
            # Generate first 5 primes for hashing if not provided
            self.primes = [2, 3, 5, 7, 11]
        
        if self.financial_primes is None:
            # Larger primes for high-entropy financial data
            self.financial_primes = [101, 103, 107, 109, 113]
            
        if self.financial_keywords is None:
            # Basic financial keywords for classification
            self.financial_keywords = [
                "bull", "bear", "stock", "market", "trade", "price", 
                "volatility", "dividend", "yield", "short", "long", "call", "put"
            ]

class NeuralHashingModule:
    """
    Advanced neural hashing for context retention with prime-weighted XOR operations.
    """
    
    def __init__(self, config: NeuralHashConfig):
        self.config = config
        self.device = torch.device(config.device)
        
        # Initialize token-to-index mapping with primes
        self.token_to_index = {token: idx for idx, token in enumerate(config.primes)}
        
        # Sparse context memory tensor for efficient storage
        self.context_memory = torch.zeros(
            config.max_context_length, 
            dtype=torch.long, 
            device=self.device
        )
        
        # Position-aware weights for dynamic hashing
        self.position_weights = torch.tensor(
            config.primes, 
            dtype=torch.float32, 
            device=self.device
        )
        
        # Hash statistics for monitoring
        self.hash_stats = {
            "total_hashes": 0,
            "unique_hashes": set(),
            "collision_count": 0,
            "financial_hashes": 0
        }
        
        # Cache financial keywords for O(1) lookup
        self.financial_keywords_set = set(token.lower() for token in config.financial_keywords) if config.financial_keywords else set()

    def classify_token(self, token: str) -> TokenType:
        """
        Classifies a token into a specific type using keyword matching and heuristics.
        
        Args:
            token (str): Input token.
            
        Returns:
            TokenType: The classification of the token.
        """
        token_lower = token.lower()
        if token_lower in self.financial_keywords_set:
            return TokenType.FINANCIAL_ENTITY
        
        # Heuristic for tickers (e.g. $AAPL) or specific financial terms
        if token.startswith("$") and len(token) > 1 and token[1:].isalpha():
            return TokenType.FINANCIAL_ENTITY
            
        return TokenType.GENERAL
    
    def hash_token(self, token: str, position: int = 0) -> int:
        """
        Hashes a token using prime-indexed XOR weighting with position awareness.
        
        Args:
            token (str): Input token to hash.
            position (int): Position in sequence for dynamic weighting.
            
        Returns:
            int: Hash value derived from prime indices and bitwise XOR.
        """
        if token not in self.token_to_index:
            # Handle unknown tokens with fallback hashing
            token_hash = hash(token) % len(self.config.primes)
            idx = token_hash
        else:
            idx = self.token_to_index[token]
        
        # Determine token type and select prime set
        token_type = self.classify_token(token)
        if token_type == TokenType.FINANCIAL_ENTITY:
            primes_to_use = self.config.financial_primes
            # Add salt to index for financial tokens to separate from general space
            idx += 1000 
            self.hash_stats["financial_hashes"] += 1
        else:
            primes_to_use = self.config.primes
        
        # Weighted XOR hash: Prime * (index + position)
        weights = []
        for i, prime in enumerate(primes_to_use):
            weight = prime * (idx + position + i)
            weights.append(weight)
        
        # Combine weights using XOR and mod for overflow prevention
        combined_hash = 0
        for weight in weights:
            combined_hash ^= weight
        
        # Final hash with bitwise AND to prevent overflow
        final_hash = combined_hash & ((1 << 16) - 1)  # 16-bit hash
        
        # Update statistics
        self.hash_stats["total_hashes"] += 1
        if final_hash in self.hash_stats["unique_hashes"]:
            self.hash_stats["collision_count"] += 1
        else:
            self.hash_stats["unique_hashes"].add(final_hash)
        
        return final_hash
    
    def hash_sequence(self, tokens: List[str]) -> List[int]:
        """
        Hashes a sequence of tokens with position awareness.
        
        Args:
            tokens (List[str]): Input token sequence.
            
        Returns:
            List[int]: Hash values for the token sequence.
        """
        hashes = []
        for i, token in enumerate(tokens):
            hash_val = self.hash_token(token, position=i)
            hashes.append(hash_val)
        return hashes
    
    def update_context(self, tokens: List[str], hashes: List[int] = None) -> None:
        """
        Updates the context memory with hashed token IDs.
        
        Args:
            tokens (List[str]): Input tokens for context window.
            hashes (List[int]): Pre-computed hash values (optional).
        """
        if hashes is None:
            hashes = self.hash_sequence(tokens)
        
        # Convert to tensor and update context memory
        hash_tensor = torch.tensor(hashes, dtype=torch.long, device=self.device)
        
        # Ensure we don't exceed context memory bounds
        seq_len = min(len(hashes), self.config.max_context_length)
        
        # Update context memory with new hashes
        self.context_memory[:seq_len] = hash_tensor[:seq_len]
    
    def get_context_hashes(self, start_pos: int = 0, length: int = None) -> torch.Tensor:
        """
        Retrieves hashed context from memory.
        
        Args:
            start_pos (int): Starting position in context memory.
            length (int): Length of context to retrieve.
            
        Returns:
            torch.Tensor: Context hash values.
        """
        if length is None:
            return self.context_memory[start_pos:]
        else:
            end_pos = min(start_pos + length, self.config.max_context_length)
            return self.context_memory[start_pos:end_pos]
    
    def reset_context(self) -> None:
        """Resets the context memory and statistics."""
        self.context_memory.zero_()
        self.hash_stats = {
            "total_hashes": 0,
            "unique_hashes": set(),
            "collision_count": 0
        }
    
    def get_hash_statistics(self) -> Dict:
        """
        Returns current hashing statistics.
        
        Returns:
            Dict: Hashing performance metrics.
        """
        return {
            "total_hashes": self.hash_stats["total_hashes"],
            "unique_hashes": len(self.hash_stats["unique_hashes"]),
            "collision_count": self.hash_stats["collision_count"],
            "collision_rate": (
                self.hash_stats["collision_count"] / max(1, self.hash_stats["total_hashes"])
            ),
            "financial_hashes": self.hash_stats["financial_hashes"],
            "memory_utilization": (
                torch.count_nonzero(self.context_memory).item() / 
                self.config.max_context_length
            )
        }
    
    def integrate_with_engram(self, engram_layer_output: torch.Tensor) -> torch.Tensor:
        """
        Integrates neural hashing with existing Engram layer output.
        
        Args:
            engram_layer_output (torch.Tensor): Output from Engram layer.
            
        Returns:
            torch.Tensor: Enhanced output with hash-based context.
        """
        batch_size, seq_len, hidden_dim = engram_layer_output.shape
        
        # Get context hashes for the sequence
        context_hashes = self.get_context_hashes(length=seq_len)
        
        # Expand hashes to match hidden dimension
        hash_embeddings = self._hash_to_embedding(context_hashes, hidden_dim)
        
        # Combine with Engram output
        enhanced_output = engram_layer_output + hash_embeddings.unsqueeze(0)
        
        return enhanced_output
    
    def _hash_to_embedding(self, hashes: torch.Tensor, embed_dim: int) -> torch.Tensor:
        """
        Converts hash values to embedding-like representations.
        
        Args:
            hashes (torch.Tensor): Hash values.
            embed_dim (int): Target embedding dimension.
            
        Returns:
            torch.Tensor: Hash-based embeddings.
        """
        # Simple hash-to-embedding conversion using sine/cosine encoding
        positions = torch.arange(embed_dim, device=self.device, dtype=torch.float32)
        div_term = torch.exp(
            torch.arange(0, embed_dim, 2, device=self.device, dtype=torch.float32) * 
            -(np.log(10000.0) / embed_dim)
        )
        
        # Convert hashes to float for encoding
        hash_floats = hashes.float().unsqueeze(-1)
        
        # Apply positional encoding-like transformation
        embeddings = torch.zeros_like(hash_floats.expand(-1, embed_dim))
        embeddings[:, 0::2] = torch.sin(hash_floats[:, 0::2] * div_term)
        embeddings[:, 1::2] = torch.cos(hash_floats[:, 1::2] * div_term)
        
        return embeddings

# Factory function for easy integration
def create_neural_hash_module(primes: List[int] = None, max_context: int = 8192) -> NeuralHashingModule:
    """
    Creates a neural hashing module with default configuration.
    
    Args:
        primes (List[int]): Prime numbers for hashing.
        max_context (int): Maximum context length.
        
    Returns:
        NeuralHashingModule: Configured neural hashing module.
    """
    config = NeuralHashConfig(primes=primes, max_context_length=max_context)
    return NeuralHashingModule(config)

# Example usage and testing
if __name__ == "__main__":
    # Create neural hashing module
    neural_hash = create_neural_hash_module()
    
    # Test with sample tokens
    test_tokens = ["engram", "local", "context", "neural", "hashing"]
    
    # Hash the sequence
    hashes = neural_hash.hash_sequence(test_tokens)
    print(f"Token hashes: {dict(zip(test_tokens, hashes))}")
    
    # Update context
    neural_hash.update_context(test_tokens, hashes)
    
    # Get context hashes
    context = neural_hash.get_context_hashes(length=len(test_tokens))
    print(f"Context hashes: {context}")
    
    # Get statistics
    stats = neural_hash.get_hash_statistics()
    print(f"Hash statistics: {stats}")
    
    # Test integration with tensor
    test_tensor = torch.randn(1, len(test_tokens), 512)
    enhanced = neural_hash.integrate_with_engram(test_tensor)
    print(f"Enhanced tensor shape: {enhanced.shape}")
    
    print("✅ Neural Hashing Module Test Complete!")