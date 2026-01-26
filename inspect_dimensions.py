import torch
import torch.nn as nn
from engram_neural_integration import create_engram_neural_hash_bridge
from engram_demo_v1 import backbone_config

def inspect_model():
    print(f"Backbone hidden_size: {backbone_config.hidden_size}")
    bridge = create_engram_neural_hash_bridge()
    layer = bridge.create_enhanced_layer(layer_id=1)
    
    print("\n--- Inspecting EnhancedEngram Layer 1 ---")
    for name, module in layer.named_modules():
        if isinstance(module, nn.RMSNorm):
            print(f"Layer: {name}, Weight Shape: {module.weight.shape}")

if __name__ == "__main__":
    inspect_model()
