"""
================================================================================
[Engram Neural Hashing Integration]

Integration module that combines the neural hashing enhancements with the existing
Engram architecture for optimized context retention and performance.
================================================================================
"""

import torch
import torch.nn as nn
from typing import List, Dict, Optional
import numpy as np

from neural_hashing import NeuralHashingModule, NeuralHashConfig, create_neural_hash_module
from engram_demo_v1 import EngramConfig, Engram, NgramHashMapping

class EnhancedEngramConfig(EngramConfig):
    """Extended configuration for neural hashing integration."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Neural hashing specific configurations
        self.neural_hash_primes = [2, 3, 5, 7, 11, 13, 17, 19]
        self.neural_hash_financial_primes = [101, 103, 107, 109, 113, 127]
        self.neural_hash_context_length = 8192
        self.neural_hash_device = "cuda" if torch.cuda.is_available() else "cpu"
        self.enable_neural_hashing = True
        self.hash_integration_weight = 0.1  # Weight for hash-based context
        self.neural_hash_financial_keywords = None # Use default if None

class EnhancedEngram(nn.Module):
    """
    Enhanced Engram layer with neural hashing integration.
    """
    
    def __init__(self, layer_id: int, config: Optional[EnhancedEngramConfig] = None):
        super().__init__()
        self.layer_id = layer_id
        self.config = config or EnhancedEngramConfig()
        
        # Original Engram components
        self.original_engram = Engram(layer_id=layer_id)
        
        # Neural hashing components
        if self.config.enable_neural_hashing:
            self.neural_hash_config = NeuralHashConfig(
                primes=self.config.neural_hash_primes,
                financial_primes=self.config.neural_hash_financial_primes,
                max_context_length=self.config.neural_hash_context_length,
                device=self.config.neural_hash_device,
                financial_keywords=self.config.neural_hash_financial_keywords
            )
            self.neural_hasher = NeuralHashingModule(self.neural_hash_config)
            
            # Integration layer for combining original and neural hash outputs
            # Use the backbone hidden size for proper dimensions
            from engram_demo_v1 import backbone_config
            self.hash_integration = nn.Linear(
                backbone_config.hidden_size,
                backbone_config.hidden_size
            )
            self.integration_weight = nn.Parameter(
                torch.tensor(self.config.hash_integration_weight)
            )
    
    def forward(self, hidden_states: torch.Tensor, input_ids: torch.Tensor) -> torch.Tensor:
        """
        Forward pass with neural hashing integration.
        
        Args:
            hidden_states: [B, L, HC_MULT, D] - Input hidden states
            input_ids: [B, L] - Input token IDs
            
        Returns:
            torch.Tensor: Enhanced output with neural hashing context
        """
        # Get original Engram output
        original_output = self.original_engram(hidden_states, input_ids)
        
        if not self.config.enable_neural_hashing:
            return original_output
        
        # Convert input_ids to tokens for neural hashing
        tokens = self._input_ids_to_tokens(input_ids)
        
        # Update neural hash context
        batch_size, seq_len = input_ids.shape
        for batch_idx in range(batch_size):
            batch_tokens = tokens[batch_idx]
            self.neural_hasher.update_context(batch_tokens)
        
        # Get neural hash integration
        hash_enhanced = self.neural_hasher.integrate_with_engram(
            original_output[:, :, 0, :]  # Take first head for integration
        )
        
        # Expand hash_enhanced to match original output dimensions
        hash_enhanced_expanded = hash_enhanced.unsqueeze(2).expand(
            -1, -1, original_output.size(2), -1
        )
        
        # Combine original and hash-enhanced outputs
        integrated_output = original_output + self.integration_weight * hash_enhanced_expanded
        
        return integrated_output
    
    def _input_ids_to_tokens(self, input_ids: torch.Tensor) -> List[List[str]]:
        """
        Convert input IDs to token strings for neural hashing.
        
        Args:
            input_ids: [B, L] - Input token IDs
            
        Returns:
            List[List[str]]: Token strings for each batch
        """
        # Use the original Engram's tokenizer
        tokenizer = self.original_engram.hash_mapping.compressed_tokenizer.tokenizer
        
        tokens = []

        for batch_idx in range(input_ids.size(0)):
            batch_ids = input_ids[batch_idx].tolist()
            batch_tokens = tokenizer.convert_ids_to_tokens(batch_ids)
            # Clean up special tokens but PRESERVE length for tensor alignment
            cleaned_tokens = []
            for token in batch_tokens:
                # Replace special chars
                clean = token.replace("Ġ", "").replace("▁", "").strip()
                # Use a placeholder for special tokens if needed, or just keep them
                # Start of sentence/pad tokens shouldn't break neural hashing, 
                # they just get hashed as general tokens.
                cleaned_tokens.append(clean)
            
            tokens.append(cleaned_tokens)
        
        return tokens
    
    def get_hash_statistics(self) -> Dict:
        """Returns neural hashing performance statistics."""
        if not self.config.enable_neural_hashing:
            return {"neural_hashing_enabled": False}
        
        return self.neural_hasher.get_hash_statistics()
    
    def reset_hash_context(self) -> None:
        """Resets the neural hashing context memory."""
        if self.config.enable_neural_hashing:
            self.neural_hasher.reset_context()

class EngramNeuralHashBridge:
    """
    Bridge class for seamless integration between existing Engram architecture
    and neural hashing enhancements.
    """
    
    def __init__(self, config: Optional[EnhancedEngramConfig] = None):
        self.config = config or EnhancedEngramConfig()
        self.enhanced_layers = {}
        
    def create_enhanced_layer(self, layer_id: int) -> EnhancedEngram:
        """
        Creates an enhanced Engram layer for the given layer ID.
        
        Args:
            layer_id: Layer identifier
            
        Returns:
            EnhancedEngram: Configured enhanced layer
        """
        if layer_id not in self.enhanced_layers:
            self.enhanced_layers[layer_id] = EnhancedEngram(layer_id, self.config)
        return self.enhanced_layers[layer_id]
    
    def get_layer_statistics(self, layer_id: Optional[int] = None) -> Dict:
        """
        Gets statistics for specific layer or all layers.
        
        Args:
            layer_id: Specific layer ID (None for all layers)
            
        Returns:
            Dict: Layer statistics
        """
        if layer_id is not None:
            if layer_id in self.enhanced_layers:
                return self.enhanced_layers[layer_id].get_hash_statistics()
            else:
                return {"error": f"Layer {layer_id} not found"}
        
        # Return statistics for all layers
        all_stats = {}
        for lid, layer in self.enhanced_layers.items():
            all_stats[lid] = layer.get_hash_statistics()
        return all_stats
    
    def reset_all_contexts(self) -> None:
        """Resets neural hashing context for all layers."""
        for layer in self.enhanced_layers.values():
            layer.reset_hash_context()

# Utility functions for easy integration
def create_engram_neural_hash_bridge(
    primes: List[int] = None,
    max_context: int = 8192,
    integration_weight: float = 0.1
) -> EngramNeuralHashBridge:
    """
    Creates a configured Engram-Neural Hash bridge.
    
    Args:
        primes: Prime numbers for hashing
        max_context: Maximum context length
        integration_weight: Weight for hash integration
        
    Returns:
        EngramNeuralHashBridge: Configured bridge
    """
    config = EnhancedEngramConfig()
    if primes:
        config.neural_hash_primes = primes
    config.neural_hash_context_length = max_context
    config.hash_integration_weight = integration_weight
    
    return EngramNeuralHashBridge(config)

# Testing and demonstration
if __name__ == "__main__":
    print("🚀 Testing Engram Neural Hash Integration...")
    
    # Create bridge
    bridge = create_engram_neural_hash_bridge()
    
    # Create enhanced layer
    enhanced_layer = bridge.create_enhanced_layer(layer_id=1)
    
    # Test with dummy data
    batch_size, seq_len = 2, 10
    hidden_dim = 1024
    hc_mult = 4
    
    # Create dummy inputs
    hidden_states = torch.randn(batch_size, seq_len, hc_mult, hidden_dim)
    input_ids = torch.randint(0, 1000, (batch_size, seq_len))
    
    print(f"Input shapes: hidden_states={hidden_states.shape}, input_ids={input_ids.shape}")
    
    # Forward pass
    with torch.no_grad():
        output = enhanced_layer(hidden_states, input_ids)
    
    print(f"Output shape: {output.shape}")
    
    # Get statistics
    stats = enhanced_layer.get_hash_statistics()
    print(f"Hash statistics: {stats}")
    
    # Test bridge statistics
    bridge_stats = bridge.get_layer_statistics()
    print(f"Bridge statistics: {bridge_stats}")
    
    print("✅ Engram Neural Hash Integration Test Complete!")