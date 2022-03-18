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

CSV_SRC_DIR = '/Users/brian/tick_data/data'
HDF5_FN = '/Users/brian/tick_data/ohlc.h5'
COLUMNS = ['ticker', 'per', 'time', 'open', 'high', 'low', 'close', 'volume', 'open_int']

def cli_args():
    parser = argparse.ArgumentParser(description='CSV Ingester')
    parser.add_argument('-s', dest='src_dir', action='store', default=CSV_SRC_DIR)
    parser.add_argument('-f', dest='h5_fn', action='store', default=HDF5_FN)
    parser.add_argument('-i', dest='tickers', action='store')
    parser.add_argument('-v', '--verbose',  dest='verbose', action='store_true')
    return parser.parse_args()

def get_logger(args):
    logger = logging.getLogger()
    if args.verbose:
        logging.basicConfig(format='%(message)s',level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(message)s',level=logging.WARNING)
    return logger

def file_to_list(fn):
    # Input file name, parse and return list of items
    with open(fn) as fh:
        lines = fh.readlines()
    tickers = [ line.rstrip().lower() for line in lines ]
    return tickers

def get_csv_map(args):
    # Input directory and return list of all csv.txt files recursivly found
    csv_map = {}
    csv_files = glob.glob(os.path.join(args.src_dir, '**/*.txt'), recursive=True)
    for fn in csv_files:
        ticker = os.path.basename(fn).split('.')[0]
        csv_map[ticker] = fn
    return csv_map

def csv_to_df(args, fn):
    # Input CSV file and return Pandas DataFrame
    try:
        df = pd.read_csv(fn, header=0, index_col=2, names=COLUMNS, parse_dates=True)
        df = df.drop(['ticker', 'per', 'time', 'open_int'], axis=1)
        return df
    except:
        return None

def list_hdf_keys(args):
    # Input HDF5 file and retun list of keys
    store = pd.HDFStore(args.h5_fn, 'r')
    h5_keys = [ x.rstrip()[1:] for x in store.keys() ] 
    store.close()
    return h5_keys


if __name__ == '__main__':

    args = cli_args()
    logger = get_logger(args)
    
    # Get dict of all CSV files and list of tickers we want to ingest
    ticker_map = get_csv_map(args)
    requested_tickers = file_to_list(args.tickers)

    if os.path.exists(args.h5_fn):
        existing_keys = list_hdf_keys(args)
    else:
        existing_keys = []

    # Create list of tickers which are eligible for insertion. They are requested
    # and they do not alredy exist in the HDF file.
    insertable_tickers = []
    for ticker in requested_tickers:
        if ticker not in existing_keys:
            insertable_tickers.append(ticker)

    hdf_store = pd.HDFStore(args.h5_fn)
    for ticker in insertable_tickers:
        try:
            df = csv_to_df(args, ticker_map[ticker])
            hdf_store.put(ticker, df, format='table', data_columns=True)
        except:
            logger.error(f"Could not load {ticker}")
    hdf_store.close()


