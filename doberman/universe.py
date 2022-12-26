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
            try:
                self.stocks[symbol] = Stock(symbol, date_start, date_end, config=self.config)
                self.stocks[symbol].load_data()
                logger.info(f'adding {symbol} to universe')
            except:
                logger.info(f'Skipping {symbol} - could not load data or build supporting items.')
                del self.stocks[symbol]


        self._universe_book = Book(self.stocks)

    def log_trade(self, ticker, shares, cash):
        self.book.loc[ticker, ['shares', 'cash']] = shares, cash

    @property
    def book(self):
        return self._universe_book._book

    @property
    def pnl(self):
        return self._universe_book._pnl

class Book:
    """
    Track total universe value over time and individual stock book values at point in time.
    Book - stock position values at specific date
    PnL - TSDB of universe value over index of all trade dates
    """
    def __init__(self, universe):

        self.universe = universe
        
        self._book = pd.DataFrame(index=universe.keys())
        self._book['shares'] = 0
        self._book['cash'] = 0
        self._book['value'] = 0
        self._book['max_draw'] = 0

        self._pnl = pd.DataFrame(index=universe[next(iter(universe))].ohlc.index)
        self._pnl['share_value'] = 0
        self._pnl['cash'] = 0

    def calc_book(self, trade_date=None):
        
        for ticker in self.universe.keys():
            cash = self.universe[ticker].usd_position()
            shares = self.universe[ticker].shares_held()
            value = (shares * self.universe[ticker].ohlc.iloc[-1]['close']) + cash
            max_draw = self.universe[ticker].max_drawdown()
            self._book.loc[ticker, ['shares', 'cash', 'value', 'max_draw']] = [shares, cash, round(value, 2), round(max_draw, 2)]

    def calc_pnl(self, trade_date=None):


        for trade_date in self._pnl.index:

            sv_sum = 0
            cv_sum = 0

            for ticker in self.universe.keys():
               share_price = self.universe[ticker].spot_price(trade_date)
               sv_sum = sv_sum + (share_price * self.universe[ticker].shares_held(trade_date))
               cv_sum = cv_sum + self.universe[ticker].usd_position(trade_date)

            self._pnl.loc[trade_date, ['share_value', 'cash']] = [sv_sum, cv_sum]