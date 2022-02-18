# ema.py
import sys


class EMA:

    CLOSE = 'close'

    def __init__(self, stock_obj, *args, **kwargs):
        self.stock_obj      = stock_obj
        self.ema_window     = kwargs.get('ema_window', 30)
        self.histogram_min  = kwargs.get('histgoram_min', -3)
        self.histogram_max  = kwargs.get('histgoram_max', 3)

        self._calc_ema()
        self._calc_signal()

    def _calc_ema(self):
        self.stock_obj.tsdb['ema'] = self.stock_obj.tsdb[self.CLOSE].ewm(span=self.ema_window).mean()
        self.stock_obj.tsdb['histogram'] = self.stock_obj.tsdb[self.CLOSE] - self.stock_obj.tsdb['ema']

    def _calc_signal(self):

        buy_count = 0
        sell_count = 0
        
        for trade_date in self.stock_obj.tsdb.index:

            if self.stock_obj.tsdb['histogram'].loc[trade_date] > self.histogram_max:

                sell_count += 1
                if sell_count >= 3:
                    self.stock_obj.signal.loc[trade_date] = 1
                    sell_count = 0

            elif self.stock_obj.tsdb['histogram'].loc[trade_date] < self.histogram_min:

                buy_count += 1
                if buy_count >= 3:
                    self.stock_obj.signal.loc[trade_date] = -1
                    buy_count = 0
    
            else:
               self.stock_obj.signal.loc[trade_date] = 0
