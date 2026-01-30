#!/usr/bin/env python3
"""
Quick test for financial neural capacity integration.
"""
import requests
import json
import time

def test_financial_endpoints():
    """Test all financial API endpoints."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Financial Neural Capacity Endpoints")
    print("="*50)
    
    # Test sentiment endpoint
    print("\n📊 Testing sentiment endpoint...")
    try:
        response = requests.get(f"{base_url}/api/engram/financial/sentiment", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Sentiment: {data['market_sentiment']:.3f} ({data['market_direction']})")
        else:
            print(f"   ❌ Sentiment endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Sentiment endpoint error: {str(e)}")
    
    # Test trends endpoint
    print("\n📈 Testing trends endpoint...")
    try:
        response = requests.get(f"{base_url}/api/engram/financial/trends", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Trend: {data['current_trend']} (strength: {data['trend_strength']:.3f})")
        else:
            print(f"   ❌ Trends endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Trends endpoint error: {str(e)}")
    
    # Test comprehensive analysis
    print("\n🎯 Testing comprehensive analysis...")
    try:
        response = requests.get(f"{base_url}/api/engram/financial/analysis", timeout=10)
        if response.status_code == 200:
            data = response.json()
            health = data['executive_summary']['overall_health']
            print(f"   ✅ Overall Health: {health}")
        else:
            print(f"   ❌ Analysis endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Analysis endpoint error: {str(e)}")
    
    # Test health endpoint
    print("\n🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health/financial", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ System Status: {data['status']}")
        else:
            print(f"   ❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health endpoint error: {str(e)}")
    
    print("\n🎉 Financial Neural Capacity Integration Test Complete!")

if __name__ == "__main__":
    test_financial_endpoints()
