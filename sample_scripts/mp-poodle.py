#!/usr/bin/env python3
# mp-poodle.py

import argparse
import multiprocessing as mp
import sys
import os
app_path = os.path.join(os.path.expanduser('~/sandbox/doberman/'))
sys.path.append(app_path)
from mp_doberman import Universe
from mp_doberman import DogPack
from mp_doberman import EMA
from mp_doberman import Simulation

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
    
def worker(data_sets,  results):
    stock_obj = data_sets.get()
    ema = EMA(stock_obj)
    ema_sim = Simulation(ema.stock_obj)
    ema_sim.paper_trade()
    results.put(ema_sim)

if __name__ == '__main__':

    args = cli_args()

    universe = Universe(read_ticker_file(args))
    universe.load_data()
    universe.align_dates('2020-01-01', '2020-12-31')
    
    task_queue = mp.Queue()
    done_queue = mp.Queue()

    for stock_name, stock_obj in universe.stocks.items():
        task_queue.put(stock_obj)

    for stock_name, stock_obj in universe.stocks.items():
        p = mp.Process(target=worker, args=(task_queue, done_queue))
        p.start()

    for stock_name, stock_obj in universe.stocks.items():
        result = done_queue.get()
        result.calc_pnl()
