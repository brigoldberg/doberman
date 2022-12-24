# stock.py

from .utils import get_logger
from .utils import read_config
import pandas as pd


class Stock:

    def __init__(self, ticker, date_start, date_end, **kwargs):

        self.ticker = ticker
        self.signal = {}

        _config =  kwargs.get('config', {})
        if type(_config) is not dict:
            self.config = read_config(_config)
        else:
            self.config = _config

        log_level = self.config['logging'].get('log_level', 'warning')
        self.logger = get_logger(f'stock-{self.ticker}', log_level)

        self._ohlc_tsdb = OHLC(ticker, date_start, date_end, self.config)

    def load_data(self):

        self._ohlc_tsdb.load_data()
        self._ohlc_tsdb.snip_dates()
        self._ohlc_tsdb.calc_pct_ret()

        self._trade_log = TradeLog(self.ticker, self.config, 
                    self._ohlc_tsdb.ohlc.index[0])
        self.logger.debug(f'Loaded OHLC TSDB')
        
    def log_trade(self, trade_date, shares, trade_cost):

        if trade_date not in self._ohlc_tsdb.ohlc.index:
            raise Exception(f'{trade_date} not in time series')

        self._trade_log.log_trade(trade_date, shares, trade_cost)

    def usd_position(self, trade_date=None):

        return self._trade_log.usd_position(trade_date)

    def shares_held(self, trade_date=None):

        return self._trade_log.shares_held(trade_date)
        
    @property
    def ohlc(self):
        return self._ohlc_tsdb.ohlc

    @property
    def trade_log(self):
        return self._trade_log.trade_log

class OHLC:

    def __init__(self, ticker, date_start, date_end, config):
        self.ticker = ticker
        self.config = config
        self.date_start = date_start
        self.date_end = date_end
        self.ohlc = None

    def load_data(self):
        self.ohlc = pd.read_hdf('~/tick_data/ohlc.h5', key=f'/{self.ticker}')

    def snip_dates(self):
        self.ohlc = self.ohlc.loc[self.date_start:self.date_end]

    def calc_pct_ret(self):
        col_name = self.config['data_map'].get('spot_quote_col', 'close')
        self.ohlc['pct_ret'] = self.ohlc[col_name].pct_change()

class TradeLog:

    def __init__(self, ticker, config, tl_index):

        self.ticker = ticker
        self.config = config

        self.trade_log = pd.DataFrame(index=[tl_index,], dtype='float64')
        self.trade_log['shares'] = 0            # shares held
        self.trade_log['trade_cost'] = 0        # total cost of trade

    def log_trade(self, trade_date, shares, trade_cost):

        trade_cost = round(trade_cost, 2)
        self.trade_log.loc[trade_date, ['shares', 'trade_cost']] = [shares, trade_cost]

    def usd_position(self, trade_date=None):

        if not trade_date:
            trade_date = self.trade_log.index[-1]
        usd = self.trade_log['trade_cost'].loc[:trade_date].sum()
        return round(usd, 2)

    def shares_held(self, trade_date=None):

        if not trade_date:
            trade_date = self.trade_log.index[-1]
        return self.trade_log['shares'].loc[:trade_date].sum()
