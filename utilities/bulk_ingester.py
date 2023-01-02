#!/usr/bin/env python3
"""
Load data from CSV files into HDF
Script will not try to load data that was already loaded.
You can filter the selection of CSV files to load by passing
a ticker file to the script.
"""

import argparse
import glob
import logging
import os 
import pandas as pd

COLUMNS = ['ticker', 'per', 'time', 'open', 'high', 'low', 'close', 'volume', 'open_int']

def cli_args():
    parser = argparse.ArgumentParser(description='CSV Ingester')
    parser.add_argument('-s', dest='src_dir', action='store')
    parser.add_argument('-f', dest='h5_fn', action='store', default='./ohlc.h5')
    parser.add_argument('-v', dest='verbose', action='store_true')
    return parser.parse_args()

def get_logger(args):
    logger = logging.getLogger(__name__)
    if args.verbose:
        logging.basicConfig(format='%(message)s',level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(message)s',level=logging.WARNING)
    return logger

def get_csv_map(args):
    # Input directory and return list of all ohlc.txt files recursivly found
    csv_map = {}
    csv_files = glob.glob(os.path.join(args.src_dir, '**/*.txt'), recursive=True)
    for fn in csv_files:
        ticker = os.path.basename(fn).split('.')[0]
        csv_map[ticker] = fn
    return csv_map

def csv_to_df(ticker, ticker_fn):
    logger.debug(f'Reading file {ticker_fn}')
    try:
        df = pd.read_csv(ticker_fn, header=0, index_col=2, names=COLUMNS, parse_dates=True)
    except:
        logger.error(f'Could not create dataframe for {ticker}.')
        return None
    df.drop(['ticker', 'per', 'time', 'open_int'], axis=1)
    return df


if __name__ == '__main__':

    args = cli_args()
    logger = get_logger(args)

    tickers = get_csv_map(args)

    hdf_store = pd.HDFStore(args.h5_fn)

    for ticker, ticker_fn in tickers.items():
        try:
            df = csv_to_df(ticker, ticker_fn)
            hdf_store.put(ticker, df, format='table', data_columns=True)
            logger.debug(f'Wrote {ticker.upper()} into HDF5 file.')
        except:
            logger.error(f'Could not write {ticker} to HDF5 file.')

    hdf_store.close()