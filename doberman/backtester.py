# backtester.py

import logging
import math

logger = logging.getLogger()


class BackTester:

    def __init__(self, stock_obj):
        
        self.stock_obj = stock_obj

        self.spot_col = stock_obj.config['data_map'].get('column_name', 'close')
        self.risk_limit = self.stock_obj.config['strategy'].get('max_position_risk', 10000)


    def _risk_check(self, signal, trade_date, spot_price):
        """
        Return number of shares allowed to be traded based on held shares
        or risk parameters.
        """
        position_risk = self.stock_obj.shares_held(trade_date) * spot_price 
        risk_allowed = self.risk_limit - abs(position_risk)

        if signal == 'buy' and risk_allowed > 0:
            trade_size = self._calc_trade_size(risk_allowed, spot_price)
        elif signal == 'sell':
            # dump entire position
            trade_size = int(self.stock_obj.shares_held(trade_date))
        else:
            trade_size = 0
        
        td_str = str(trade_date)[:10]
        if trade_size != 0:
            logger.debug(f'Risk Check ({td_str}) allows {signal.upper()} '
                        + f'{trade_size} @ ${spot_price:0.2f}')
        else:
            logger.debug(f'Risk check ({td_str}) allows {signal.upper()} 0 shares.')
            
        return trade_size


    def _calc_trade_size(self, risk_allowed, spot_price):
        return math.floor(risk_allowed / spot_price)


    def backtest(self, signal_name):
        
        signal = self.stock_obj.signal[signal_name].signal

        for trade_dt in self.stock_obj.ohlc[self.spot_col].index:

            spot_price = round(self.stock_obj.ohlc[self.spot_col].loc[trade_dt], 2)

            if signal[trade_dt] <= -1:          # Buy Stock
                trade_limit = self._risk_check('buy', trade_dt, spot_price)
                trade_cost = trade_limit * spot_price
                if abs(trade_limit) > 0:
                    self.stock_obj.log_trade(trade_dt, 'buy', trade_limit, trade_cost)

            elif signal[trade_dt] >= 1:         # Sell Stock
                trade_limit = self._risk_check('sell', trade_dt, spot_price)
                trade_cost = trade_limit * spot_price
                if abs(trade_limit) > 0:
                    self.stock_obj.log_trade(trade_dt, 'sell', trade_limit, trade_cost)