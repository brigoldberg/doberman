# stock.py
import logging
import pandas as pd
from .utils import read_config

logger = logging.getLogger()

class Stock:

    def __init__(self, ticker, date_start, date_end, **kwargs):

        _config =  kwargs.get('config', {})
        if type(_config) is not dict:
            self.config = read_config(_config)
        else:
            self.config = _config

        self.ticker = ticker
        self.signal = {}
        self._ohlc_tsdb = OHLC(ticker, date_start, date_end, self.config)

    def load_data(self):

        self._ohlc_tsdb.load_data()
        self._ohlc_tsdb.snip_dates()
        self._ohlc_tsdb.calc_pct_ret()

        self._trade_log = TradeLog(self.ticker, self.config, 
                    self._ohlc_tsdb.ohlc.index[0])
        
    def log_trade(self, trade_date, order_type, shares, trade_cost):

        if trade_date not in self._ohlc_tsdb.ohlc.index:
            raise Exception(f'{trade_date} not in time series')

        self._trade_log.log_trade(trade_date, order_type, shares, trade_cost)
        logger.debug(f'Trade logged: {trade_date.strftime("%Y-%m-%d")} {self.ticker.upper()} {order_type} {shares} @ ${round(trade_cost, 2)}')

    def usd_position(self, trade_date=None):
        return self._trade_log.usd_position(trade_date)

    def shares_held(self, trade_date=None):
        return self._trade_log.shares_held(trade_date)

    def position_value(self, trade_date=None):
        pv = self.shares_held(trade_date)  * self.spot_price(trade_date) \
                + self.usd_position(trade_date) 
        return pv

    def max_drawdown(self, trade_date=None):
        return self._trade_log.max_drawdown(trade_date)

    def spot_price(self, trade_date=None, col='close'):
        if not trade_date:
            trade_date = self.trade_log.index[-1]

        if trade_date not in self._ohlc_tsdb.ohlc.index:
            #raise Exception(f'{trade_date} not in time series')
            logger.error(f'{self.ticker.upper()} {trade_date} not in time series')

        return self.ohlc.loc[trade_date][col]

    def rate_of_return(self, trade_date=None):
        if not trade_date:
            trade_date = self.ohlc.index[-1]
        
        share_value = self.shares_held(trade_date) * self.spot_price(trade_date) 
        present_value = share_value + self.usd_position(trade_date)
        ror = present_value / abs(self.max_drawdown(trade_date))

        return ror
        
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
        hdf_fn = self.config['data_source'].get('hdf5_file')
        try:
            self.ohlc = pd.read_hdf(hdf_fn, key=f'/{self.ticker}')
        except:
            raise Exception(f'Cannot load data for {self.ticker.upper()}')
        logger.info(f'Loaded dataframe for {self.ticker.upper()}')

    def snip_dates(self):
        try:
            self.ohlc = self.ohlc.loc[self.date_start:self.date_end]
        except:
            raise Exception(f'Cannot snip dates for f{self.ticker.upper()}')
        logger.info(f'Snipped dates for {self.ticker.upper()}')

    def calc_pct_ret(self):
        col_name = self.config['data_map'].get('spot_quote_col', 'close')
        self.ohlc['pct_ret'] = self.ohlc[col_name].pct_change()
        logger.info(f'Calculated pct return for {self.ticker.upper()}')

class TradeLog:

    def __init__(self, ticker, config, tl_index):

        self.ticker = ticker
        self.config = config

        self.trade_log = pd.DataFrame(index=[tl_index,], dtype='float64')
        self.trade_log['shares'] = 0            # shares held
        self.trade_log['order_type'] = None
        self.trade_log['trade_cost'] = 0        # total cost of trade

    def log_trade(self, trade_date, order_type, shares, trade_cost):

        trade_cost = round((trade_cost), 2)

        if order_type == 'buy':
            trade_cost = trade_cost * -1
        elif order_type == 'sell':
            shares = shares * -1

        self.trade_log.loc[trade_date, ['shares', 'order_type', 'trade_cost']] = [shares, order_type, trade_cost]
        logger.debug(f'Trade logged: {trade_date.strftime("%Y-%m-%d")} {self.ticker.upper()} {order_type} {shares} @ ${round(trade_cost, 2)}')

    def usd_position(self, trade_date=None):

        if not trade_date:
            trade_date = self.trade_log.index[-1]
        usd = self.trade_log['trade_cost'].loc[:trade_date].sum()
        return round(usd, 2)

    def shares_held(self, trade_date=None):

        if not trade_date:
            trade_date = self.trade_log.index[-1]
        return self.trade_log['shares'].loc[:trade_date].sum()

    def max_drawdown(self, trade_date=None):

        if not trade_date:
            trade_date = self.trade_log.index[-1]
        return self.trade_log['trade_cost'].loc[:trade_date].cumsum().min()
