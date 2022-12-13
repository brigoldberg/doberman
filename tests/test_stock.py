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
    '2015-01-02': 50,
    '2015-01-07': -50,
    '2015-01-12': 56,
    '2015-01-21': -50,
    '2015-01-27': 60 }
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

    cfg_val = stock.config['data_map'].get('spot_quote_col', '')
    assert cfg_val == 'close'

def test_data_load():

    row_open = stock.ohlc.loc['2015-01-09']['open']
    row_close = stock.ohlc.loc['2015-01-09']['close']

    assert [row_open, row_close] == approx([179.82, 177.96], abs=1)

def test_log_trades():

    col_name = stock.config['data_map'].get('spot_quote_col', 'close')

    for trade_date, shares in trades.items():
        spot_price = stock.ohlc[col_name].loc[trade_date]
        trade_cost = shares * spot_price
        stock.log_trade(trade_date, shares, trade_cost)

    results = [ stock.shares_held('2015-01-13'), stock.shares_held(),
        stock.usd_position('2015-01-13'), stock.usd_position('2015-01-13')]

    assert results == approx([56.0, 66.0, 10024.6, 10024.6], abs=1)
    
    