#!/usr/bin/env python3
# test_stock.py

import os
import sys
from pytest import approx
app_path = os.path.join(os.path.expanduser('~/sandbox/doberman'))
sys.path.append(app_path)
from doberman import Stock

symbol = 'spy'
date_start = '2015-01-01'
date_end = '2015-01-28'
trades = {
    '2015-01-02': ('buy', 50),
    '2015-01-07': ('sell', 50),
    '2015-01-12': ('buy', 56),
    '2015-01-21': ('sell', 50),
    '2015-01-27': ('buy', 60) }
"""
DATE        PRICE
2015-01-02  179.005
2015-01-07  176.267
2015-01-12  176.566
2015-01-21  176.984
2015-01-27  176.655
"""

stock = Stock(symbol, date_start, date_end, config='../config.toml')
stock.load_data()

def test_configuration():
    # Read configuration and check a parameter settting.
    cfg_val = stock.config['data_map'].get('spot_quote_col', '')
    assert cfg_val == 'close'

def test_data_load(test_date='2015-01-09'):
    # Read dataframe and confirm trade date / price match.
    #row_open = stock.ohlc.loc[test_date]['open']
    #row_close = stock.ohlc.loc[test_date]['close']
    row_open = stock.spot_price(test_date, 'open')
    row_close = stock.spot_price(test_date, 'close')

    assert [row_open, row_close] == approx([179.82, 177.96], abs=1)

def test_log_trades(test_date='2015-01-13'):
    # Add trades to trade log. Confirm shares held and USD position
    # at specified date.
    col_name = stock.config['data_map'].get('spot_quote_col', 'close')

    for trade_date, stock_order in trades.items():
        order_type, shares = stock_order
        trade_cost = shares * stock.spot_price(trade_date, col_name)
        stock.log_trade(trade_date, order_type, shares, trade_cost)

    results = [
        stock.shares_held(test_date), stock.usd_position(test_date),
        stock.shares_held(), stock.usd_position()
    ]

    assert results == approx([56.0, -10024.6, 66, -11774.7], abs=1)
    
def test_pnl_report():
    pass