# test_backtester.py

import logging
import os
import sys
app_path = os.path.join(os.path.expanduser('~/sandbox/doberman'))
sys.path.append(app_path)
from doberman import Stock
from doberman import BackTester
from doberman import StrategyFactory

logger = logging.getLogger()

symbol = 'fake'
date_start = '2024-03-01'
date_end = '2024-03-30'

CONFIG = os.path.expanduser('~/sandbox/doberman/test-config.toml')
stock = Stock(symbol, date_start, date_end, config=CONFIG)
stock.load_data()
sim = StrategyFactory(stock, 'ema')
bt = BackTester(stock)
bt.backtest('ema')

def test_backtest_trade_log():
    """
    Check if expected trades have been entered into log.
    """

    trade1 = tuple(bt.stock_obj.trade_log.loc['2024-03-01'])
    trade2 = tuple(bt.stock_obj.trade_log.loc['2024-03-20'])

    assert (trade1, trade2) == ((96.0, 'buy', -9907.2), (-96.0, 'sell', 13622.4))


def test_backtest_results():

    shares = stock.shares_held()
    cash = f"{stock.cash_position():0.2f}"
    position_value = f"{stock.position_value():0.2f}"

    assert (shares, cash, position_value) == (0.0, "3715.20", "3715.20")