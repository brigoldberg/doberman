#!/usr/bin/env python3

import argparse
import os
import sys
import pandas as pd


def cli_args():
    parser = argparse.ArgumentParser(description='HDF5 DF Reader')
    parser.add_argument('-y', dest='hdf_fn', action='store', default='~/tick_data/ohlc_ds.h5')
    parser.add_argument('-t', dest='ticker', action='store', required=True)
    parser.add_argument('-v', dest='verbose', action='store_true')
    return parser.parse_args()

def get_logger(args):
    logger = logging.getLogger()
    if args.verbose:
        logging.basicConfig(format='%(message)s',level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(message)s',level=logging.WARNING)
    return logger


if __name__ == '__main__':

    args = cli_args()
    try:
        df = pd.read_hdf(args.hdf_fn, key=f'/{args.ticker}')
        print(df)
    except KeyError:
        print(f'Could not find data for {args.ticker}')

