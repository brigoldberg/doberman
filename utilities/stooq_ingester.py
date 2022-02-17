#!/usr/bin/env python3

import argparse
import datetime 
import glob
import os
import pandas as pd

BASE_DIR = os.path.expanduser('~/tick_data/stooq_data')
HDF5_FILE='~/tick_data/stooq_ohlc_ds.h5'

def cli_args():

    parser = argparse.ArgumentParser(description='Stooq Ingester')
    parser.add_argument('-d', dest='source_dir', action='store', default=BASE_DIR)
    parser.add_argument('-f', dest='hdf_file', action='store', default=HDF5_FILE)
    parser.add_argument('-i', dest='include_fn', action='store')
    return parser.parse_args()

def get_csv_files(args):

    csv_map = {}
    csv_files = glob.glob( os.path.join(args.source_dir, '**/*.txt'), recursive=True)
    for csv_file in csv_files:
        ticker_name = os.path.basename(csv_file).split('.')[0]
        csv_map[ticker_name] = csv_file
    return csv_map

def csv_to_df(args, symbol, fname):

    columns = ['ticker', 'per', 'time', 'open', 'high', 'low', 'close', 'volume', 'open_int']
    df = pd.read_csv(fname, header=0, index_col=2, names=columns, parse_dates=True)
    df = df.drop(['ticker', 'per', 'time', 'open_int'], axis=1)
    return df

def get_include_list(args):

    if not args.include_fn:
       return []

    inc_list = []
    with open (args.include_fn, 'r') as fh:
        lines = fh.readlines()
        [ inc_list.append(line.rstrip().lower()) for line in lines ]
    return inc_list

def write_to_hdf(args, ticker_symbol,  df):

    hdf = pd.HDFStore(args.hdf_file)
    if f'/{ticker_symbol.lower()}' in hdf.keys():
        hdf.remove(f'/{ticker_symbol.lower()}')
    else:
        hdf.put(ticker_symbol.lower(), df, format='table', data_columns=True)
    hdf.close()
    

if __name__ == '__main__':

    args = cli_args()
    tickers = get_csv_files(args)
    include_list = get_include_list(args)

    for k, v in tickers.items():
        if k in include_list: 
            print(f"Working on {k} {v}")
            try:
                df = csv_to_df(args, k, tickers[k])
                write_to_hdf(args, k, df)
            except:
                print(f"Could not process {k}, {v}")
