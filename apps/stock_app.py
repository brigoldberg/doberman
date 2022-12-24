#!/usr/bin/env python3

import logging
import os
import sys

app_path = os.path.join(os.path.expanduser('~/sandbox/doberman'))
sys.path.append(app_path)
from doberman import Stock
from doberman import StrategyFactory

DATE_START = '2014-01-01'
DATE_END   = '2014-03-30'

s = Stock('amzn', DATE_START, DATE_END, config='../debug-config.toml')
s.load_data()

sim = StrategyFactory(s, 'ema')
