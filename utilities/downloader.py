#!/usr/bin/env python3

import argparse
import datetime
import os
import pandas as pd
import pandas_datareader.data as web

CSV_DIR=os.path.expanduser('~/tick_data/csv')
HDF5_FILE='~/tick_data/ohlc_ds.h5'

def cli_args():
    parser = argparse.ArgumentParser(description='OHLC fetcher')
    parser.add_argument('-t', dest='ticker_sym', action='store', required=True)
    parser.add_argument('-s', dest='date_start', action='store', default=get_dstr(1095))
    parser.add_argument('-e', dest='date_end', action='store', default=get_dstr(1))
    parser.add_argument('-p', dest='provider', action='store', default='yahoo')
    return parser.parse_args()

def get_dstr(delta):
    target_date = datetime.datetime.now() - datetime.timedelta(days=delta)
    return target_date.strftime('%Y-%m-%d')

def web_fetch(args):
    df = web.DataReader(args.ticker_sym, args.provider, start=args.date_start,
                            end=args.date_end)
    df.columns = ['high', 'low', 'open', 'close', 'vol', 'adj_close']
    df.index.rename('date', inplace=True)
    return df

def write_csv_file(args):
    symbol = args.ticker_sym.lower()
    csv_fname = os.path.join(CSV_DIR, f'{symbol}.csv')
    df.to_csv(csv_fname)

def write_hdf(args, df):

    hdf = pd.HDFStore(HDF5_FILE)

    if f'/{args.ticker_sym.lower()}' in hdf.keys():
        hdf.remove(f'/{args.ticker_sym.lower()}')
    else:
        hdf.put(args.ticker_sym.lower(), df, format='table', data_columns=True)

    hdf.close()

if __name__ == '__main__':

    args = cli_args()
    df = web_fetch(args)
    write_csv_file(args)
    write_hdf(args, df)
