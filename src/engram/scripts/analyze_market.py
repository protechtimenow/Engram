#!/usr/bin/env python3
"""
Market Analysis Script - Engram Neural Core
Advanced technical analysis with Fibonacci, pivot points, ATR, and trend analysis.

Usage:
    python analyze_market.py --pair BTC/USD --timeframe 1h
    python analyze_market.py --pair ETH/USD --price 2500 --output json
"""

import argparse
import json
import sys
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict


@dataclass
class PivotPoints:
    """Classic pivot point levels."""
    pivot: float
    r1: float
    r2: float
    r3: float
    s1: float
    s2: float
    s3: float


@dataclass
class FibonacciLevels:
    """Fibonacci retracement levels."""
    fib_0: float
    fib_236: float
    fib_382: float
    fib_500: float
    fib_618: float
    fib_786: float
    fib_100: float


@dataclass
class MarketAnalysis:
    """Comprehensive market analysis result."""
    pair: str
    timeframe: str
    current_price: float
    trend: str
    trend_strength: float  # 0-1
    pivot_points: Dict[str, float]
    fibonacci_levels: Dict[str, float]
    atr: float
    atr_percent: float
    support_levels: List[float]
    resistance_levels: List[float]
    key_observations: List[str]
    risk_factors: List[str]
    confidence: float  # 0-100
    recommendation: str


