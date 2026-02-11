"""
================================================================================
Engram Configuration Module

Defines configuration dataclasses for the Engram architecture with validation
and sensible defaults.
================================================================================
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class ShortConvConfig:
    """Configuration for ShortConv local pattern capture module.
    
    Args:
        kernel_size: Convolution kernel size (default: 4)
        dilation: Dilation rate for expanded receptive field (default: 1)
        norm_eps: Epsilon for normalization stability (default: 1e-5)
        activation: Whether to apply SiLU activation (default: True)
    """
    kernel_size: int = 4
    dilation: int = 1
    norm_eps: float = 1e-5
    activation: bool = True
    
    def __post_init__(self):
        if self.kernel_size < 1:
            raise ValueError(f"kernel_size must be >= 1, got {self.kernel_size}")
        if self.dilation < 1:
            raise ValueError(f"dilation must be >= 1, got {self.dilation}")
        if self.norm_eps <= 0:
            raise ValueError(f"norm_eps must be > 0, got {self.norm_eps}")


@dataclass
class EngramConfig:
    """Configuration for the Engram memory augmentation module.
    
    This configuration defines the architecture parameters for deterministic
    N-gram hashing-based memory retrieval with multi-head embeddings.
    
    Args:
        tokenizer_name_or_path: HuggingFace tokenizer identifier or local path
        engram_vocab_size: List of vocabulary sizes for each n-gram size [2-gram, 3-gram, ...]
        max_ngram_size: Maximum n-gram size to consider (default: 3)
        n_embed_per_ngram: Embedding dimension per n-gram (default: 512)
        n_head_per_ngram: Number of attention heads per n-gram (default: 8)
        layer_ids: List of transformer layer IDs to apply Engram (default: [1, 15])
        pad_id: Token ID for padding (default: 2)
        seed: Random seed for deterministic hashing (default: 0)
        kernel_size: ShortConv kernel size (default: 4)
        device: Computation device (default: "cuda" if available else "cpu")
        dtype: PyTorch data type (default: torch.float32)
    """
    tokenizer_name_or_path: str = "deepseek-ai/DeepSeek-V3"
    engram_vocab_size: List[int] = field(default_factory=lambda: [129280*5, 129280*5])
    max_ngram_size: int = 3
    n_embed_per_ngram: int = 512
    n_head_per_ngram: int = 8
    layer_ids: List[int] = field(default_factory=lambda: [1, 15])
    pad_id: int = 2
    seed: int = 0
    kernel_size: int = 4
    device: str = "cuda"
    dtype: Optional[str] = "float32"
    
    # Advanced settings
    use_cache: bool = True
    cache_size: int = 10000
    
    def __post_init__(self):
        # Validate n-gram sizes
        if self.max_ngram_size < 2:
            raise ValueError(f"max_ngram_size must be >= 2, got {self.max_ngram_size}")
        
        expected_vocab_sizes = self.max_ngram_size - 1
        if len(self.engram_vocab_size) != expected_vocab_sizes:
            raise ValueError(
                f"engram_vocab_size must have {expected_vocab_sizes} elements "
                f"for max_ngram_size={self.max_ngram_size}, got {len(self.engram_vocab_size)}"
            )
        
        # Validate embedding dimensions
        if self.n_embed_per_ngram % self.n_head_per_ngram != 0:
            raise ValueError(
                f"n_embed_per_ngram ({self.n_embed_per_ngram}) must be divisible by "
                f"n_head_per_ngram ({self.n_head_per_ngram})"
            )
        
        # Validate layer IDs
        if not self.layer_ids:
            raise ValueError("layer_ids cannot be empty")
        
        # Validate device
        import torch
        if self.device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA not available, falling back to CPU")
            self.device = "cpu"
        
        # Parse dtype
        dtype_map = {
            "float32": torch.float32,
            "float16": torch.float16,
            "bfloat16": torch.bfloat16,
        }
        if isinstance(self.dtype, str):
            if self.dtype not in dtype_map:
                raise ValueError(f"Unsupported dtype: {self.dtype}")
            self.dtype = dtype_map[self.dtype]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "tokenizer_name_or_path": self.tokenizer_name_or_path,
            "engram_vocab_size": self.engram_vocab_size,
            "max_ngram_size": self.max_ngram_size,
            "n_embed_per_ngram": self.n_embed_per_ngram,
            "n_head_per_ngram": self.n_head_per_ngram,
            "layer_ids": self.layer_ids,
            "pad_id": self.pad_id,
            "seed": self.seed,
            "kernel_size": self.kernel_size,
            "device": self.device,
            "use_cache": self.use_cache,
            "cache_size": self.cache_size,
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "EngramConfig":
        """Create config from dictionary."""
        return cls(**config_dict)


@dataclass
class BackBoneConfig:
    """Configuration for the backbone transformer model.
    
    Args:
        hidden_size: Hidden dimension of the backbone (default: 1024)
        hc_mult: Hyper-connection multiplier (default: 4)
        vocab_size: Vocabulary size of the tokenizer (default: 129280)
        num_layers: Number of transformer layers (default: 30)
        num_attention_heads: Number of attention heads (default: 16)
        intermediate_size: FFN intermediate dimension (default: 4096)
        dropout: Dropout rate (default: 0.1)
    """
    hidden_size: int = 1024
    hc_mult: int = 4
    vocab_size: int = 129280
    num_layers: int = 30
    num_attention_heads: int = 16
    intermediate_size: int = 4096
    dropout: float = 0.1
    
    def __post_init__(self):
        if self.hidden_size % self.num_attention_heads != 0:
            raise ValueError(
                f"hidden_size ({self.hidden_size}) must be divisible by "
                f"num_attention_heads ({self.num_attention_heads})"
            )
        if self.hc_mult < 1:
            raise ValueError(f"hc_mult must be >= 1, got {self.hc_mult}")
