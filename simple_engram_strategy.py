from freqtrade.strategy import IStrategy
import pandas as pd
import numpy as np
from typing import Dict, List

class EngramStrategy(IStrategy):
    """
    Simple Engram Strategy for FreqTrade Integration
    ================================================
    
    This is a basic strategy that will be enhanced with Engram AI signals.
    For now, it uses simple technical indicators as a foundation.
    """
    
    # Strategy interface version
    INTERFACE_VERSION = 3
    
    # Minimal ROI (Return on Investment) designed for the strategy
    minimal_roi = {
        "0": 0.10  # 10% profit target
    }
    
    # Stoploss
    stoploss = -0.10  # 10% stop loss
    
    # Timeframe
    timeframe = '5m'
    
    # Optional: exit signals
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_exit_signal = False
    
    # Optional: startup_candle_count
    startup_candle_count: int = 30
    
    # Hyperoptable parameters
    buy_rsi = int(30)
    sell_rsi = int(70)
    
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """
        Adds several indicators to the given DataFrame.
        
        :param dataframe: DataFrame with OHLCV data
        :param metadata: Additional information, like the traded pair
        :return: DataFrame with indicators added
        """
        
        # RSI
        dataframe['rsi'] = 100 - (100 / (1 + dataframe['close'].diff(1).rolling(window=14).apply(
            lambda x: x[x > 0].mean() / -x[x < 0].mean() if len(x[x < 0]) > 0 else np.nan
        )))
        
        # Simple Moving Averages
        dataframe['sma_fast'] = dataframe['close'].rolling(window=10).mean()
        dataframe['sma_slow'] = dataframe['close'].rolling(window=30).mean()
        
        # Bollinger Bands
        bb_period = 20
        bb_std = 2
        dataframe['bb_middle'] = dataframe['close'].rolling(window=bb_period).mean()
        bb_std_dev = dataframe['close'].rolling(window=bb_period).std()
        dataframe['bb_upper'] = dataframe['bb_middle'] + (bb_std_dev * bb_std)
        dataframe['bb_lower'] = dataframe['bb_middle'] - (bb_std_dev * bb_std)
        
        return dataframe

    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """
        Based on TA indicators, populates the entry signal for the given dataframe
        :param dataframe: DataFrame with OHLCV data and indicators
        :param metadata: Additional information, like the traded pair
        :return: DataFrame with entry columns populated
        """
        
        # Buy signals (entry conditions)
        dataframe.loc[
            (
                (dataframe['rsi'] < self.buy_rsi) &  # Oversold
                (dataframe['close'] < dataframe['bb_lower']) &  # Price below lower Bollinger Band
                (dataframe['sma_fast'] < dataframe['sma_slow'])  # Fast SMA below slow SMA
            ),
            'enter_long'
        ] = 1
        
        return dataframe

    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """
        Based on TA indicators, populates the exit signal for the given dataframe
        :param dataframe: DataFrame with OHLCV data and indicators
        :param metadata: Additional information, like the traded pair
        :return: DataFrame with exit columns populated
        """
        
        # Sell signals (exit conditions)
        dataframe.loc[
            (
                (dataframe['rsi'] > self.sell_rsi) &  # Overbought
                (dataframe['close'] > dataframe['bb_upper'])  # Price above upper Bollinger Band
            ),
            'exit_long'
        ] = 1
        
        return dataframe
    
    def custom_stake_amount(self, pair: str, current_time: str, current_rate: float,
                          proposed_stake: float, min_stake: Optional[float], max_stake: float,
                          leverage: float, entry_tag: Optional[str], side: str,
                          **kwargs) -> float:
        """
        Custom stake amount calculation.
        For now, returns the proposed stake (can be enhanced with Engram risk management).
        """
        return proposed_stake
    
    def confirm_trade_entry(self, pair: str, order_type: str, amount: float,
                           rate: float, time_in_force: str, current_time: str,
                           entry_tag: Optional[str], side: str, **kwargs) -> bool:
        """
        Confirm trade entry.
        This can be enhanced with Engram AI confirmation.
        """
        return True
    
    def leverage(self, pair: str, current_time: str, current_rate: float,
                proposed_leverage: float, max_leverage: float, entry_tag: Optional[str],
                side: str, **kwargs) -> float:
        """
        Custom leverage calculation.
        Returns 1 (no leverage) for spot trading.
        """
        return 1.0