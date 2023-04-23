#!/usr/bin/env python3
import argparse
import locale
import logging
import multiprocessing as mp
import os
import sys
from pprint import pprint
app_path = os.path.join(os.path.expanduser('~/sandbox/doberman'))
sys.path.append(app_path)
from doberman import BackTester
from doberman import StrategyFactory
from doberman import Universe

DATE_START = '2020-01-01'
DATE_END   = '2021-03-30'
SIGNAL_NAME = 'ema'

locale.setlocale(locale.LC_ALL, 'en_US')

def cli_args():
    parser = argparse.ArgumentParser(description='MuliProc Dogger')
    parser.add_argument('-f', dest='ticker_file', action='store', required=True)
    parser.add_argument('-c', dest='config', action='store', required=True)
    parser.add_argument('-s', dest='date_start', action='store', type=str, default=DATE_START)
    parser.add_argument('-e', dest='date_end', action='store', type=str, default=DATE_END)
    parser.add_argument('-x', dest='signal_name', action='store', default=SIGNAL_NAME)
    parser.add_argument('-v', dest='verbose', action='store_true')
    return parser.parse_args()

def get_logger(args):
    logger = logging.getLogger()
    if args.verbose:
        logging.basicConfig(format='%(levelname)s - %(message)s',level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s - %(message)s',level=logging.WARNING)
    return logger

def read_ticker_file(args):
    symbols = []
    try:
        with open(args.ticker_file, 'r') as fh:
            lines = fh.readlines()
            for line in lines:
                symbols.append(line.rstrip().lower())
    except:
        logger.error(f'Could not open {args.ticker_file}.')
    return symbols

def queue_count(stock_list):
    # MP-Queue count must be no greater than amount of tickers being
    # analyzed. Return lesser of ticker count or processor count.
    if len(stock_list) < mp.cpu_count():
        return len(stock_list)
    return mp.cpu_count()

def worker(wq, rq, signal_name):
    while True:
        stock_obj = wq.get()
        if stock_obj is None:
            wq.task_done()
            break
        sim = StrategyFactory(stock_obj, signal_name) 
        bt = BackTester(stock_obj)
        bt.backtest(signal_name)
        rq.put(stock_obj)

if __name__ == '__main__':

    args = cli_args()
    logger = get_logger(args)

    universe = Universe(read_ticker_file(args), args.date_start, 
                                args.date_end, config=args.config, 
                                signal_name=args.signal_name)

    NUM_QUEUES = queue_count(universe.stocks)

    work_queue = mp.JoinableQueue()
    result_queue = mp.Queue()	

    for ticker, stock_obj in universe.stocks.items():
        work_queue.put(stock_obj)
    for _ in range(NUM_QUEUES):
        work_queue.put(None)

    for _ in range(NUM_QUEUES):
        p = mp.Process(target=worker, args=(work_queue, result_queue, args.signal_name))
        p.start()

    # Replace original universe item with processed data. We need to do this
    # because the work was done in a separate process and the original 
    # universe object was not updated with the results.
    for stock_name, stock_obj in universe.stocks.items():
        result = result_queue.get()
        universe.stocks[result.ticker] = result

        # REPORTING
        universe.log_trade(result.ticker, result.shares_held(), result.usd_position())

    universe._universe_book.calc_book()
    universe._universe_book.calc_pnl()
    max_drawdown = universe.pnl['cash'].min()

    print(f'Max drawdown: {locale.currency(max_drawdown, grouping=True)}')
    #print(universe.book)
    print(f"Stonk'd Gains: {locale.currency(universe.book['value'].sum(), grouping=True)}")

    universe.universe_results()
    from pprint import pprint
    pprint(universe.simulation_result)
