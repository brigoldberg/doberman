# universe.py
import logging
import pandas as pd
from .stock import Stock
from .utils import read_config

logger = logging.getLogger(__name__)

class Universe:

    def __init__(self, symbol_list, date_start, date_end, **kwargs):

        _config =  kwargs.get('config', {})
        if type(_config) is not dict:
            self.config = read_config(_config)
        else:
            self.config = _config

        log_level = self.config['logging'].get('log_level', 'ERROR')
        logger.setLevel(log_level.upper())      

        self.stocks = {}
        for symbol in symbol_list:
            self.stocks[symbol] = Stock(symbol, date_start, date_end, config=self.config)
            self.stocks[symbol].load_data()
            logger.info(f'adding {symbol} to universe')

        self._universe_book = Book(symbol_list)

    def log_trade(self, ticker, shares, cash):
        self.book.loc[ticker, ['shares', 'cash']] = shares, cash

    def calc_value(self):
        for ticker in self.stocks.keys():
            cash = self.stocks[ticker].usd_position()
            shares = self.stocks[ticker].shares_held()
            value = (shares * self.stocks[ticker].ohlc.iloc[-1]['close']) + cash
            self.book.loc[ticker, ['shares', 'cash', 'value']] = [shares, cash, value]

    def get_pnl(self):
        self.calc_value()
        pnl = self.book.value.sum()
        return pnl

    @property
    def book(self):
        return self._universe_book._book

class Book:

    def __init__(self, book_index):

        self._book = pd.DataFrame(index=book_index)
        self._book['shares'] = 0
        self._book['cash'] = 0
        self._book['value'] = 0
