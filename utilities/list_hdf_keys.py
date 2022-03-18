#!/usr/bin/env python3

import argparse
import os
import pprint
import pandas as pd

HDF5_FILE=os.path.expanduser('~/tick_data/ohlc.h5')

parser = argparse.ArgumentParser(description='List HDF5 Keys')
parser.add_argument('-f', dest='hdf_file', action='store', default=HDF5_FILE)
args =  parser.parse_args()

store = pd.HDFStore(args.hdf_file, 'r')
# strip off quotes and leading '/'
tickers = [ x.rstrip()[1:] for x in store.keys() ]

pprint.pprint(tickers)
