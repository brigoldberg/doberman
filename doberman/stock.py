import os
import pandas as pd
import pandas_datareader.data as web


class Stock:

    tick_ds = os.path.expanduser('~/tick_data/stooq_ohlc.h5')

    def __init__(self, symbol):
        self.symbol         = symbol.lower()
        self.tsdb           = None
        self.signal         = None

    def load_data(self):
        self.tsdb = pd.read_hdf(self.tick_ds, key=f'/{self.symbol}')
        # create empty signal Series
        self.signal = pd.Series(index=self.tsdb.index)

    def snip_dates(self, date_start, date_end):
        """Prune rows from beginning and/or ends of the TSDB"""
        self.tsdb = self.tsdb.loc[date_start:date_end]
        self.signal = self.signal.loc[date_start:date_end]

