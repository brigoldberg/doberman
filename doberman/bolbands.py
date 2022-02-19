# bolbands.py
import sys


class BolBands:

    CLOSE = 'close'

    def __init__(self, stock_obj, *args, **kwargs):
        self.stock_obj  = stock_obj
        self.ma_window  = kwargs.get('ema_window', 30)
        self.n          = kwargs.get('std_dev', 2)

        self._calc_bolbands()
        self._calc_signal()

    def _calc_bolbands(self):
        self.stock_obj.tsdb['std_dev'] = self.stock_obj.tsdb['close'].rolling(20).std(ddof=0)
        self.stock_obj.tsdb['ma']      = self.stock_obj.tsdb['close'].rolling(20).mean()
        self.stock_obj.tsdb['bol_hi']  = self.stock_obj.tsdb['ma'] + self.n * self.stock_obj.tsdb['std_dev']
        self.stock_obj.tsdb['bol_lo']  = self.stock_obj.tsdb['ma'] - self.n * self.stock_obj.tsdb['std_dev']

    def _calc_signal(self):

        buy_count  = 0
        sell_count = 0

        for trade_date in self.stock_obj.tsdb.index:

            if self.stock_obj.tsdb['close'].loc[trade_date] > self.stock_obj.tsdb['bol_hi'].loc[trade_date]:
                # sell signal
                sell_count += 1
                if sell_count >= 3:
                    self.stock_obj.signal.loc[trade_date] = 1
                    sell_count = 0

            elif self.stock_obj.tsdb['close'].loc[trade_date] < self.stock_obj.tsdb['bol_lo'].loc[trade_date]:
                # buy signal 
                buy_count += 1
                if buy_count >= 2:
                    self.stock_obj.signal.loc[trade_date] = -1
                    buy_count = 0

            else:
                self.stock_obj.signal.loc[trade_date] = 0
                
