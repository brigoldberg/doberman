# ema.py
import sys


class EMA:

    CLOSE = 'close'

    def __init__(self, stock_obj, *args, **kwargs):

        self.stock_obj = stock_obj
        self.name = 'ema'

        self.ema_config     = self.stock_obj.config['strategy']['ema']
        self.ema_window     = self.ema_config.get('ema_window', 30)
        self.histogram_min  = self.ema_config.get('histgoram_min', -2)
        self.histogram_max  = self.ema_config.get('histgoram_max', 2)
        self.buy_count_max  = self.ema_config.get('buy_count_max', 2)
        self.sell_count_max = self.ema_config.get('sell_count_max', 2)

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
                if sell_count >= self.sell_count_max:
                    self.stock_obj.signal.loc[trade_date] = 1
                    sell_count = 0

            elif self.stock_obj.tsdb['histogram'].loc[trade_date] < self.histogram_min:

                buy_count += 1
                if buy_count >= self.buy_count_max:
                    self.stock_obj.signal.loc[trade_date] = -1
                    buy_count = 0
    
            else:
               self.stock_obj.signal.loc[trade_date] = 0