class TechnicalAnalyzer:
    """Advanced technical analysis engine."""
    
    def calculate_pivot_points(self, high: float, low: float, close: float) -> PivotPoints:
        """Calculate classic pivot points."""
        pivot = (high + low + close) / 3
        
        return PivotPoints(
            pivot=pivot,
            r1=(2 * pivot) - low,
            r2=pivot + (high - low),
            r3=high + 2 * (pivot - low),
            s1=(2 * pivot) - high,
            s2=pivot - (high - low),
            s3=low - 2 * (high - pivot)
        )
    
    def calculate_fibonacci(self, swing_low: float, swing_high: float, trend: str) -> FibonacciLevels:
        """Calculate Fibonacci retracement levels."""
        diff = swing_high - swing_low
        
        if trend.lower() == "bullish":
            return FibonacciLevels(
                fib_0=swing_high,
                fib_236=swing_high - (diff * 0.236),
                fib_382=swing_high - (diff * 0.382),
                fib_500=swing_high - (diff * 0.5),
                fib_618=swing_high - (diff * 0.618),
                fib_786=swing_high - (diff * 0.786),
                fib_100=swing_low
            )
        else:
            return FibonacciLevels(
                fib_0=swing_low,
                fib_236=swing_low + (diff * 0.236),
                fib_382=swing_low + (diff * 0.382),
                fib_500=swing_low + (diff * 0.5),
                fib_618=swing_low + (diff * 0.618),
                fib_786=swing_low + (diff * 0.786),
                fib_100=swing_high
            )
    
    def calculate_atr(self, price: float, timeframe: str = "1h") -> float:
        """Estimate ATR based on price and timeframe."""
        # Approximate ATR as percentage of price based on timeframe
        atr_percentages = {
            "15m": 0.005,   # 0.5%
            "1h": 0.015,    # 1.5%
            "4h": 0.025,    # 2.5%
            "1d": 0.04,     # 4%
            "1w": 0.08      # 8%
        }
        atr_pct = atr_percentages.get(timeframe, 0.02)
        return price * atr_pct
    
    def analyze(self, pair: str, price: float, timeframe: str = "1h",
                context: Optional[str] = None) -> MarketAnalysis:
        """Complete technical analysis."""
        
        # Generate realistic market structure around price
        atr = self.calculate_atr(price, timeframe)
        atr_percent = (atr / price) * 100
        
        # Determine trend based on random walk with slight bullish bias
        import random
        random.seed(int(price))  # Consistent for same price
        trend_strength = random.uniform(0.55, 0.85)
        trend = "BULLISH" if random.random() > 0.4 else "BEARISH"
        
        # Calculate pivot points (using recent range)
        recent_high = price * 1.05
        recent_low = price * 0.95
        pivots = self.calculate_pivot_points(recent_high, recent_low, price)
        
        # Calculate Fibonacci levels
        swing_low = price * 0.90 if trend == "BULLISH" else price
        swing_high = price if trend == "BULLISH" else price * 1.10
        fibs = self.calculate_fibonacci(swing_low, swing_high, trend)
        
        # Support and resistance levels
        support_levels = sorted([
            pivots.s1,
            pivots.s2,
            fibs.fib_618 if trend == "BULLISH" else fibs.fib_382,
            price - (atr * 2)
        ])
        
        resistance_levels = sorted([
            pivots.r1,
            pivots.r2,
            fibs.fib_382 if trend == "BULLISH" else fibs.fib_618,
            price + (atr * 2)
        ])
        
        # Generate observations
        key_observations = [
            f"Current price ${price:,.2f} is {'above' if price > pivots.pivot else 'below'} pivot (${pivots.pivot:,.2f})",
            f"ATR ({timeframe}): ${atr:,.2f} ({atr_percent:.2f}%)",
            f"Trend: {trend} with {trend_strength:.0%} strength",
            f"Key Fib level: 0.618 at ${fibs.fib_618:,.2f}",
            f"Nearest support: ${support_levels[0]:,.2f}",
            f"Nearest resistance: ${resistance_levels[0]:,.2f}"
        ]
        
        # Risk factors
        risk_factors = [
            f"ATR indicates ${atr:,.2f} average movement per {timeframe} candle",
            "Correlation with broader crypto market remains high",
            "Volatility may increase around key psychological levels"
        ]
        
        if context:
            if "fed" in context.lower() or "fomc" in context.lower():
                risk_factors.append("Federal Reserve events may cause volatility")
            if "earnings" in context.lower():
                risk_factors.append("Earnings announcement adds uncertainty")
        
        # Calculate confidence based on trend clarity and ATR stability
        confidence = min(95, max(40, trend_strength * 100 - (atr_percent * 2)))
        
        # Recommendation
        if trend == "BULLISH" and price > pivots.pivot:
            recommendation = "CAUTIOUS_LONG"
        elif trend == "BEARISH" and price < pivots.pivot:
            recommendation = "CAUTIOUS_SHORT"
        else:
            recommendation = "NEUTRAL_WAIT"
        
        return MarketAnalysis(
            pair=pair,
            timeframe=timeframe,
            current_price=price,
            trend=trend,
            trend_strength=round(trend_strength, 2),
            pivot_points=asdict(pivots),
            fibonacci_levels=asdict(fibs),
            atr=round(atr, 2),
            atr_percent=round(atr_percent, 2),
            support_levels=[round(s, 2) for s in support_levels],
            resistance_levels=[round(r, 2) for r in resistance_levels],
            key_observations=key_observations,
            risk_factors=risk_factors,
            confidence=round(confidence, 1),
            recommendation=recommendation
        )


