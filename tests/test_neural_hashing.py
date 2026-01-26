#!/usr/bin/env python3
"""
================================================================================
[Engram Neural Hashing Test Suite]

Comprehensive test suite for the neural hashing integration with Engram.
Demonstrates the enhanced context retention and performance improvements.
================================================================================
"""

import torch
import sys
import os
from typing import List, Dict

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from neural_hashing import create_neural_hash_module, TokenType
from engram_neural_integration import create_engram_neural_hash_bridge, EnhancedEngramConfig
from engram_demo_v1 import EngramConfig

def test_neural_hashing_standalone():
    """Test the neural hashing module independently."""
    print("🧪 Testing Neural Hashing Module...")
    
    # Create module
    neural_hash = create_neural_hash_module(
        primes=[2, 3, 5, 7, 11, 13],
        max_context=1024
    )
    
    # Test tokens
    test_tokens = ["engram", "neural", "hashing", "context", "memory", "local", "first"]
    
    # Hash sequence
    hashes = neural_hash.hash_sequence(test_tokens)
    print(f"  Token hashes: {dict(zip(test_tokens, hashes))}")
    
    # Update context
    neural_hash.update_context(test_tokens)
    
    # Get statistics
    stats = neural_hash.get_hash_statistics()
    print(f"  Hash statistics: {stats}")
    
    # Test context retrieval
    context = neural_hash.get_context_hashes(length=len(test_tokens))
    print(f"  Context hashes: {context.tolist()}")
    
    print("✅ Neural Hashing Module Test Complete!")
    return True

def test_engram_integration():
    """Test the integration with existing Engram architecture."""
    print("\n🧪 Testing Engram Integration...")
    
    # Create bridge
    bridge = create_engram_neural_hash_bridge(
        primes=[2, 3, 5, 7, 11, 13, 17],
        max_context=2048,
        integration_weight=0.15
    )
    
    # Create enhanced layer
    enhanced_layer = bridge.create_enhanced_layer(layer_id=1)
    
    # Test data
    batch_size, seq_len = 1, 8
    hidden_dim = 1024
    hc_mult = 4
    
    # Create dummy inputs
    hidden_states = torch.randn(batch_size, seq_len, hc_mult, hidden_dim)
    input_ids = torch.randint(1, 500, (batch_size, seq_len))
    
    print(f"  Input shapes: hidden_states={hidden_states.shape}, input_ids={input_ids.shape}")
    
    # Forward pass
    with torch.no_grad():
        try:
            output = enhanced_layer(hidden_states, input_ids)
            print(f"  Output shape: {output.shape}")
            print("  ✅ Forward pass successful")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"  ❌ Forward pass failed: {e}")
            return False
    
    # Get statistics
    stats = enhanced_layer.get_hash_statistics()
    print(f"  Hash statistics: {stats}")
    
    print("✅ Engram Integration Test Complete!")
    return True

def test_context_retention():
    """Test context retention capabilities."""
    print("\n🧪 Testing Context Retention...")
    
    # Create neural hash module
    neural_hash = create_neural_hash_module(max_context=100)
    
    # Test sequences
    sequences = [
        ["engram", "neural", "context"],
        ["local", "first", "architecture"],
        ["hashing", "memory", "retention"],
        ["efficient", "computing", "system"]
    ]
    
    print("  Processing sequences...")
    for i, seq in enumerate(sequences):
        neural_hash.update_context(seq)
        context = neural_hash.get_context_hashes(length=len(seq))
        print(f"    Seq {i+1}: {seq} -> {context.tolist()}")
    
    # Test long sequence handling
    long_sequence = ["token"] * 50
    neural_hash.update_context(long_sequence)
    
    stats = neural_hash.get_hash_statistics()
    print(f"  Final statistics: {stats}")
    
    print("✅ Context Retention Test Complete!")
    return True

def test_performance_metrics():
    """Test performance and efficiency metrics."""
    print("\n🧪 Testing Performance Metrics...")
    
    # Create module
    neural_hash = create_neural_hash_module(max_context=8192)
    
    # Performance test
    import time
    
    test_tokens = ["engram", "neural", "hashing"] * 1000  # 3000 tokens
    start_time = time.time()
    
    # Hash all tokens
    hashes = neural_hash.hash_sequence(test_tokens)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"  Processed {len(test_tokens)} tokens in {processing_time:.4f}s")
    print(f"  Tokens/second: {len(test_tokens)/processing_time:.0f}")
    
    # Memory usage
    context_memory_usage = torch.count_nonzero(neural_hash.context_memory).item()
    total_memory = len(neural_hash.context_memory)
    memory_efficiency = context_memory_usage / total_memory
    
    print(f"  Memory efficiency: {memory_efficiency:.2%}")
    
    # Collision rate
    stats = neural_hash.get_hash_statistics()
    collision_rate = stats["collision_rate"]
    print(f"  Hash collision rate: {collision_rate:.2%}")
    
    print("✅ Performance Metrics Test Complete!")
    print("✅ Performance Metrics Test Complete!")
    return True

def test_financial_hashing():
    """Test financial token classification and hashing."""
    print("\n🧪 Testing Financial Hashing...")
    
    # Create module
    neural_hash = create_neural_hash_module(
        primes=[2, 3, 5],
        max_context=1024
    )
    
    # Test specific financial keywords
    financial_tokens = ["bull", "bear", "$AAPL", "$btc", "dividend"]
    general_tokens = ["hello", "world", "engram", "python"]
    
    print("  Testing classification...")
    for token in financial_tokens:
        cls = neural_hash.classify_token(token)
        print(f"    '{token}' -> {cls}")
        if cls != TokenType.FINANCIAL_ENTITY:
            print(f"    ❌ Expected FINANCIAL_ENTITY for '{token}', got {cls}")
            return False
            
    for token in general_tokens:
        cls = neural_hash.classify_token(token)
        print(f"    '{token}' -> {cls}")
        if cls != TokenType.GENERAL:
            print(f"    ❌ Expected GENERAL for '{token}', got {cls}")
            return False
            
    # Test hashing difference
    # "bull" is financial, ensure it produces consistent hash
    hash1 = neural_hash.hash_token("bull")
    hash2 = neural_hash.hash_token("bull")
    
    if hash1 != hash2:
        print("    ❌ Hashing is not deterministic")
        return False
        
    print(f"    'bull' hash: {hash1}")
    
    # Check stats
    stats = neural_hash.get_hash_statistics()
    print(f"  Stats: {stats}")
    if stats["financial_hashes"] == 0:
        print("    ❌ Financial hashes count is 0")
        # Note: hash_token updates stats, so this should be > 0
        return False
        
    print("✅ Financial Hashing Test Complete!")
    return True

def run_comprehensive_test():
    """Run all tests and provide summary."""
    print("🚀 Starting Comprehensive Engram Neural Hash Test Suite...")
    print("=" * 60)
    
    tests = [
        ("Neural Hashing Standalone", test_neural_hashing_standalone),
        ("Engram Integration", test_engram_integration),
        ("Context Retention", test_context_retention),
        ("Context Retention", test_context_retention),
        ("Performance Metrics", test_performance_metrics),
        ("Financial Hashing", test_financial_hashing)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Engram Neural Hashing is ready for deployment.")
    else:
        print("⚠️  Some tests failed. Review the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)