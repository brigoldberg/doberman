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
        fig = plt.figure(figsize=(18, 10))
        #fig.suptitle('Price/Vol')
        ax1 = plt.subplot2grid((3,3), (0,0), colspan=3, rowspan=2)
        ax2 = plt.subplot2grid((3,3), (2,0), colspan=3, rowspan=1)

        if strategy_name == 'ema':
            ax1.plot(self.tsdb['ema'])
        elif strategy_name == 'macd':
            ax1.plot(self.tsdb['macd_fast'])
            ax1.plot(self.tsdb['macd_slow'])
        elif strategy_name == 'bolbands':
            ax1.plot(self.tsdb['ma'])
            ax1.plot(self.tsdb['bol_hi'])
            ax1.plot(self.tsdb['bol_lo'])

        ax1.set_title('Closing Price')
        ax2.set_title('Volume')
        ax1.plot(self.tsdb.close)
        ax2.bar(self.tsdb.index, self.tsdb['volume'])

        ax1.set_ylabel('Closing Price')
        ax2.set_ylabel('Volume')

        #ax2.legend(prop={'size':20})
        #ax2.tick_params(axis='both', which='major', labelsize=10)
        #ax2.xaxis.set_major_locator(MonthLocator(interval=1))
        #ax2.xaxis.set_major_formatter(DateFormatter("%b %Y"))

        # Plot buy/sell signals on price
        ax1.plot( 
                self.signal.loc[self.signal == -1].index,
                self.tsdb[self.price_col][self.signal == -1],
                '^', markersize=10, color='green')
        ax1.plot( 
                self.signal.loc[self.signal == 1].index,
                self.tsdb[self.price_col][self.signal == 1],
                'v', markersize=10, color='red')

        plt.show()

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

