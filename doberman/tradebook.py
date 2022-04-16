# tradebook.py

import os
import sys
import pandas as pd


class TradeBook:

    TICK_DS = os.path.expanduser('~/tick_data/ohlc.h5')
    CLOSE = 'close'

    def __init__(self, *args, **kwargs):

        self.cash_init  = kwargs.get('cash_init', 10000)
        self.book       = {'cash-usd': self.cash_init}
        self.tick_ds    = kwargs.get('tick_ds', self.TICK_DS)
        self.risk_limit = kwargs.get('risk_limit', 1000)
        self.trade_log  = []

    def log_trade(self, log_entry):
        self.trade_log.append(log_entry)

    def update_book(self, symbol, shares):
        """
        Update or add with traded symbol and shares
        """
        if symbol not in self.book:
            self.book[symbol] = shares
        else:
            self.book[symbol] = self.book[symbol] + shares

    def get_stock_price(self, symbol, trade_date):
        """
        Input symbol and trade date.
        Return stock price.
        """
        hdf = pd.HDFStore(self.tick_ds, mode='r')
        stock_price = hdf[symbol][self.CLOSE].loc[trade_date]
        hdf.close()
        return stock_price

    def calc_position_size(self, symbol, trade_date):
        """
        Input symbol and date
        Return cash value of all shares in book baseded on the
        price of that day.
        """
        stock_price = self.get_stock_price(symbol, trade_date)
        position_size = stock_price * self.book[symbol]
        return position_size

    def calc_book_value(self, trade_date):
        """
        Input trade date.
        Return cash value of all stocks in the book plus held cash.
        """
        book_value = 0
        for key in self.book.keys():
            if key != 'cash-usd':
                pos_size = self.calc_position_size(key, trade_date)
                book_value += pos_size

        book_value += self.book['cash-usd']

        return book_value

    def calc_book_pnl(self, trade_date):

        book_pnl = self.calc_book_value(trade_date) - self.cash_init
        return book_pnl


    def trade_risk_check(self, symbol, trade_date):
        '''
        Get current cash value of stock position. If dollar value is
        greater than risk limit (eg: $10,000), do not buy any more stock.
        '''
        # Return true if no key. That means we don't own the stock and 
        # therefore there is no risk to starting a new position.
        if not symbol in self.book:       
            return True
        # We do own some of the stock, so we must perform a risk check.
        if self.calc_position_size(symbol, trade_date) > self.risk_limit:
            return False
        else:
            return True
