import os
import pandas as pd
import toml
from .stock import Stock as Stock
from .utils import iterate_basket as iterate_basket
from .utils import read_config as read_config


class Universe:

    def __init__(self, stock_list, *args, **kwargs):

        self.stocks = {}
        config_file = kwargs.get('config', './config.toml')
        self.config = read_config(config_file)

        for stock_symbol in stock_list:
            self.stocks[stock_symbol] = Stock(stock_symbol, config=self.config)

    @iterate_basket
    def list_basket(self, stock_obj):
        """Print a list of all stocks in the universe"""
        print(f'{stock_obj.symbol}')

    @iterate_basket
    def load_data(self, stock_obj):
        """ Load TSDB with data from HDF5 files """
        stock_obj.load_data()

    @iterate_basket
    def align_dates(self, stock_obj, start_date, end_date):
        stock_obj.snip_dates(start_date, end_date)

    def get_correlation(self, *args, **kwargs):
        """
        Create DataFrame of adjusted close prices for each ticker.
        Return Dataframe of correlations for each ticker pair.
        """
        close = kwargs.get(close, 'close')

        data = [self.stocks[x].tsdb[self.CLOSE] for x in self.stocks.keys()]
        ticker_names = self.stocks.keys()
        universe_prices = pd.concat(data, axis=1, keys=ticker_names)

        self.correlation_matrix = universe_prices.corr()
