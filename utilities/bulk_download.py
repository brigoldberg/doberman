#!/usr/bin/env python3
# name: bulk_download.py
"""
Check if data exists locally in HDF file
  - if yes -> move onto next symbol
  - if no  -> download data
"""
import argparse
import datetime
import logging
import os
import sys
import pandas as pd
import pandas_datareader.data as web


def cli_args():
    parser = argparse.ArgumentParser(description='OHLC fetcher')
    parser.add_argument('-y', dest='hdf_fn', action='store')
    parser.add_argument('-f', dest='ticker_file', action='store', required=True)
    parser.add_argument('-s', dest='date_start', action='store')
    parser.add_argument('-e', dest='date_end', action='store')
    parser.add_argument('-v', dest='verbose', action='store_true')
    return parser.parse_args()

def get_logger(args):
    if args.verbose:
        logging.basicConfig(format='%(message)s',level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(message)s',level=logging.WARNING)
        
    logger = logging.getLogger()
    return logger


class TickerFetch:

    HDF_FILE = os.path.expanduser('~/tick_data/ohlc_ds.h5')

    def __init__(self, symbol, date_start, date_end, *args, **kwargs):
        self.symbol     = symbol.lower()
        self.date_start = date_start
        self.date_end   = date_end
        self.hdf_file   = kwargs.get('hdf_file', self.HDF_FILE)

    def hdf_key_test(self):
        # get list of ticker symbols in hdf file and check if desired symbol
        # is in the file. Return True if key exists, false if it doesn't.
        store = pd.HDFStore(self.hdf_file, 'r')
        symbol_list = store.keys()
        store.close()
        if f'/{self.symbol}' in symbol_list:
            return True
        else:
            return False

    def test_date_range(self):
        # Get HDF tsdb start date and end date. Check if they are less than
        # and greater than the requeste date range. Return True/False.
        tsdb = pd.read_hdf(self.hdf_file, self.symbol)
        tsdb_start = tsdb.index[1]
        tsdb_end = tsdb.index[-1]
        date_start_ts = datetime.datetime.strptime(self.date_start, '%Y-%m-%d')
        date_end_ts = datetime.datetime.strptime(self.date_end, '%Y-%m-%d')
        if tsdb_start <= date_start_ts and tsdb_end >= date_end_ts:
            return True
        else:
            return False

    def download_data(self):

        df = web.DataReader(self.symbol, 'yahoo' , start=self.date_start,
                                end=self.date_end)
        df.columns = ['high', 'low', 'open', 'close', 'vol', 'adj_close']
        df.index.rename('date', inplace=True)
    
        hdf = pd.HDFStore(self.hdf_file)
    
        if f'/{self.symbol}' in hdf.keys():
            hdf.remove(f'/{self.symbol}')
        else:
            hdf.put(self.symbol, df, format='table', data_columns=True)
    
        hdf.close()        


if __name__ == '__main__':

    args = cli_args()
    logger = get_logger(args) 

    symbols = []

    with open(args.ticker_file, 'r') as fh:
        for line in fh:
            symbols.append(line.rstrip().lower())
    logger.debug(f"Found symbols {symbols}")

    for symbol in symbols:
        logger.debug(f"Working on symbol {symbol}")
        tf = TickerFetch(symbol, args.date_start, args.date_end, hdf_file='~/scratch/test.h5')

        if not tf.hdf_key_test():
            logger.debug(f"Missing HDF key for {symbol}. Will attempt download.")
            tf.download_data()

        if not tf.test_date_range():
            logger.debug(f"Incomplete date range for {symbol}. Will attempt download.")
            tf.download_data()

        print(tf.hdf_file)


