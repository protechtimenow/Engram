"""
================================================================================
Engram Core Module - Production-Ready Implementation

A high-performance neural memory augmentation system based on DeepSeek's 
Engram architecture, featuring:
- Deterministic O(1) N-gram lookup via prime-based hashing
- Multi-head embedding tables for rich representation
- Gating mechanism for adaptive backbone fusion
- ShortConv for local pattern capture
- Compressed tokenizer with vocabulary reduction

Author: Engram Team
Version: 1.0.0
================================================================================
"""

__version__ = "1.0.0"
__author__ = "Engram Team"

from .config import EngramConfig, BackBoneConfig, ShortConvConfig
from .tokenizer import CompressedTokenizer
from .hashing import NgramHashMapping, find_next_prime
from .embedding import MultiHeadEmbedding
from .engram import EngramLayer, EngramModel

__all__ = [
    "EngramConfig",
    "BackBoneConfig", 
    "ShortConvConfig",
    "CompressedTokenizer",
    "NgramHashMapping",
    "find_next_prime",
    "MultiHeadEmbedding",
    "EngramLayer",
    "EngramModel",
]
