#!/usr/bin/env python3
import locale
import multiprocessing as mp
import os
import sys
from pprint import pprint
app_path = os.path.join(os.path.expanduser('~/sandbox/doberman'))
sys.path.append(app_path)
from doberman import BackTester
from doberman import StrategyFactory
from doberman import Universe

DATE_START = '2014-01-01'
DATE_END   = '2021-03-30'
SIGNAL_NAME = 'ema'

stocks = ['aapl', 'adbe', 'bac', 'ibm', 'jnj', 'jpm', 'ko', 'msft', 'nvda', 'pep', 't', 'tgt', 'v' ]
#stocks = ['aapl']
config = '../config.toml'

locale.setlocale(locale.LC_ALL, 'en_US')

def queue_count(stock_list):
    # MP-Queue count must be no greater than amount of tickers being
    # analyzed. Return lesser of ticker count or processor count.
    if len(stock_list) < mp.cpu_count():
        return len(stock_list)
    return mp.cpu_count()

def worker(wq, rq):
    while True:
        stock_obj = wq.get()
        if stock_obj is None:
            wq.task_done()
            break
        sim = StrategyFactory(stock_obj, SIGNAL_NAME) 
        bt = BackTester(stock_obj)
        bt.backtest(SIGNAL_NAME)
        rq.put(stock_obj)

if __name__ == '__main__':

    universe = Universe(stocks, DATE_START, DATE_END, config=config)

    NUM_QUEUES = queue_count(universe.stocks)

    work_queue = mp.JoinableQueue()
    result_queue = mp.Queue()	

    for ticker, stock_obj in universe.stocks.items():
        work_queue.put(stock_obj)
    for _ in range(NUM_QUEUES):
        work_queue.put(None)

    for _ in range(NUM_QUEUES):
        p = mp.Process(target=worker, args=(work_queue, result_queue))
        p.start()

    for stock_name, stock_obj in universe.stocks.items():
        result = result_queue.get()
        universe.stocks[result.ticker] = result

        #print(result.trade_log)
        universe.log_trade(result.ticker, result.shares_held(), result.usd_position())
        print(f'{result.ticker} shares: {result.shares_held()} -- cash: ${result.usd_position():0.2f}')

    universe.calc_value()
    print(universe.book)
    print(f'Universe PnL: {locale.currency(universe.get_pnl(), grouping=True)}')