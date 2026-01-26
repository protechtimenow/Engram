import os
import math
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.checkpoint import checkpoint
from dataclasses import dataclass
from typing import List, Dict
import hashlib

# ==========================================
# ShortConv Core Architecture
# ==========================================

class GatedLinearUnit(nn.Module):
    """GLU activation helper for architecture efficiency."""
    def __init__(self, hidden_size):
        super().__init__()
        self.gate_proj = nn.Linear(hidden_size, hidden_size)
        self.val_proj = nn.Linear(hidden_size, hidden_size)

    def forward(self, x):
        return self.val_proj(x) * torch.sigmoid(self.gate_proj(x))

class ShortConvBlock(nn.Module):
    """
    Causal Short Convolution Block.
    Optimized for sequences up to 8192 tokens.
    Uses depthwise 1D convolutions with causal padding.
    """
    def __init__(self, dim, kernel_size=4, expansion_factor=2):
        super().__init__()
        self.dim = dim
        self.expand_dim = dim * expansion_factor
        
        self.pre_norm = nn.RMSNorm(dim)
        self.proj_in = nn.Linear(dim, self.expand_dim * 2) # For Gated Linear logic
        
        # Depthwise Causal Conv
        self.conv = nn.Conv1d(
            in_channels=self.expand_dim,
            out_channels=self.expand_dim,
            kernel_size=kernel_size,
            groups=self.expand_dim,
            padding=kernel_size - 1,
            bias=False
        )
        
        self.proj_out = nn.Linear(self.expand_dim, dim)
        self.kernel_size = kernel_size

    def forward(self, x):
        B, L, D = x.shape
        residual = x
        
        x = self.pre_norm(x)
        gate_val = self.proj_in(x)
        gate, val = gate_val.chunk(2, dim=-1)
        
        # Causal Conv on val path
        val = val.transpose(1, 2) # B, ED, L
        val = self.conv(val)[:, :, :L] # Shifted for causality
        val = val.transpose(1, 2) # B, L, ED
        
        # SwiGLU-like gating
        x = F.silu(gate) * val
        x = self.proj_out(x)
        
        return x + residual

# ==========================================
# Tiny-Llama-ShortConv Model
# ==========================================

@dataclass
class ModelConfig:
    dim: int = 512
    n_layers: int = 12
    n_heads: int = 8
    vocab_size: int = 32000
    max_seq_len: int = 8192
    grad_checkpointing: bool = True
    use_engram: bool = True
    engram_dim: int = 128

class NeuralEngramMemory(nn.Module):
    """
    Implements Neural Hashing for localized memory.
    Uses prime-indexed XOR weighting for context-aware embeddings.
    """
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        self.register_buffer("primes", torch.tensor([2, 3, 5, 7, 11, 13, 17, 19, 23, 29], dtype=torch.long))
        self.hash_dim = len(self.primes)
        self.memory_proj = nn.Linear(1, config.engram_dim)
        
    def hash_tokens(self, tokens: torch.Tensor) -> torch.Tensor:
        """
        Bitwise XOR hashing using prime numbers.
        Tokens shape: (B, L)
        Returns: (B, L, hash_dim)
        """
        B, L = tokens.shape
        # Create weighted indices for each prime
        # (B, L, P)
        token_indices = tokens.unsqueeze(-1).expand(-1, -1, self.hash_dim)
        positions = torch.arange(self.hash_dim, device=tokens.device).view(1, 1, -1)
        
        # Weighted weights: p * (token_idx + i)
        weights = self.primes.view(1, 1, -1) * (token_indices + positions)
        
        # For a truly "neural" XOR, we can use bitwise operations if on CPU/some GPUs,
        # but for PyTorch compatibility across backends, we might simulate or use 
        # actual bitwise if possible. 
        # torch.bitwise_xor is available.
        
        # We perform cumulative XOR across the prime weights? 
        # The user formula: Hash(t_i) = XOR(p_j * embedding(t_i, j))
        # Here we use token_idx as base for embedding.
        
        # Let's implement the specific logic provided:
        # hash_value ^= weight for weight in prime_weights
        
        res = torch.zeros_like(weights[:, :, 0])
        for i in range(self.hash_dim):
            res = torch.bitwise_xor(res, weights[:, :, i])
            
        return res.unsqueeze(-1).float() # Return as float for projection

    def forward(self, tokens: torch.Tensor) -> torch.Tensor:
        h_hash = self.hash_tokens(tokens)
        # Ensure dtype matches memory_proj weights (important for FP16/BF16)
        h_hash = h_hash.to(self.memory_proj.weight.dtype)
        return self.memory_proj(h_hash)

