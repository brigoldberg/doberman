# simulation.py

import math
from .tradebook import TradeBook as TradeBook

class Simulation:

    CLOSE = 'close'

    def __init__(self, stock_obj, *args, **kwargs):
        self.stock_obj = stock_obj
        self.hi_signal = kwargs.get('hi_signal', 1)
        self.lo_signal = kwargs.get('lo_signal', -1)
        self.tradebook = TradeBook()

    def paper_trade(self):

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
                self.tradebook.log_trade(f'{[trade_date]} BUY {trade_quantity} {symbol}@{price}')

            elif signal >= self.hi_signal and position_size >= 10:      # Sell signal
                
                trade_revenue = price * position_size
                self.tradebook.update_book(symbol, (position_size * -1))
                self.tradebook.update_book('cash-usd', trade_revenue)
                self.tradebook.log_trade(f'{[trade_date]} SELL {position_size} {symbol}@{price}')

    def calc_pnl(self, *args, **kwargs):

        trade_date = kwargs.get('trade_date', self.stock_obj.tsdb.index[-1])
        '''
        Return cash value of all portfolio holding.  This sums up the entire portfolio
        no matter what date you provide, ergo, only use the last trading date.
        '''
        cash_value = 0
        for k,v in self.tradebook.book.items():
            if k == 'cash-usd':
                cash_value += v
            else:
                cash_value += self.tradebook.calc_position_size(k, trade_date)

        print(f"{self.stock_obj.symbol} simulation PnL: ${cash_value:,.0f}")

