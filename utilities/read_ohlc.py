#!/usr/bin/env python3

import argparse
import datetime
import locale
from locale import currency as cc
import os
import sys
import pandas as pd

locale.setlocale( locale.LC_ALL, '' )
HDF_FILE='~/tick_data/ohlc.h5'

def cli_args():
    parser = argparse.ArgumentParser(description='HDF5 DF Reader')
    parser.add_argument('-y', dest='hdf_fn', action='store', default=HDF_FILE)
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

def print_record(args, d):
    date = datetime.datetime.strftime(d.name, '%Y-%m-%d')
    try:
        print(f'{args.ticker}: {date} -- o:{cc(d.open)} h:{cc(d.high)} l:{cc(d.low)} c:{cc(d.close)}' + 
                f' adj_cls:{cc(d.adj_close)} -- vol:{d.vol:,.0f}')
    except:
        print(f'{args.ticker}: {date} -- o:{cc(d.open)} h:{cc(d.high)} l:{cc(d.low)} c:{cc(d.close)}' + 
                f' -- vol:{d.volume:,.0f}')

if __name__ == '__main__':

    args = cli_args()
    try:
        df = pd.read_hdf(args.hdf_fn, key=f'/{args.ticker}')
        print_record(args, df.iloc[1])
        print_record(args, df.iloc[-1])
    except KeyError:
        print(f'Could not find data for {args.ticker}')

