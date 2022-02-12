# macd.py


class MACD:

    def __init__(self, stock_obj, *args, **kwargs):
        self.stock_obj  = stock_obj
        self.macd_fast  = kwargs.get('macd_fast', 12)
        self.macd_slow  = kwargs.get('macd_slow', 26)
        self.macd_sig   = kwargs.get('macd_sig', 9)

        self.hist_max   = kwargs.get('hist_max', 1)
        self.hist_min   = kwargs.get('hist_min', -1)

        self._calc_macd()
        self._calc_signal()

    def _calc_macd(self):
        self.stock_obj.tsdb['macd_fast'] = self.stock_obj.tsdb['adj_close'].ewm(span=self.macd_fast).mean()
        self.stock_obj.tsdb['macd_slow'] = self.stock_obj.tsdb['adj_close'].ewm(span=self.macd_slow).mean()
        self.stock_obj.tsdb['macd']      = self.stock_obj.tsdb['macd_fast'] - self.stock_obj.tsdb['macd_slow']

        self.stock_obj.tsdb['macd_sig']  = self.stock_obj.tsdb['macd'].ewm(span=self.macd_sig).mean()
        self.stock_obj.tsdb['macd_hist'] = self.stock_obj.tsdb['macd'] - self.stock_obj.tsdb['macd_sig']

    def _signal_test(self, row):
        if row.macd_hist > self.hist_max:
            return 1
        elif row.macd_hist < self.hist_min:
            return -1
        else:
            return 0

    def _calc_signal(self):
        self.stock_obj.signal = self.stock_obj.tsdb.apply(lambda row: self._signal_test(row), axis=1)
