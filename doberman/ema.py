import matplotlib.pyplot as plt
from matplotlib.dates import MonthLocator
from .utils import iterate_stocks as iterate_stocks


class EMA():

    def __init__(self, universe, *args, **kwargs):
        self.universe       = universe
        self.ema_window     = kwargs.get('ema_window', 30)
        self.histogram_min  = kwargs.get('histgoram_min', -3)
        self.histogram_max  = kwargs.get('histgoram_max', 3)

        self._calc_ema()
        self._calc_signal()

    @iterate_stocks
    def _calc_ema(self, stock_obj):
        stock_obj.tsdb['ema'] = stock_obj.tsdb['adj_close'].ewm(span=self.ema_window).mean()
        stock_obj.tsdb['histogram'] = stock_obj.tsdb['adj_close'] - stock_obj.tsdb['ema']

    def _signal_test(self, row):
        if row.histogram > self.histogram_max:
            return 1
        elif row.histogram < self.histogram_min:
            return -1
        else:
            return 0

    @iterate_stocks
    def _calc_signal(self, stock_obj):
        stock_obj.signal = stock_obj.tsdb.apply(lambda row: self._signal_test(row), axis=1)

    def plot_results(self, ticker_name):
        # Plot price and EMA
        fig, ax = plt.subplots(2, figsize=(24, 20))
        fig.suptitle('Exponetial Moving Avg')
        self.universe.stocks[ticker_name].tsdb['adj_close'].plot(ax=ax[0])
        self.universe.stocks[ticker_name].tsdb['ema'].plot(ax=ax[0])
        ax[0].tick_params(axis='both', which='major', labelsize=20)
        ax[0].legend()
        ax[0].xaxis.set_major_locator(MonthLocator())
        # Plot histogram
        self.universe.stocks[ticker_name].tsdb['histogram'].plot(ax=ax[1])
        ax[1].legend()
        ax[1].xaxis.set_major_locator(MonthLocator())
        ax[1].tick_params(axis='both', which='major', labelsize=20)
        ax[1].axhline(y=0, color='r')
