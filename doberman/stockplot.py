# stockplot.py

import matplotlib.pyplot as plt
from matplotlib.dates import MonthLocator


class StockPlot:

    price_col = 'adj_close'

    def __init__(self, stock_obj):
        self.symbol = stock_obj.symbol
        self.tsdb   = stock_obj.tsdb

    def plot_signal(self, *args, **kwargs):
        signal_name = kwargs.get(signal_name, '')

        fig, ax = plt.subplots(1, figsize=(24, 20))
        fig.suptitle(f'Signal {signal_name}')

        self.tsdb[self.price_col].plot(ax=ax[0])
        self.tsdb['signal'].plot(ax=ax[0])
         
        ax[0].tick_params(axis='both', which='major', labelsize=20)
        ax[0].legend(prop={'size':20})
        ax[0].xaxis.set_major_locator(MonthLocator())

    def plot_ema(self, *args, **kwargs):

        fig, ax = plt.subplots(2, figsize=(24, 20))
        fig.suptitle('Exponetial Moving Avg')

        self.tsdb[self.price_col].plot(ax=ax[0])
        self.tsdb['ema'].plot(ax=ax[0])
         
        ax[0].tick_params(axis='both', which='major', labelsize=20)
        ax[0].legend(prop={'size':20})
        ax[0].xaxis.set_major_locator(MonthLocator())

        # Plot histogram
        self.tsdb['histogram'].plot(ax=ax[1])
        ax[1].legend(prop={'size': 20})
        ax[1].xaxis.set_major_locator(MonthLocator())
        ax[1].tick_params(axis='both', which='major', labelsize=20)
        ax[1].axhline(y=0, color='r')
