#!/usr/bin/env python3

"""
Test script for local Engram model.
"""

import sys
import os
sys.path.append('src')

try:
    from core.engram_demo_v1 import EngramModel
    print("✅ Engram model imported successfully")

    # Test initialization
    model = EngramModel(use_clawdbot=False)
    print("✅ Engram model initialized successfully")

    # Test forward pass
    import torch
    input_ids = torch.randint(0, 1000, (1, 10))  # Dummy input
    output = model(input_ids)
    print(f"✅ Forward pass successful, output shape: {output.shape}")

    print("🎉 Local Engram model is working!")
    sys.exit(0)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
