# stockplot.py

import matplotlib.pyplot as plt
from matplotlib.dates import MonthLocator


class StockPlot:

    price_col = 'adj_close'

    def __init__(self, stock_obj):
        self.symbol = stock_obj.symbol
        self.tsdb   = stock_obj.tsdb
        self.signal = stock_obj.signal

    def plot_results(self, *args, **kwargs):
        strategy_name = kwargs.get('strategy_name')

        # Plot price and 
        fig, ax = plt.subplots(2, figsize=(24, 20))
        fig.suptitle(strategy_name.upper())

        self.tsdb[self.price_col].plot(ax=ax[0])
        self.tsdb[strategy_name].plot(ax=ax[0])

        ax[0].legend(prop={'size':20})
        ax[0].tick_params(axis='both', which='major', labelsize=20)
        ax[0].xaxis.set_major_locator(MonthLocator())

        # Plot histogram
        self.tsdb['histogram'].plot(ax=ax[1], color='green')
        ax[1].legend(prop={'size': 20})
        ax[1].axhline(y=0, color='r')
        ax[1].tick_params(axis='both', which='major', labelsize=20)
        ax[1].xaxis.set_major_locator(MonthLocator())

        # Plot buy/sell signals on price & histo plots
        ax[0].plot( 
                self.signal.loc[self.signal == -1].index,
                self.tsdb[self.price_col][self.signal == -1],
                '^', markersize=10, color='green')
        ax[0].plot( 
                self.signal.loc[self.signal == 1].index,
                self.tsdb[self.price_col][self.signal == 1],
                '^', markersize=10, color='red')
        ax[1].plot( 
                self.signal.loc[self.signal == -1].index,
                self.tsdb['histogram'][self.signal == -1],
                '^', markersize=10, color='green')
        ax[1].plot( 
                self.signal.loc[self.signal == 1].index,
                self.tsdb['histogram'][self.signal == 1],
                '^', markersize=10, color='red')
