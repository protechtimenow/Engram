#!/usr/bin/env python3
"""
R Model Runner for Engram
Executes R trading models and feeds output to A2A system
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from datetime import datetime

R_SCRIPT_PATH = Path(__file__).parent / "trading_signal_generator.R"
SIGNALS_DIR = Path(__file__).parent / "signals"

def run_r_model(symbol: str = "BTCUSDT") -> dict:
    """Run R tidymodels and get trading signal"""
    
    print(f"🔄 Running R model for {symbol}...")
    
    try:
        # Run R script
        result = subprocess.run(
            ["Rscript", str(R_SCRIPT_PATH), symbol],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            cwd=str(R_SCRIPT_PATH.parent)
        )
        
        if result.returncode != 0:
            print(f"❌ R script error: {result.stderr}")
            return None
        
        print(result.stdout)
        
        # Read output JSON
        signal_file = SIGNALS_DIR / f"{symbol}_signal.json"
        if signal_file.exists():
            with open(signal_file, 'r') as f:
                signal_data = json.load(f)
            return signal_data
        else:
            print(f"❌ Signal file not found: {signal_file}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ R script timeout")
        return None
    except Exception as e:
        print(f"❌ Error running R model: {e}")
        return None

def format_for_a2a(signal_data: dict) -> str:
    """Format signal for A2A debate"""
    
    if not signal_data:
        return "No signal generated"
    
    return f"""
ML MODEL SIGNAL (tidymodels Random Forest):

Asset: {signal_data['symbol']} @ ${signal_data['current_price']}
Signal: {signal_data['signal']} (confidence: {signal_data['confidence']}%)

Probabilities:
- BUY: {signal_data['probabilities']['buy']*100:.1f}%
- SELL: {signal_data['probabilities']['sell']*100:.1f}%
- HOLD: {signal_data['probabilities']['hold']*100:.1f}%

Technical Features:
- Price/SMA7 Ratio: {signal_data['features']['sma7_ratio']:.4f}
- 7-Day Momentum: {signal_data['features']['momentum_7']*100:.2f}%
- Volatility: {signal_data['features']['volatility']:.4f}

Recommendation: {signal_data['recommendation']}
"""

def main():
    """Main entry point"""
    symbol = sys.argv[1] if len(sys.argv) > 1 else "BTCUSDT"
    
    print("=" * 60)
    print("🧠 R ML MODEL - ENGRAM INTEGRATION")
    print("=" * 60)
    
    # Ensure directories exist
    SIGNALS_DIR.mkdir(exist_ok=True)
    
    # Run model
    signal = run_r_model(symbol)
    
    if signal:
        formatted = format_for_a2a(signal)
        print("\n" + "=" * 60)
        print("📤 OUTPUT FOR A2A DEBATE:")
        print("=" * 60)
        print(formatted)
        
        # Save formatted output
        output_file = SIGNALS_DIR / f"{symbol}_a2a_input.txt"
        with open(output_file, 'w') as f:
            f.write(formatted)
        print(f"\n💾 A2A input saved to: {output_file}")
        
        return 0
    else:
        print("❌ Failed to generate signal")
        return 1

if __name__ == "__main__":
    sys.exit(main())
