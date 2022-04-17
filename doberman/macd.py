# macd.py
from .doberlog import get_logger


class MACD:
    
    CLOSE = 'close'

    def __init__(self, stock_obj, *args, **kwargs):

        self.stock_obj  = stock_obj
        self.name       = 'macd'

        log_level = self.stock_obj.config['logging']['log_level']
        self.logger = get_logger(f'ema-{self.stock_obj.symbol}', log_level)

        self.macd_config    = self.stock_obj.config['strategy']['macd']
        self.macd_fast      = self.macd_config.get('macd_fast', 12)
        self.macd_slow      = self.macd_config.get('macd_slow', 26)
        self.macd_sig       = self.macd_config.get('macd_sig', 9)
        self.histogram_max  = self.macd_config.get('histogram_max', 1)
        self.histogram_min  = self.macd_config.get('histogram_min', -1)
        self.buy_count_max  = self.macd_config.get('buy_count_max', 3)
        self.sell_count_max = self.macd_config.get('sell_count_max', 3)

        self._calc_macd()
        self._calc_signal()

    def _calc_macd(self):

        self.stock_obj.tsdb['macd_fast'] = self.stock_obj.tsdb[self.CLOSE].ewm(span=self.macd_fast).mean()
        self.stock_obj.tsdb['macd_slow'] = self.stock_obj.tsdb[self.CLOSE].ewm(span=self.macd_slow).mean()
        self.stock_obj.tsdb['macd']      = self.stock_obj.tsdb['macd_fast'] - self.stock_obj.tsdb['macd_slow']

        self.stock_obj.tsdb['macd_sig']  = self.stock_obj.tsdb['macd'].ewm(span=self.macd_sig).mean()
        self.stock_obj.tsdb['histogram'] = self.stock_obj.tsdb['macd'] - self.stock_obj.tsdb['macd_sig']
        self.logger.info(f'{self.stock_obj.symbol.upper()}: MACD calculated')

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

        self.logger.info(f'{self.stock_obj.symbol.upper()}: Signal calculated')
