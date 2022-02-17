#!/usr/bin/env python3

import argparse
import datetime
import glob
import os
import pandas as pd

BASE_DIR = os.path.expanduser('~/tick_data/stooq_data')
HDF5_FILE='~/tick_data/stooq_ohlc_ds.h5'

def cli_args():

    parser = argparse.ArgumentParser(description='CSV Ingester')
    parser.add_argument('-d', dest='source_dir', action='store', default=BASE_DIR)
    parser.add_argument('-f', dest='hdf_file', action='store', default=HDF5_FILE)
    parser.add_argument('-i', dest='ignore_file', action='store')
    return parser.parse_args()

def get_ohlc_files(args):

    ohlc_files = glob.glob( os.path.join(args.source_dir, '**/*.txt'), recursive=True)
    return ohlc_files

def read_ignore_file(args):

    if not args.ignore_file:
        return []
    with open(args.match_file) as fh:
        lines = fh.readlines()
        return lines

def write_hdf(ticker_symbol, df):

    hdf = pd.HDFStore(args.hdf_file)
    if f'/{ticker_symbol.lower()}' in hdf.keys():
        hdf.remove(f'/{ticker_symbol.lower()}')
    else:
        hdf.put(ticker_symbol.lower(), df, format='table', data_columns=True)
    hdf.close()

if __name__ == '__main__':

    args = cli_args()
    ohlc_files = get_ohlc_files(args)

    columns = ['ticker', 'per', 'time', 'open', 'high', 'low', 'close', 'volume', 'open_int']
    used_cols = ['open', 'high', 'low', 'close', 'volume']

    ticker = {}

    for fn in ohlc_files:
        t_name = os.path.basename(fn).split('.')[0]
        try:
            ticker[t_name] = pd.read_csv(fn, header=0, index_col=2, names=columns, parse_dates=True)
            ticker[t_name] = ticker[t_name].drop(['ticker', 'per', 'time', 'open_int'], axis=1)
            write_hdf(t_name, ticker[t_name])
        except:
            print(f"Could not process {t_name}")
