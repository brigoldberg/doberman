import os
import pandas as pd
import toml
from .stock import Stock 
from .utils import iterate_basket 
from .utils import read_config 
from .doberlog import get_logger


class Universe:

    def __init__(self, stock_list, *args, **kwargs):

        self.stocks = {}
        
        _config = kwargs.get('config')
        if type(_config) is not dict:
            self.config = read_config(_config)
        else:
            self.config = _config

        for stock_symbol in stock_list:
            self.stocks[stock_symbol] = Stock(stock_symbol, config=self.config)

        log_level = self.config['logging']['log_level']
        self.logger = get_logger('universe', log_level)

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

