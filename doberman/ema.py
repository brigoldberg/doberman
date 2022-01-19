import matplotlib.pyplot as plt
from matplotlib.dates import MonthLocator
from .strategy import Strategy as Strategy
from .utils import iterate_stocks as iterate_stocks


class EMA(Strategy):

    start_cash = 10000

    def __init__(self, universe, *args, **kwargs):
        super().__init__(universe)
        self.universe       = universe
        self.ema_window     = kwargs.get('ema_window', 30)
        self.histogram_min  = -1
        self.histogram_max  = 1

        self._calc_ema()
        self._calc_signal()
        self._paper_trade()

    @iterate_stocks
    def _calc_ema(self, stock_obj):
        stock_obj.tsdb['ema'] = stock_obj.tsdb[self.ohlc_col].ewm(span=self.ema_window).mean()
        stock_obj.tsdb['histogram'] = stock_obj.tsdb[self.ohlc_col] - stock_obj.tsdb['ema']

    def _signal_test(self, row):
        if row.histogram > self.histogram_max:
            return 1
        elif row.histogram < self.histogram_min:
            return -1
        else:
            return 0

    @iterate_stocks
    def _calc_signal(self, stock_obj):
        stock_obj.signal['signal'] = stock_obj.tsdb.apply(lambda row: self._signal_test(row), axis=1)

    def plot_results(self, ticker_name):
       fig, ax = plt.subplots(2, 1, figsize=(24, 20), sharex=True)
       self.universe.stocks[ticker_name].tsdb['adj_close'].plot(ax=ax[0])
       self.universe.stocks[ticker_name].tsdb['ema'].plot(ax=ax[0])
       ax[0].legend()
       ax[0].xaxis.set_major_locator(MonthLocator())
       self.universe.stocks[ticker_name].tsdb['histogram'].plot(ax=ax[1], kind='bar', color='b')
       ax[1].legend()
       ax[1].xaxis.set_major_locator(MonthLocator())
