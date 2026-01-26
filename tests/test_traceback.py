import torch
import traceback
from engram_neural_integration import create_engram_neural_hash_bridge

def test_traceback():
    try:
        bridge = create_engram_neural_hash_bridge()
        enhanced_layer = bridge.create_enhanced_layer(layer_id=1)
        
        print("\n--- Model Norm Inspection ---")
        for name, m in enhanced_layer.named_modules():
            if "RMSNorm" in str(type(m)):
                print(f"Norm: {name}, Weight Shape: {m.weight.shape}")

        batch_size, seq_len = 1, 8
        hidden_dim = 1024
        hc_mult = 4
        
        hidden_states = torch.randn(batch_size, seq_len, hc_mult, hidden_dim)
        input_ids = torch.randint(1, 500, (batch_size, seq_len))
        
        print("Starting forward pass...")
        with torch.no_grad():
            output = enhanced_layer(hidden_states, input_ids)
        print("Forward pass successful!")
        
    except Exception:
        print("\n--- ERROR DETECTED ---")
        traceback.print_exc()

if __name__ == "__main__":
    test_traceback()