def hash_text_to_id(text: str, vocab_size: int = 32000) -> int:
    """Deterministic string-to-ID mapping for Engram Project Context."""
    # Use MD5 for a stable hash across runs, then map to vocab
    hash_object = hashlib.md5(text.encode())
    return int(hash_object.hexdigest(), 16) % vocab_size

class LlamaShortConv(nn.Module):
    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        self.tok_embeddings = nn.Embedding(config.vocab_size, config.dim)
        
        if config.use_engram:
            self.engram_memory = NeuralEngramMemory(config)
            self.combine_proj = nn.Linear(config.dim + config.engram_dim, config.dim)
        
        self.layers = nn.ModuleList([
            ShortConvBlock(config.dim) for _ in range(config.n_layers)
        ])
        
        self.norm = nn.RMSNorm(config.dim)
        self.output = nn.Linear(config.dim, config.vocab_size, bias=False)

    def forward(self, tokens):
        _bsz, seqlen = tokens.shape
        h = self.tok_embeddings(tokens)
        
        if self.config.use_engram:
            engram_h = self.engram_memory(tokens)
            h = torch.cat([h, engram_h], dim=-1)
            h = self.combine_proj(h)
        
        for layer in self.layers:
            if self.config.grad_checkpointing and self.training:
                h = checkpoint(layer, h, use_reentrant=False)
            else:
                h = layer(h)
        
        h = self.norm(h)
        logits = self.output(h)
        return logits

# ==========================================
# Training & Inference Scripts
# ==========================================

def run_test():
    """Verifies 8192 context length and memory usage."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🚀 Running ShortConv Test on {device}")
    
    config = ModelConfig(max_seq_len=8192)
    model = LlamaShortConv(config).to(device).to(torch.float16)
    
    # 8192 Sequence
    dummy_input = torch.randint(0, 32000, (1, 8192)).to(device)
    
    start_time = time.time()
    with torch.no_grad():
        logits = model(dummy_input)
    end_time = time.time()
    
    print(f"✅ Forward pass complete: {logits.shape}")
    print(f"⏱️ Time: {end_time - start_time:.4f}s")
    
    if torch.cuda.is_available():
        mem = torch.cuda.max_memory_allocated() / 1e9
        print(f"💾 Peak VRAM: {mem:.2f}GB")

def run_bench():
    """Benchmarking training step with Mixed Precision."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🏁 Benchmarking Training Step...")
    
    config = ModelConfig()
    model = LlamaShortConv(config).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    scaler = torch.amp.GradScaler('cuda') if torch.cuda.is_available() else None
    
    dummy_input = torch.randint(0, 32000, (4, 1024)).to(device)
    target = torch.randint(0, 32000, (4, 1024)).to(device)
    
    model.train()
    
    for i in range(5):
        optimizer.zero_grad()
        
        with torch.amp.autocast('cuda' if torch.cuda.is_available() else 'cpu'):
            logits = model(dummy_input)
            loss = F.cross_entropy(logits.view(-1, 32000), target.view(-1))
        
        if scaler:
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            optimizer.step()
            
        print(f"Step {i+1} Loss: {loss.item():.4f}")

if __name__ == "__main__":
    import sys
    if "--bench" in sys.argv:
        run_bench()
    else:
        run_test()
