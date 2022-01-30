# macd.py
import matplotlib.pyplot as plt
from matplotlib.dates import MonthLocator
from .utils import iterate_stocks as iterate_stocks


class MACD:

    def __init__(self, universe, *args, **kwargs):
        self.universe   = universe
        self.macd_fast  = kwargs.get('macd_fast', 12)
        self.macd_slow  = kwargs.get('macd_slow', 26)
        self.macd_sig   = kwargs.get('macd_sig', 9)

        self.hist_max   = kwargs.get('hist_max', 1)
        self.hist_min   = kwargs.get('hist_min', -1)

        self._calc_macd()
        self._calc_signal()

    @iterate_stocks
    def _calc_macd(self, stock_obj):
        stock_obj.tsdb['macd_fast'] = stock_obj.tsdb['adj_close'].ewm(span=self.macd_fast).mean()
        stock_obj.tsdb['macd_slow'] = stock_obj.tsdb['adj_close'].ewm(span=self.macd_slow).mean()
        stock_obj.tsdb['macd']      = stock_obj.tsdb['macd_fast'] - stock_obj.tsdb['macd_slow']

        stock_obj.tsdb['macd_sig']  = stock_obj.tsdb['macd'].ewm(span=self.macd_sig).mean()
        stock_obj.tsdb['macd_hist'] = stock_obj.tsdb['macd'] - stock_obj.tsdb['macd_sig']

    def _signal_test(self, row):
        if row.macd_hist > self.hist_max:
            return 1
        elif row.macd_hist < self.hist_min:
            return -1
        else:
            return 0

    @iterate_stocks
    def _calc_signal(self, stock_obj):
        stock_obj.signal = stock_obj.tsdb.apply(lambda row: self._signal_test(row), axis=1)

    def plot_results(self, sym):
        # plot price and MAs
        fig, ax = plt.subplots(2, figsize=(20, 18))
        fig.suptitle('Moving Avg Convergence/Divergence')
        self.universe.stocks[sym].tsdb['adj_close'].plot(ax=ax[0], linewidth=3)
        self.universe.stocks[sym].tsdb['macd_fast'].plot(ax=ax[0], linewidth=2)
        self.universe.stocks[sym].tsdb['macd_slow'].plot(ax=ax[0], linewidth=2)
        ax[0].tick_params(axis='both', which='major', labelsize=20)
        ax[0].legend(prop={'size': 18})
        ax[0].xaxis.set_major_locator(MonthLocator())
        # plot MACD sig/histogram
        self.universe.stocks[sym].tsdb['macd'].plot(ax=ax[1])
        self.universe.stocks[sym].tsdb['macd_sig'].plot(ax=ax[1])
        self.universe.stocks[sym].tsdb['macd_hist'].plot(ax=ax[1], linewidth=4, linestyle='dashed')
        ax[1].tick_params(axis='both', which='major', labelsize=20)
        ax[1].legend(prop={'size': 18})
        ax[1].xaxis.set_major_locator(MonthLocator())
        ax[1].tick_params(axis='both', which='major', labelsize=20)
        ax[1].axhline(y=0, color='r')
   

