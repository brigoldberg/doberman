import os
import pandas as pd
import toml
from .utils import read_config
from .doberlog import get_logger


class Stock:

    def __init__(self, symbol, *args, **kwargs):

        self.symbol     = symbol.lower()
        self.tsdb       = None
        self.signal     = None

        _config =  kwargs.get('config')
        if type(_config) is not dict:
            self.config = read_config(_config)
        else:
            self.config = _config

        log_level   = self.config['logging']['log_level']
        self.logger = get_logger(f'stock-{self.symbol}', log_level)

        self.tick_ds    = self.config['data_source']['hdf5_file']

    def load_data(self):

        self.tsdb = pd.read_hdf(self.tick_ds, key=f'/{self.symbol}')
        # create empty signal Series
        self.signal = pd.Series(index=self.tsdb.index, dtype='int32')
        self.logger.info(f'{self.symbol.upper()}: loaded tsdb and set empty signal')

    def snip_dates(self, date_start, date_end):

        """Prune rows from beginning and/or ends of the TSDB"""
        self.tsdb = self.tsdb.loc[date_start:date_end]
        self.signal = self.signal.loc[date_start:date_end]
        self.logger.info(f'{self.symbol.upper()}: pruned dates {date_start} to {date_end}')