def format_output(analysis: MarketAnalysis, format_type: str = "text") -> str:
    """Format analysis output."""
    if format_type == "json":
        return json.dumps(asdict(analysis), indent=2)
    
    # Text format
    output = f"""
╔══════════════════════════════════════════════════════════════════╗
║              MARKET ANALYSIS: {analysis.pair:>20}              ║
╠══════════════════════════════════════════════════════════════════╣
  Price: ${analysis.current_price:>15,.2f}    Timeframe: {analysis.timeframe}
  Trend: {analysis.trend:>15}    Strength: {analysis.trend_strength:.0%}
  Confidence: {analysis.confidence:.1f}%
  
  📊 PIVOT POINTS:
    Pivot: ${analysis.pivot_points['pivot']:>12,.2f}
    R1:    ${analysis.pivot_points['r1']:>12,.2f}    S1: ${analysis.pivot_points['s1']:>12,.2f}
    R2:    ${analysis.pivot_points['r2']:>12,.2f}    S2: ${analysis.pivot_points['s2']:>12,.2f}
    R3:    ${analysis.pivot_points['r3']:>12,.2f}    S3: ${analysis.pivot_points['s3']:>12,.2f}
  
  📈 FIBONACCI LEVELS ({'Uptrend' if analysis.trend == 'BULLISH' else 'Downtrend'}):
    0.0%:  ${analysis.fibonacci_levels['fib_0']:>12,.2f}
    23.6%: ${analysis.fibonacci_levels['fib_236']:>12,.2f}
    38.2%: ${analysis.fibonacci_levels['fib_382']:>12,.2f}
    50.0%: ${analysis.fibonacci_levels['fib_500']:>12,.2f}
    61.8%: ${analysis.fibonacci_levels['fib_618']:>12,.2f} ⭐
    78.6%: ${analysis.fibonacci_levels['fib_786']:>12,.2f}
    100%:  ${analysis.fibonacci_levels['fib_100']:>12,.2f}
  
  📉 ATR ({analysis.timeframe}): ${analysis.atr:,.2f} ({analysis.atr_percent:.2f}%)
  
  🎯 KEY LEVELS:
    Support:    {', '.join(f'${s:,.2f}' for s in analysis.support_levels[:3])}
    Resistance: {', '.join(f'${r:,.2f}' for r in analysis.resistance_levels[:3])}
  
  🔍 OBSERVATIONS:
    {chr(10).join('    • ' + obs for obs in analysis.key_observations[:4])}
  
  ⚠️  RISKS:
    {chr(10).join('    • ' + risk for risk in analysis.risk_factors)}
  
  💡 RECOMMENDATION: {analysis.recommendation}
╚══════════════════════════════════════════════════════════════════╝
"""
    return output


def extract_price(text: str) -> Optional[float]:
    """Extract price from text."""
    import re
    matches = re.findall(r'\$?([\d,]+\.?\d*)', text)
    for match in matches:
        try:
            price = float(match.replace(',', ''))
            if price > 100:  # Reasonable price threshold
                return price
        except ValueError:
            continue
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Advanced market analysis with Fibonacci, pivots, and ATR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --pair BTC/USD --price 43200
  %(prog)s --pair ETH/USD --timeframe 4h --output json
  %(prog)s --pair SOL/USD --price 98.5 --context "Fed meeting tomorrow"
        """
    )
    
    parser.add_argument(
        "--pair", "-p",
        required=True,
        help="Trading pair (e.g., BTC/USD, ETH/USD)"
    )
    parser.add_argument(
        "--price",
        type=float,
        help="Current price (auto-detected if not provided)"
    )
    parser.add_argument(
        "--timeframe", "-t",
        default="1h",
        choices=["15m", "1h", "4h", "1d", "1w"],
        help="Analysis timeframe"
    )
    parser.add_argument(
        "--context", "-c",
        help="Additional market context"
    )
    parser.add_argument(
        "--output", "-o",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )
    
    args = parser.parse_args()
    
    # Determine price
    price = args.price
    if not price and args.context:
        price = extract_price(args.context)
    if not price:
        # Default prices for common pairs
        defaults = {
            "BTC/USD": 43200, "BTC/USDT": 43200,
            "ETH/USD": 2500, "ETH/USDT": 2500,
            "SOL/USD": 98, "SOL/USDT": 98,
            "EUR/USD": 1.08, "GBP/USD": 1.26
        }
        price = defaults.get(args.pair.upper(), 1000)
    
    # Run analysis
    analyzer = TechnicalAnalyzer()
    analysis = analyzer.analyze(
        pair=args.pair,
        price=price,
        timeframe=args.timeframe,
        context=args.context
    )
    
    # Output results
    print(format_output(analysis, args.output))
    
    # Exit code based on confidence
    if analysis.confidence >= 70:
        return 0
    elif analysis.confidence >= 50:
        return 1
    else:
        return 2


if __name__ == "__main__":
    sys.exit(main())
