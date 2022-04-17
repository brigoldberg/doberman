# bolbands.py
from .doberlog import get_logger


class BolBands:

    CLOSE = 'close'

    def __init__(self, stock_obj, *args, **kwargs):

        self.stock_obj  = stock_obj
        self.name       = 'bolbands'

        log_level = self.stock_obj.config['logging']['log_level']
        self.logger = get_logger(f'ema-{self.stock_obj.symbol}', log_level)

        self.bb_cfg      = self.stock_obj.config['strategy']['bolbands']
        self.ma_window  = self.bb_cfg.get('ma_window', 30)
        self.std_devs   = self.bb_cfg.get('std_deviations', 2)
        self.buy_count_max  = self.bb_cfg.get('buy_count_max', 2)
        self.sell_count_max = self.bb_cfg.get('sell_count_max', 2)

        self._calc_bolbands()
        self._calc_signal()

    def _calc_bolbands(self):
        self.stock_obj.tsdb['std_dev'] = \
                    self.stock_obj.tsdb[self.CLOSE].rolling(self.ma_window).std(ddof=0)
        self.stock_obj.tsdb['ma']      = \
                    self.stock_obj.tsdb[self.CLOSE].rolling(self.ma_window).mean()
        self.stock_obj.tsdb['bol_hi']  = self.stock_obj.tsdb['ma'] + \
                                    self.std_devs * self.stock_obj.tsdb['std_dev']
        self.stock_obj.tsdb['bol_lo']  = self.stock_obj.tsdb['ma'] - \
                                    self.std_devs * self.stock_obj.tsdb['std_dev']

        self.logger.info(f'{self.stock_obj.symbol.upper()}: BolBands calculated')

    def _calc_signal(self):

        buy_count  = 0
        sell_count = 0

        for trade_date in self.stock_obj.tsdb.index:

            if self.stock_obj.tsdb['close'].loc[trade_date] > self.stock_obj.tsdb['bol_hi'].loc[trade_date]:
                # sell signal
                sell_count += 1
                if sell_count >= self.sell_count_max:
                    self.stock_obj.signal.loc[trade_date] = 1
                    sell_count = 0

            elif self.stock_obj.tsdb['close'].loc[trade_date] < self.stock_obj.tsdb['bol_lo'].loc[trade_date]:
                # buy signal 
                buy_count += 1
                if buy_count >= self.buy_count_max:
                    self.stock_obj.signal.loc[trade_date] = -1
                    buy_count = 0

            else:
                self.stock_obj.signal.loc[trade_date] = 0

        self.logger.info(f'{self.stock_obj.symbol.upper()}: Signal calculated')
