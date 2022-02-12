#!/usr/bin/env python3

'''
% time ./poodle.py
Simulation PnL: $103,437
./poodle.py  19.70s user 0.90s system 95% cpu 21.485 total
'''

import argparse
import sys
import os
app_path = os.path.join(os.path.expanduser('~/sandbox/doberman/'))
sys.path.append(app_path)
from doberman import Universe
from doberman import EMA
from doberman import Simulation

def cli_args():
    parser = argparse.ArgumentParser(description='MuliProc Dogger')
    parser.add_argument('-f', dest='ticker_file', action='store')
    parser.add_argument('-v', dest='verbose', action='store_true')
    return parser.parse_args()

def read_ticker_file(args):
    symbols = []
    with open(args.ticker_file, 'r') as fh:
        lines = fh.readlines()
        for line in lines:
            symbols.append(line.rstrip().lower())
    return symbols

args = cli_args()
universe = Universe(read_ticker_file(args))
universe.load_data()
universe.align_dates('2020-01-01', '2020-12-31')

# Calculate EMA signals
ema = EMA(universe)

# Run trading simulation using EMA signals. The signals
# are in the "universe" object instance so we pass that
# to the Simulation object.
ema_sim = Simulation(universe)
ema_sim.paper_trade()

last_trade_date = universe.stocks['aapl'].tsdb.index[-1]

ema_sim.calc_pnl(last_trade_date)
