#!/usr/bin/env python3

import argparse
import pandas as pd

HDF_FILE = '~/sandbox/doberman/data/ohlc.h5'

def cli_args():
    parser = argparse.ArgumentParser(description='HDF5 DF Reader')
    parser.add_argument('-f', dest='hdf_fn', action='store', default=HDF_FILE)
    parser.add_argument('-t', dest='ticker_file', action='store', required=True)
    parser.add_argument('-v', dest='verbose', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':

    args = cli_args()

    hdf_tickers = pd.HDFStore(args.hdf_fn, 'r')

    with open(args.ticker_file, 'r') as fh:
        lines = fh.readlines()
        for line in lines:
            if f'/{line.rstrip().lower()}' not in hdf_tickers:
                print(f'Ticker {line.rstrip()} not in HDF5 file')


