#!/usr/bin/env python3
"""
Market Data Fetcher - Engram Neural Core
Fetches real-time price data from Binance API (free, no auth required).

Usage:
    python fetch_data.py --pair BTCUSDT
    python fetch_data.py --pair ETHUSDT --klines 1h --limit 100
"""

import argparse
import json
import sys
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import urllib.request
import urllib.error


@dataclass
class PriceData:
    """Current price data."""
    symbol: str
    price: float
    change_24h: float
    change_percent_24h: float
    high_24h: float
    low_24h: float
    volume_24h: float
    quote_volume_24h: float
    timestamp: int


@dataclass
class KlineData:
    """OHLCV candlestick data."""
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    quote_volume: float


@dataclass
class OrderBookLevel:
    """Order book level."""
    price: float
    quantity: float


@dataclass
class MarketData:
    """Complete market data."""
    symbol: str
    current_price: float
    price_change_24h: float
    price_change_percent_24h: float
    high_24h: float
    low_24h: float
    volume_24h: float
    quote_volume_24h: float
    bid_price: float
    ask_price: float
    spread: float
    spread_percent: float
    klines: List[KlineData]
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    timestamp: int


class BinanceAPI:
    """Binance API client (free, no authentication required)."""
    
    BASE_URL = "https://api.binance.com"
    
    def __init__(self):
        self.timeout = 10
    
    def _request(self, endpoint: str, params: Dict[str, str] = None) -> Any:
        """Make API request."""
        url = f"{self.BASE_URL}{endpoint}"
        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{query}"
        
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "EngramBot/1.0",
                    "Accept": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise Exception(f"Binance API error: {e.code} - {error_body}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def get_ticker_24hr(self, symbol: str) -> PriceData:
        """Get 24hr ticker data for a symbol."""
        data = self._request("/api/v3/ticker/24hr", {"symbol": symbol.upper()})
        
        return PriceData(
            symbol=data['symbol'],
            price=float(data['lastPrice']),
            change_24h=float(data['priceChange']),
            change_percent_24h=float(data['priceChangePercent']),
            high_24h=float(data['highPrice']),
            low_24h=float(data['lowPrice']),
            volume_24h=float(data['volume']),
            quote_volume_24h=float(data['quoteVolume']),
            timestamp=data['closeTime']
        )
    
    def get_klines(self, symbol: str, interval: str = "1h", limit: int = 100) -> List[KlineData]:
        """Get candlestick data."""
        data = self._request("/api/v3/klines", {
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": str(limit)
        })
        
        klines = []
        for k in data:
            klines.append(KlineData(
                timestamp=k[0],
                open=float(k[1]),
                high=float(k[2]),
                low=float(k[3]),
                close=float(k[4]),
                volume=float(k[5]),
                quote_volume=float(k[7])
            ))
        return klines
    
    def get_order_book(self, symbol: str, limit: int = 5) -> Dict[str, List[OrderBookLevel]]:
        """Get order book (bids and asks)."""
        data = self._request("/api/v3/depth", {
            "symbol": symbol.upper(),
            "limit": str(limit)
        })
        
        bids = [OrderBookLevel(price=float(b[0]), quantity=float(b[1])) for b in data['bids']]
        asks = [OrderBookLevel(price=float(a[0]), quantity=float(a[1])) for a in data['asks']]
        
        return {"bids": bids, "asks": asks}
    
    def get_full_market_data(self, symbol: str, interval: str = "1h") -> MarketData:
        """Get complete market data."""
        # Fetch all data in parallel (sequentially here for simplicity)
        ticker = self.get_ticker_24hr(symbol)
        klines = self.get_klines(symbol, interval, limit=50)
        order_book = self.get_order_book(symbol, limit=5)
        
        # Calculate spread
        best_bid = order_book['bids'][0].price if order_book['bids'] else ticker.price
        best_ask = order_book['asks'][0].price if order_book['asks'] else ticker.price
        spread = best_ask - best_bid
        spread_percent = (spread / ticker.price) * 100
        
        return MarketData(
            symbol=symbol,
            current_price=ticker.price,
            price_change_24h=ticker.change_24h,
            price_change_percent_24h=ticker.change_percent_24h,
            high_24h=ticker.high_24h,
            low_24h=ticker.low_24h,
            volume_24h=ticker.volume_24h,
            quote_volume_24h=ticker.quote_volume_24h,
            bid_price=best_bid,
            ask_price=best_ask,
            spread=spread,
            spread_percent=spread_percent,
            klines=klines,
            bids=order_book['bids'],
            asks=order_book['asks'],
            timestamp=ticker.timestamp
        )


def format_output(data: MarketData, format_type: str = "text") -> str:
    """Format market data output."""
    if format_type == "json":
        return json.dumps(asdict(data), indent=2, default=lambda x: asdict(x) if hasattr(x, '__dataclass_fields__') else x)
    
    # Calculate some technical levels from recent klines
    recent_highs = [k.high for k in data.klines[-20:]] if data.klines else [data.high_24h]
    recent_lows = [k.low for k in data.klines[-20:]] if data.klines else [data.low_24h]
    
    swing_high = max(recent_highs)
    swing_low = min(recent_lows)
    
    # Fibonacci levels
    diff = swing_high - swing_low
    fib_382 = swing_high - (diff * 0.382)
    fib_500 = swing_high - (diff * 0.5)
    fib_618 = swing_high - (diff * 0.618)
    
    output = f"""
+==================================================================+
|                 LIVE MARKET DATA - {data.symbol:>12}                    |
+==================================================================+
  Current Price:  ${data.current_price:>15,.2f}
  24h Change:     ${data.price_change_24h:+>15,.2f} ({data.price_change_percent_24h:+.2f}%)
  24h High:       ${data.high_24h:>15,.2f}
  24h Low:        ${data.low_24h:>15,.2f}
  24h Volume:     {data.volume_24h:>15,.4f}
  
  ORDER BOOK:
    Best Bid:     ${data.bid_price:>15,.2f}
    Best Ask:     ${data.ask_price:>15,.2f}
    Spread:       ${data.spread:>15,.2f} ({data.spread_percent:.4f}%)
  
  FIBONACCI LEVELS (Recent Swing):
    0.0%:         ${swing_high:>15,.2f} (High)
    38.2%:        ${fib_382:>15,.2f}
    50.0%:        ${fib_500:>15,.2f}
    61.8%:        ${fib_618:>15,.2f}  *
    100%:         ${swing_low:>15,.2f} (Low)
  
  TECHNICAL OBSERVATIONS:
    - Price is {'above' if data.current_price > fib_500 else 'below'} the 50% Fib level
    - {'Bullish' if data.price_change_percent_24h > 0 else 'Bearish'} momentum (24h: {data.price_change_percent_24h:+.2f}%)
    - Spread is {'tight' if data.spread_percent < 0.1 else 'wide'} ({data.spread_percent:.4f}%)
    
  SUPPORT/RESISTANCE:
    Support 1:    ${data.low_24h:>15,.2f} (24h Low)
    Support 2:    ${fib_618:>15,.2f} (Fib 61.8%)
    Resistance 1: ${data.high_24h:>15,.2f} (24h High)
    Resistance 2: ${fib_382:>15,.2f} (Fib 38.2%)
+==================================================================+
"""
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Fetch real-time market data from Binance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fetch_data.py --pair BTCUSDT
  python fetch_data.py --pair ETHUSDT --interval 4h
  python fetch_data.py --pair SOLUSDT --output json
  
Common pairs: BTCUSDT, ETHUSDT, SOLUSDT, ADAUSDT, DOTUSDT
        """
    )
    
    parser.add_argument(
        "--pair", "-p",
        required=True,
        help="Trading pair (e.g., BTCUSDT, ETHUSDT)"
    )
    parser.add_argument(
        "--interval", "-i",
        default="1h",
        choices=["1m", "5m", "15m", "1h", "4h", "1d", "1w"],
        help="Kline interval (default: 1h)"
    )
    parser.add_argument(
        "--output", "-o",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )
    
    args = parser.parse_args()
    
    # Normalize symbol
    symbol = args.pair.upper()
    if "/" in symbol:
        symbol = symbol.replace("/", "")
    
    print(f"Fetching live data for {symbol} from Binance...")
    
    try:
        api = BinanceAPI()
        data = api.get_full_market_data(symbol, args.interval)
        print(format_output(data, args.output))
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
