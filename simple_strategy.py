from freqtrade.strategy import IStrategy
import pandas as pd
import numpy as np

class SimpleEngramStrategy(IStrategy):
    """
    Simple Engram-Compatible Strategy
    ================================
    
    Basic technical analysis strategy that serves as a foundation
    for Engram AI integration. Works without heavy dependencies.
    """
    
    INTERFACE_VERSION = 3
    
    # Minimal ROI designed for quick testing
    minimal_roi = {
        "0": 0.05  # 5% profit target
    }
    
    # Stoploss
    stoploss = -0.05  # 5% stop loss
    
    # Timeframe
    timeframe = '5m'
    
    # Trailing stop
    trailing_stop = False
    trailing_stop_positive = None
    trailing_stop_positive_offset = 0.0
    trailing_only_offset_is_reached = False
    
    # Optional: startup_candle_count
    startup_candle_count: int = 20
    
    # Hyperoptable parameters
    buy_rsi = int(35)
    sell_rsi = int(65)
    
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """
        Adds several indicators to the given DataFrame.
        """
        
        # Simple RSI calculation
        delta = dataframe['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        dataframe['rsi'] = 100 - (100 / (1 + rs))
        
        # Simple Moving Averages
        dataframe['sma_short'] = dataframe['close'].rolling(window=10).mean()
        dataframe['sma_long'] = dataframe['close'].rolling(window=20).mean()
        
        # Price momentum
        dataframe['momentum'] = dataframe['close'].pct_change(periods=5)
        
        return dataframe

    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """
        Based on TA indicators, populates the entry signal.
        """
        
        # Buy signal conditions
        dataframe.loc[
            (
                (dataframe['rsi'] < self.buy_rsi) &  # Oversold
                (dataframe['close'] < dataframe['sma_long']) &  # Below long SMA
                (dataframe['sma_short'] < dataframe['sma_long']) &  # Bear trend
                (dataframe['volume'] > 0)  # Volume check
            ),
            'enter_long'
        ] = 1
        
        return dataframe

    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """
        Based on TA indicators, populates the exit signal.
        """
        
        # Sell signal conditions  
        dataframe.loc[
            (
                (dataframe['rsi'] > self.sell_rsi) &  # Overbought
                (dataframe['close'] > dataframe['sma_short'])  # Above short SMA
            ),
            'exit_long'
        ] = 1
        
        return dataframe