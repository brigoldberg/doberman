#!/usr/bin/env python3

import os
import sys

app_path = os.path.join(os.path.expanduser('~/sandbox/doberman'))
sys.path.append(app_path)
from doberman import BackTester
from doberman import StrategyFactory
from doberman import Stock

DATE_START = '2014-01-01'
DATE_END   = '2014-03-30'

s = Stock('amzn', DATE_START, DATE_END, config='../debug-config.toml')
s.load_data()

sim = StrategyFactory(s, 'ema')
bt = BackTester(s)
bt.backtest('ema')

print(f'{s.ticker.upper()} shares: {s.shares_held()} -- cash: ${s.usd_position():0.2f}')
print(s.trade_log)
