import torch
import torch.nn as nn
from engram_neural_integration import create_engram_neural_hash_bridge

def test_shapes():
    bridge = create_engram_neural_hash_bridge()
    layer = bridge.create_enhanced_layer(layer_id=1)
    
    batch_size, seq_len = 1, 8
    hidden_dim = 1024
    hc_mult = 4
    
    hidden_states = torch.randn(batch_size, seq_len, hc_mult, hidden_dim)
    input_ids = torch.randint(1, 500, (batch_size, seq_len))
    
    # Track shapes through Engram
    print("\n--- Shape Tracing ---")
    
    with torch.no_grad():
        original_output = layer.original_engram(hidden_states, input_ids)
        print(f"Original Engram output shape: {original_output.shape}")
        
        target_head = original_output[:, :, 0, :]
        print(f"Target head shape: {target_head.shape}")
        
        # Manually invoke integrate_with_engram
        batch_size, seq_len, hidden_dim = target_head.shape
        print(f"Target hidden_dim: {hidden_dim}")
        
        context_hashes = layer.neural_hasher.get_context_hashes(length=seq_len)
        print(f"Context hashes shape: {context_hashes.shape}")
        
        # Check _hash_to_embedding internal logic
        embed_dim = hidden_dim
        positions = torch.arange(embed_dim, device=layer.neural_hasher.device, dtype=torch.float32)
        print(f"Positions shape: {positions.shape}")
        
        div_term = torch.exp(
            torch.arange(0, embed_dim, 2, device=layer.neural_hasher.device, dtype=torch.float32) * 
            -(3.14159 / embed_dim) # simplified for test
        )
        print(f"Div term shape: {div_term.shape}")
        
        hash_floats = context_hashes.float().unsqueeze(-1)
        print(f"Hash floats shape: {hash_floats.shape}")
        
        embeddings = torch.zeros(seq_len, embed_dim)
        print(f"Embeddings base shape: {embeddings.shape}")
        
        # Check slice shape
        slice_shape = embeddings[:, 0::2].shape
        print(f"Embeddings slice shape: {slice_shape}")
        
        sin_part = torch.sin(hash_floats * div_term)
        print(f"Sin part shape: {sin_part.shape}")
        
        # Addition check
        try:
            enhanced = target_head + sin_part.unsqueeze(0)
            print("Target head + sin_part successful")
        except Exception as e:
            print(f"Target head + sin_part FAILED: {e}")

if __name__ == "__main__":
    test_shapes()
