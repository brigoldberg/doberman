#!/usr/bin/env python3

import sys
import os
app_path = os.path.join(os.path.expanduser('~/sandbox/doberman/'))
sys.path.append(app_path)

import matplotlib.pyplot as plt
from matplotlib.dates import MonthLocator
from doberman import Universe
from doberman import EMA

stock_list = ['aapl', 'xom']
universe = Universe(stock_list, fetch_method='file',
                    data_dir='~/tick_data/')

universe.load_data()
ema = EMA(universe)

ema.plot_results('xom')

