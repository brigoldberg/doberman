#!/usr/bin/env python3
# bollinger_bands.py

import argparse
import locale
import multiprocessing as mp
import sys
import os
app_path = os.path.join(os.path.expanduser('~/sandbox/doberman/'))
sys.path.append(app_path)
from doberman import Universe
from doberman import BolBands
from doberman import Simulation

locale.setlocale(locale.LC_ALL, 'en_US')
NUM_PROCS=8

DATE_START = '2020-01-01'
DATE_END   = '2020-12-31'

def cli_args():
    parser = argparse.ArgumentParser(description='MuliProc Dogger')
    parser.add_argument('-f', dest='ticker_file', action='store', required=True)
    parser.add_argument('-c', dest='config', action='store', required=True)
    return parser.parse_args()

def read_ticker_file(args):
    symbols = []
    with open(args.ticker_file, 'r') as fh:
        lines = fh.readlines()
        for line in lines:
            symbols.append(line.rstrip().lower())
    return symbols

def queue_count(stock_list):
    # MP-Queue count must be no greater than amount of tickers being
    # analyzed. Return lesser of ticker count or processor count.
    if len(stock_list) < NUM_PROCS:
        return len(stock_list)
    else:
        return NUM_PROCS
    
def worker(work_q, result_q):
    while True:
        stock_obj = work_q.get()
        if stock_obj is None:
            work_q.task_done()
            break 
        bb = BolBands(stock_obj)
        bb_sim = Simulation(bb.stock_obj)
        bb_sim.paper_trade()
        result_q.put(bb_sim)

if __name__ == '__main__':

    args = cli_args()

    universe = Universe(read_ticker_file(args), config=args.config)
    universe.load_data()
    universe.align_dates(DATE_START, DATE_END)

    NUM_QUEUES = queue_count(universe.stocks)
    
    task_queue = mp.JoinableQueue()
    done_queue = mp.Queue()

    for stock_name, stock_obj in universe.stocks.items():
        task_queue.put(stock_obj)
    for x in range(NUM_QUEUES):
        task_queue.put(None)

    for i in range(NUM_QUEUES):
        p = mp.Process(target=worker, args=(task_queue, done_queue))
        p.start()

    sim_results = {}
    for stock_name, stock_obj in universe.stocks.items():
        result = done_queue.get()
        sim_results[result.stock_obj.symbol] = result.tradebook

    total_pnl = 0
    for ticker in universe.stocks.keys():
        pnl = sim_results[ticker].calc_book_pnl(DATE_END)
        total_pnl = total_pnl + pnl
        fmt_pnl = locale.format_string('%.0f', pnl, True)
        print(f"{ticker} PnL: ${fmt_pnl}")

    print(f"Total PnL: ${locale.format_string('%.0f', total_pnl, True)}")
