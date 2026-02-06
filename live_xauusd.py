#!/usr/bin/env python3
"""Live XAUUSD Price Fetcher"""

import yfinance as yf
import datetime

def get_live_xauusd():
    """Get live XAUUSD data from Yahoo Finance"""
    try:
        # XAUUSD via Gold Futures (GC=F)
        ticker = yf.Ticker('GC=F')
        
        hist = ticker.history(period='1d', interval='1m')
        
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            open_price = hist['Open'].iloc[0]
            high = hist['High'].max()
            low = hist['Low'].min()
            
            # Get current UTC time
            now = datetime.datetime.now(datetime.timezone.utc)
            
            return {
                'symbol': 'XAUUSD (GC=F)',
                'timestamp': now.strftime('%Y-%m-%d %H:%M:%S GMT'),
                'current': current_price,
                'open': open_price,
                'high': high,
                'low': low,
                'success': True
            }
        else:
            return {'success': False, 'error': 'No data available'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    data = get_live_xauusd()
    
    if data['success']:
        print(f"[{data['symbol']}] {data['timestamp']}")
        print(f"Current: ${data['current']:.2f}")
        print(f"Open: ${data['open']:.2f}")
        print(f"High: ${data['high']:.2f}")
        print(f"Low: ${data['low']:.2f}")
    else:
        print(f"Error: {data.get('error', 'Unknown error')}")
