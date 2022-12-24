# backtester.py
import logging
import math

logger = logging.getLogger(__name__)

class BackTester:

    def __init__(self, stock_obj):
        
        self.stock_obj = stock_obj

        log_level = self.stock_obj.config['logging'].get('log_level', 'ERROR')
        logger.setLevel(log_level.upper())
        
        self.spot_col = stock_obj.config['data_map'].get('column_name', 'close')
        self.risk_limit = self.stock_obj.config['strategy'].get('max_position_risk', 10000)

    def _risk_check(self, signal, trade_date, spot_price):
        position_risk = self.stock_obj.shares_held(trade_date) * spot_price 
        risk_allowed = self.risk_limit - abs(position_risk)

        if signal == 'buy' and risk_allowed > 0:
            trade_size = self._calc_trade_size(risk_allowed, spot_price)
        elif signal == 'sell':
            # dump entire position
            trade_size = self.stock_obj.shares_held(risk_allowed, spot_price)
        return trade_size

    def _calc_trade_size(self, risk_allowed, spot_price):
        return math.floor(risk_allowed / spot_price)

    def backtest(self, signal_name):
        
        signal = self.stock_obj.signal[signal_name].signal

        for trade_dt in self.stock_obj.ohlc[self.spot_col].index:

            spot_price = self.stock_obj.ohlc[self.spot_col].loc[trade_dt]

            if signal[trade_dt] <= -1:          # Buy Stock
                trade_limit = self._risk_check('buy', trade_dt, spot_price)
                self.stock_obj.log_trade(trade_dt, trade_limit, spot_price)
                logger.debug(f'Purchase {self.stock_obj.ticker} {trade_limit}@{spot_price}')

            elif signal[trade_dt] >= 1:         # Sell Stock
                trade_limit = self._risk_check('buy', trade_dt, spot_price)
                self.stock_obj.log_trade(trade_dt, (trade_limit * -1), spot_price)
                logger.debug(f'Sell {self.stock_obj.ticker} {trade_limit}@{spot_price}')