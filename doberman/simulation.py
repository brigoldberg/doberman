# simulation.py
from .utils import iterate_stocks as iterate_stocks
from .tradebook import TradeBook as TradeBook


class Simulation:

    tradebook = TradeBook()

    def __init__(self, universe, *args, **kwargs):
        self.universe  = universe
        self.hi_signal = kwargs.get('hi_signal', 1)
        self.lo_signal = kwargs.get('lo_signal', -1)

    @iterate_stocks
    def paper_trade(self, stock_obj):

        for trade_date in stock_obj.signal.index:
            
            symbol = stock_obj.symbol
            price  = stock_obj.tsdb['adj_close'].loc[trade_date]
            signal = stock_obj.signal.loc[trade_date]

            long_test = self.tradebook.trade_risk_check(symbol, trade_date)
            position_size = self.tradebook.book.get(symbol, 0)

            if signal <=  self.lo_signal and long_test:     # buy signal

                trade_quantity = 100
                trade_cost = price * 100 * -1
                self.tradebook.update_book(symbol, trade_quantity)
                self.tradebook.update_book('cash-usd', trade_cost)
                self.tradebook.log_trade(f'{[trade_date]} BUY 100 {symbol}@{price}')

            elif signal >= self.hi_signal and position_size >= 10:      # Sell signal
                
                trade_revenue = price * position_size
                self.tradebook.update_book(symbol, (position_size * -1))
                self.tradebook.update_book('cash-usd', trade_revenue)
                self.tradebook.log_trade(f'{[trade_date]} SELL {position_size} {symbol}@{price}')

    def calc_pnl(self, trade_date):
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

        print(f"Simulation PnL: ${cash_value:,.0f}")
            
