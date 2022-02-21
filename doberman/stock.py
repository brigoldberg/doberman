import os
import pandas as pd
import pandas_datareader.data as web
import toml
from .utils import read_config


class Stock:

    def __init__(self, symbol, *args, **kwargs):

        _config =  kwargs.get('config')
        if type(_config) is not dict:
            self.config = read_config(_config)
        else:
            self.config = _config

        self.symbol     = symbol.lower()
        self.tsdb       = None
        self.signal     = None
        self.tick_ds    = self.config['data_source']['hdf5_file']

    def load_data(self):

        self.tsdb = pd.read_hdf(self.tick_ds, key=f'/{self.symbol}')
        # create empty signal Series
        self.signal = pd.Series(index=self.tsdb.index)

    def snip_dates(self, date_start, date_end):

        """Prune rows from beginning and/or ends of the TSDB"""
        self.tsdb = self.tsdb.loc[date_start:date_end]
        self.signal = self.signal.loc[date_start:date_end]

