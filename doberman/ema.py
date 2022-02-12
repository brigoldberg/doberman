# ema.py


class EMA:

    def __init__(self, stock_obj, *args, **kwargs):
        self.stock_obj      = stock_obj
        self.ema_window     = kwargs.get('ema_window', 30)
        self.histogram_min  = kwargs.get('histgoram_min', -3)
        self.histogram_max  = kwargs.get('histgoram_max', 3)

        self._calc_ema()
        self._calc_signal()

    def _calc_ema(self):
        self.stock_obj.tsdb['ema'] = self.stock_obj.tsdb['adj_close'].ewm(span=self.ema_window).mean()
        self.stock_obj.tsdb['histogram'] = self.stock_obj.tsdb['adj_close'] - self.stock_obj.tsdb['ema']

    def _signal_test(self, row):
        if row.histogram > self.histogram_max:
            return 1
        elif row.histogram < self.histogram_min:
            return -1
        else:
            return 0

    def _calc_signal(self):
        self.stock_obj.signal = self.stock_obj.tsdb.apply(lambda row: self._signal_test(row), axis=1)
