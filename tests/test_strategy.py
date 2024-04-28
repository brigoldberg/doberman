# test_strategy.py

import logging
import os
import sys
from pytest import approx
app_path = os.path.join(os.path.expanduser('~/sandbox/doberman'))
sys.path.append(app_path)
from doberman import Stock
from doberman import StrategyFactory

logger = logging.getLogger()

symbol = 'fake'
date_start = '2024-03-01'
date_end = '2024-03-30'

CONFIG = os.path.expanduser('~/sandbox/doberman/test-config.toml')
stock = Stock(symbol, date_start, date_end, config=CONFIG)
stock.load_data()
sim = StrategyFactory(stock, 'ema')


def test_ema(trade_date='2024-03-22'):
    """
    Validate ema from strategy dataframe.
    """
    ema = sim.stock_obj.signal['ema'].loc[trade_date].ema

    assert ema == approx(130.10, abs=0.1)


def test_ema_histogram(trade_date='2024-03-22'):
    """
    Validate histogram from strategy dataframe.
    """
    ema = sim.stock_obj.signal['ema'].loc[trade_date].histogram

    assert ema == approx(15.60, abs=0.1)


def test_ema_hist_norm(trade_date='2024-03-22'):
    """
    Validate histogram normalized from strategy dataframe.
    """
    ema = sim.stock_obj.signal['ema'].loc[trade_date].hist_norm

    assert ema == approx(0.728, abs=0.01)


def test_ema_signal(trade_date='2024-03-22'):
    """
    Validate signal from strategy dataframe.
    """
    ema = sim.stock_obj.signal['ema'].loc[trade_date].signal

    assert ema == 1.0