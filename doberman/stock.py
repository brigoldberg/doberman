import pandas as pd
import pandas_datareader.data as web


class Stock:

    data_source = 'yahoo'

    def __init__(self, symbol, quantity=0):
        self.symbol         = symbol
        self.tsdb           = None
        self.signal         = None
        self.cash_position  = 0
        self.shares_held     = quantity
        self.trade_log      = []

    def _init_positions(self):
        self.signal = pd.DataFrame(index=self.tsdb.index)

    def web_fetch(self):
        """Pull data from Interwebs"""
        self.tsdb = web.DataReader(self.symbol, self.data_source)
        self.tsdb.columns = ['high', 'low', 'open', 'close', 'vol', 'adj_close']
        self.tsdb.index.rename('date', inplace=True)
        # Create empty DataFrames for signal, cash and shares
        self._init_positions()

    def snip_dates(self, date_start, date_end):
        """Prune rows from beginning and/or ends of the TSDB"""
        self.tsdb = self.tsdb.loc[date_start:date_end]

    def read_csv(self, fname):
        """Create DataFrame from local CSV file"""
        try:
            self.tsdb = pd.read_csv(fname, index_col=0)
            # Create empty DataFrames for signal, cash and shares
            self._init_positions()
        except FileNotFoundError :
            print(f'Cannot open file: {fname}')

    def write_csv(self, fname):
        """Write Pandas DataFrame to local CSV file"""
        self.tsdb.to_csv(fname)
