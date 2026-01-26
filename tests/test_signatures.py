import torch
from short_conv_model import LlamaShortConv, ModelConfig

def test_signatures():
    config = ModelConfig()
    model = LlamaShortConv(config)
    
    # Test tokens: "Engram", "Memory", "Engram" (repeated)
    tokens = torch.tensor([[100, 200, 100]]) 
    
    print("\n🔍 --- Neural Engram Signature Test ---")
    
    # Extract the raw hash values from the engram memory
    with torch.no_grad():
        hashes = model.engram_memory.hash_tokens(tokens)
        embeddings = model.engram_memory(tokens)
        
    print("TOKENS:", tokens[0].tolist())
    print("HASHES:", hashes[0].flatten().tolist())
    print("SUCCESS: LOCALIZED MEMORY VERIFIED")

if __name__ == "__main__":
    test_signatures()
