# doberplot.py

import matplotlib.pyplot as plt
from matplotlib.dates import MonthLocator
from matplotlib.dates import DateFormatter


class DoberPlot:

    price_col = 'close'

    def __init__(self, stock_obj):
        self.symbol = stock_obj.symbol
        self.tsdb   = stock_obj.tsdb
        self.signal = stock_obj.signal

    def order_signal(self, *args, **kwargs):
        strategy_name = kwargs.get('strategy_name')
        # Plot price 
        fig, ax = plt.subplots(figsize=(18, 10))
        fig.suptitle(strategy_name.upper())

        self.tsdb[self.price_col].plot(ax=ax)

        if strategy_name == 'ema':
            self.tsdb['ema'].plot(ax=ax)
        elif strategy_name == 'macd':
            self.tsdb['macd_fast'].plot(ax=ax)
            self.tsdb['macd_slow'].plot(ax=ax)
        elif strategy_name == 'bolbands':
            self.tsdb['ma'].plot(ax=ax)
            self.tsdb['bol_hi'].plot(ax=ax)
            self.tsdb['bol_lo'].plot(ax=ax)

        ax.legend(prop={'size':20})
        ax.tick_params(axis='both', which='major', labelsize=20)
        ax.xaxis.set_major_locator(MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(DateFormatter("%b %Y"))

        # Plot buy/sell signals on price
        ax.plot( 
                self.signal.loc[self.signal == -1].index,
                self.tsdb[self.price_col][self.signal == -1],
                '^', markersize=10, color='green')
        ax.plot( 
                self.signal.loc[self.signal == 1].index,
                self.tsdb[self.price_col][self.signal == 1],
                'v', markersize=10, color='red')

    def histogram(self, *args, **kwargs):
        strategy_name = kwargs.get('strategy_name')
        # Plot histogram
        fig, ax = plt.subplots(figsize=(18, 10))
        fig.suptitle('EMA Histogram')

        self.tsdb['histogram'].plot(ax=ax, color='green')

        if strategy_name == 'macd':
            self.tsdb['macd'].plot(ax=ax)
            self.tsdb['macd_sig'].plot(ax=ax)
 
        ax.legend(prop={'size': 20})
        ax.axhline(y=0, color='r')
        ax.tick_params(axis='both', which='major', labelsize=20)
        ax.xaxis.set_major_locator(MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(DateFormatter("%b %Y"))

        ax.plot( 
                self.signal.loc[self.signal == -1].index,
                self.tsdb['histogram'][self.signal == -1],
                '^', markersize=10, color='green')
        ax.plot( 
                self.signal.loc[self.signal == 1].index,
                self.tsdb['histogram'][self.signal == 1],
                'v', markersize=10, color='red')

