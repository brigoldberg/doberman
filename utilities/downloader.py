#!/usr/bin/env python3
"""
Script: yf_ohlc.py
Fetch OHLC data from Yahoo Finance and save as CSV files in local
directory.
"""
import argparse
import os
import pandas as pd
import pandas_datareader.data as web

def cli_args():
    parser = argparse.ArgumentParser(description='OHLC fetcher')
    parser.add_argument('-d', dest='data_dir', action='store', default='~/TICK_DATA')
    parser.add_argument('-f', dest='ticker_file', action='store', required=True)
    return parser.parse_args()

def check_exists(fname):
    if os.path.isfile(fname):
        return True
    return False

def web_fetch(ticker_sym):
    provider = 'yahoo'
    df = web.DataReader(ticker_sym, provider)
    df.columns = ['high', 'low', 'open', 'close', 'vol', 'adj_close']
    df.index.rename('date', inplace=True)
    return df

def write_csv_file(file_name):
    df.to_csv(file_name)


if __name__ == '__main__':

    args = cli_args()

    if not os.path.isdir(args.data_dir):
        os.makedirs(args.data_dir)

    with open(args.ticker_file, 'r') as tfh:

        for line in tfh.readlines():
            ticker_sym = line.rstrip()

            file_name = os.path.join(args.data_dir, f'{ticker_sym}.csv')

            if not check_exists(file_name):
                print(f'Fetching {ticker_sym}')
                df = web_fetch(ticker_sym)
                write_csv_file(file_name)
            else:
                print(f'{file_name} exists, skipping download')
