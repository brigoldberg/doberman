#!/usr/bin/env python3

import argparse
import datetime
import logging
import os
import sys
import pandas as pd
import pandas_datareader.data as web


def cli_args():
    parser = argparse.ArgumentParser(description='OHLC fetcher')
    parser.add_argument('-y', dest='hdf_fn', action='store', default='~/tick_data/ohlc_ds.h5')
    parser.add_argument('-f', dest='ticker_file', action='store', required=True)
    parser.add_argument('-s', dest='date_start', action='store')
    parser.add_argument('-e', dest='date_end', action='store')
    parser.add_argument('-v', dest='verbose', action='store_true')
    return parser.parse_args()

def get_logger(args):
    logger = logging.getLogger()
    if args.verbose:
        logging.basicConfig(format='%(message)s',level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(message)s',level=logging.WARNING)
    return logger

def get_symbol_list(args):
    symbols = []
    with open(args.ticker_file, 'r') as fh:
        lines = fh.readlines()
        for line in lines:
            symbol = line.rstrip().lower()
            symbols.append(symbol)
            logger.debug(f'Appending {symbol} to symbol list')
    return symbols

class TickerFetch:

    def __init__(self, symbol, **kwargs):
        self.symbol     = symbol
        self.date_start = kwargs.get('date_start')
        self.date_end   = kwargs.get('date_end')
        self.hdf_file   = kwargs.get('hdf_file')

        if not self.key_check():
            logger.debug(f'{self.symbol} data missing. Downloading to {self.hdf_file}.')
            self.download_data()
        #elif not self.date_range_check():
        #    logger.debug(f'{self.symbol} key exists w/incorrect date range in {self.hdf_file}.')
        #    self.download_data()
        else:
            logger.debug(f'{self.symbol} data exists in {self.hdf_file}.')

    def key_check(self):
        store = pd.HDFStore(self.hdf_file, 'r')
        symbol_list = store.keys()
        store.close()
        if f'/{self.symbol}' in symbol_list:
            logger.debug(f'{self.symbol} exists in {self.hdf_file}')
            return True
        else:
            logger.debug(f'{self.symbol} missing from {self.hdf_file}')
            return False

    def date_range_check(self):
        pass

    def download_data(self):
        try:
            df = web.DataReader(self.symbol, 'yahoo' , start=self.date_start,
                                end=self.date_end)
        except:
            logger.error(f'Could not fetch data for {self.symbol}')
            return
        df.columns = ['high', 'low', 'open', 'close', 'vol', 'adj_close']
        df.index.rename('date', inplace=True)
        hdf = pd.HDFStore(self.hdf_file)
        hdf.put(self.symbol, df, format='table', data_columns=True)
        hdf.close()


if __name__ == '__main__':

    args = cli_args()
    logger = get_logger(args)
    symbol_list = get_symbol_list(args)

    # assume hdf5 file exists

    for symbol in symbol_list:
        loader = TickerFetch(symbol, hdf_file=args.hdf_fn)
