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

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def cli_args():
    parser = argparse.ArgumentParser(description='CSV Ingester')
    parser.add_argument('-s', dest='src_dir', action='store')
    parser.add_argument('-f', dest='h5_fn', action='store')
    return parser.parse_args()


if __name__ == '__main__':

    args = cli_args()