#!/usr/bin/env python3
# mp-poodle.py

import argparse
import multiprocessing as mp
import sys
import os
app_path = os.path.join(os.path.expanduser('~/sandbox/doberman/'))
sys.path.append(app_path)
from doberman import Universe
from doberman import MACD
from doberman import Simulation

NUM_PROCS=4

def cli_args():
    parser = argparse.ArgumentParser(description='MuliProc Dogger')
    parser.add_argument('-f', dest='ticker_file', action='store', required=True)
    parser.add_argument('-v', dest='verbose', action='store_true')
    return parser.parse_args()

def read_ticker_file(args):
    symbols = []
    with open(args.ticker_file, 'r') as fh:
        lines = fh.readlines()
        for line in lines:
            symbols.append(line.rstrip().lower())
    return symbols
    
def worker(work_q, result_q):
    while True:
        stock_obj = work_q.get()
        if stock_obj is None:
            work_q.task_done()
            break 
        macd = MACD(stock_obj)
        macd_sim = Simulation(macd.stock_obj)
        macd_sim.paper_trade()
        result_q.put(macd_sim)

if __name__ == '__main__':

    args = cli_args()

    universe = Universe(read_ticker_file(args))
    universe.load_data()
    universe.align_dates('2020-01-01', '2020-12-31')
    
    task_queue = mp.JoinableQueue()
    done_queue = mp.Queue()

    for stock_name, stock_obj in universe.stocks.items():
        task_queue.put(stock_obj)
    for x in range(NUM_PROCS):
        task_queue.put(None)

    for i in range(NUM_PROCS):
        p = mp.Process(target=worker, args=(task_queue, done_queue))
        p.start()

    sim_results = {}
    for stock_name, stock_obj in universe.stocks.items():
        result = done_queue.get()
        sim_results[result.stock_obj.symbol] = result.stock_obj.tsdb
        result.calc_pnl()`
