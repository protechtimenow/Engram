"""
Engram Bridge Skill for ClawdBot
Integrates Freqtrade bridges with Neural Core
"""

import sys
from pathlib import Path

# Add freqtrade bridges to path
bridges_path = Path(__file__).parent.parent.parent / "freqtrade" / "bridges"
if str(bridges_path) not in sys.path:
    sys.path.insert(0, str(bridges_path))

# Import from master bridge implementations
from neural_bridge_adapter import (
    NeuralBridgeAdapter,
    EngramBridgeSkill,
    NeuralSignal
)
from barchart_bridge import BarChartBridge, TickData
from tradovate_bridge import TradovateBridge, Order, OrderSide, OrderType
from csv_export_bridge import CSVExportBridge, TradeRecord

__all__ = [
    'NeuralBridgeAdapter',
    'EngramBridgeSkill', 
    'NeuralSignal',
    'BarChartBridge',
    'TickData',
    'TradovateBridge',
    'Order',
    'OrderSide',
    'OrderType',
    'CSVExportBridge',
    'TradeRecord'
]

# Skill entry point for ClawdBot
def create_skill():
    """Factory function for ClawdBot skill system"""
    return EngramBridgeSkill()
