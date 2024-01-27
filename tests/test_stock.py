#!/usr/bin/env python3
# test_stock.py

import os
import sys
from pytest import approx
app_path = os.path.join(os.path.expanduser('~/sandbox/doberman'))
sys.path.append(app_path)
from doberman import Stock

symbol = 'brk-a'
date_start = '2015-06-01'
date_end = '2015-06-30'
trades = {
    '2015-06-02': ('buy', 1),
    '2015-06-05': ('sell', 1),
    '2015-06-12': ('buy', 1),
    '2015-06-22': ('sell', 1),
    '2015-06-29': ('buy', 1) 
    }

CONFIG = os.path.expanduser('~/sandbox/doberman/config.toml')
stock = Stock(symbol, date_start, date_end, config=CONFIG)
stock.load_data()

def test_configuration():
    # TEST CONFIGURATION
    # Read configuration and check a parameter settting.
    
    cfg_val = stock.config['data_map'].get('spot_quote_col', '')
    assert cfg_val == 'close'

def test_load_data(test_date='2015-06-09'):
    # TEST OHLC CLASS - data loading and date snipping
    # Read dataframe and confirm trade date / price match.
    
    row_open = stock.spot_price(test_date, 'open')
    row_close = stock.spot_price(test_date, 'close')

    assert [row_open, row_close] == approx([209400.00, 209700.00], abs=1)

def test_log_trades(test_date='2015-06-15'):
    # Add trades to trade log. Confirm shares held and USD position
    # at specified date.
    
    col_name = stock.config['data_map'].get('spot_quote_col', 'close')

    # Subimt fake orders
    for trade_date, stock_order in trades.items():
        order_type, shares = stock_order
        trade_cost = shares * stock.spot_price(trade_date, col_name)
        stock.log_trade(trade_date, order_type, shares, trade_cost)

    results = [
        stock.trade_log.loc['2015-06-05'].shares,
        stock.trade_log.loc['2015-06-05'].order_type,
        stock.trade_log.loc['2015-06-05'].trade_cost ]

    assert results == [-1.0, 'sell', 211560.0]

def test_trade_log_stats(test_date='2015-06-30'):
    # Test calculation of cash position, shares held and max
    # drawdown

    results = [
        stock.shares_held(test_date),
        stock.cash_position(test_date),
        stock.shares_held('2015-06-15'),
        stock.cash_position('2015-06-15'),
        stock.max_drawdown()]

    assert results == [1, -206440, 1, -214020, -214820.0]
