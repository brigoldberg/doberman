# simulation.py

import math
from .tradebook import TradeBook 
from .doberlog import get_logger

class Simulation:

    CLOSE = 'close'

    def __init__(self, stock_obj, *args, **kwargs):

        self.stock_obj = stock_obj

        log_level = self.stock_obj.config['logging']['log_level']
        self.logger = get_logger(f'sim-{self.stock_obj.symbol}', log_level)

        self.hi_signal = kwargs.get('hi_signal', 1)
        self.lo_signal = kwargs.get('lo_signal', -1)
        self.tradebook = TradeBook()

    def paper_trade(self):
        '''
        Trade a symbol based upon its signal series data. 
        '''
        for trade_date in self.stock_obj.signal.index:

            symbol = self.stock_obj.symbol
            price  = self.stock_obj.tsdb[self.CLOSE].loc[trade_date]
            signal = self.stock_obj.signal.loc[trade_date]

            long_test = self.tradebook.trade_risk_check(symbol, trade_date)
            position_size = self.tradebook.book.get(symbol, 0)

            if signal <=  self.lo_signal and long_test:     # buy signal

                trade_quantity = math.floor(self.tradebook.risk_limit / price)
                trade_cost = price * trade_quantity * -1
                self.tradebook.update_book(symbol, trade_quantity)
                self.tradebook.update_book('cash-usd', trade_cost)
                self.tradebook.log_trade((trade_date, 'buy', trade_quantity, symbol, price))
                self.logger.debug(f'existing {symbol} position is {position_size} shares')
                self.logger.debug(f'bought {symbol} {trade_quantity} @ ${price:0.2f}')


            elif signal >= self.hi_signal and position_size >= 1:      # Sell signal
                
                trade_revenue = price * position_size
                self.tradebook.update_book(symbol, (position_size * -1))
                self.tradebook.update_book('cash-usd', trade_revenue)
                self.tradebook.log_trade((trade_date, 'sell', position_size, symbol, price))
                self.logger.debug(f'existing {symbol} position is {position_size} shares')
                self.logger.debug(f'sold {symbol} {trade_quantity} @ ${price:0.2f}')

