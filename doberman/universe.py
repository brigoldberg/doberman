import os
import pandas as pd
from .stock import Stock as Stock
from .utils import iterate_basket as iterate_basket


class Universe:

    def __init__(self, stock_list, fetch_method='web', data_dir='tick_data'):
        self.fetch_method       = fetch_method
        self.data_dir           = data_dir
        self.correlation_matrix = None

        self.stocks = {}
        for stock_symbol in stock_list:
            self.stocks[stock_symbol] = Stock(stock_symbol)

    @iterate_basket
    def list_basket(self, stock_obj):
        """Print a list of all stocks in the universe"""
        print(f'{stock_obj.symbol}')

    @iterate_basket
    def load_data(self, stock_obj):
        """ Load TSDB with data """
        if self.fetch_method == 'web':
            stock_obj.web_fetch()
        elif self.fetch_method == 'file':
            fname = os.path.join(self.data_dir, f'{stock_obj.symbol}.csv')
            stock_obj.read_csv(fname)

    @iterate_basket
    def align_dates(self, stock_obj, start_date, end_date):
        stock_obj.snip_dates(start_date, end_date)

    def get_correlation(self):
        """
        Create DataFrame of adjusted close prices for each ticker.
        Return Dataframe of correlations for each ticker pair.
        """
        data = [self.stocks[x].tsdb.adj_close for x in self.stocks.keys()]
        ticker_names = self.stocks.keys()
        universe_prices = pd.concat(data, axis=1, keys=ticker_names)

        self.correlation_matrix = universe_prices.corr()
