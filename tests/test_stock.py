# test_stock.py

import os
import sys
from pytest import approx
app_path = os.path.join(os.path.expanduser('~/sandbox/doberman'))
sys.path.append(app_path)
from doberman import Stock

symbol = 'fake'
date_start = '2024-03-01'
date_end = '2024-03-30'
trades = {
    '2024-03-07': ('buy', 2),
    '2024-03-14': ('sell', 1),
    '2024-03-21': ('buy', 1),
    }

CONFIG = os.path.expanduser('~/sandbox/doberman/test-config.toml')
stock = Stock(symbol, date_start, date_end, config=CONFIG)
stock.load_data()

def test_configuration():
    """
    Load configuration and test reading a parameter.
    """
    cfg_val = stock.config['data_map'].get('spot_quote_col', '')
    assert cfg_val == 'close'


def test_load_data(test_date='2024-03-11'):
    """
    Test reading items from dataframe to ensure proper data loading.
    """
    row_open = stock.spot_price(test_date, 'open')
    row_close = stock.spot_price(test_date, 'close')

    assert [row_open, row_close] == approx([122.00, 123.90], abs=1)


def test_log_trades(test_date='2024-03-21'):
    """
    Add trades to trade log, confirm shares held and USD position
    at specified data.
    """
    col_name = stock.config['data_map'].get('spot_quote_col', 'close')

    # Subimt fake orders
    for trade_date, stock_order in trades.items():
        order_type, shares = stock_order
        trade_cost = shares * stock.spot_price(trade_date, col_name)
        stock.log_trade(trade_date, order_type, shares, trade_cost)

    results = [
        stock.trade_log.loc[test_date].shares,
        stock.trade_log.loc[test_date].order_type,
        stock.trade_log.loc[test_date].trade_cost ]

    assert results == [1, 'buy', -143.8]


def test_shares_held(test_date='2024-03-29'):
    """
    Sum of shares: 2 - 1 + 1 == 2
    """
    assert stock.shares_held(trade_date=test_date) == 2


def test_cash_position(test_date='2024-03-29'):
    """
    Cost of trades: -232.4 + 129.7 - 143.8 == -246.50
    """
    assert stock.cash_position(trade_date=test_date) == -246.50


def test_position_value(test_date='2024-03-29'):
    """
    Calc value of cash and shares: -246.5(cash) + (2 * 161.7) == 76.90
    """
    assert stock.position_value(trade_date='2024-03-29') == approx(76.9, abs=1)


def test_max_drawdown(test_date='2024-03-29'):
    """
    Max value of cash outlaid from trading
    """
    assert stock.max_drawdown() == approx(-246.5, abs=1)


def test_spot_price():

    assert stock.spot_price() == 161.7


def test_rate_of_return():

    assert stock.rate_of_return() == approx(0.313, abs=0.01)
