# strategy.py
from abc import ABC, abstractmethod
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

class Strategy(ABC):

    @abstractmethod
    def create_factors(self):
        pass

    @abstractmethod
    def create_signal(self):
        pass

class EMA(Strategy):

    def __init__(self, stock_obj):


        self.stock_obj = stock_obj
        self.signal_df = pd.DataFrame(index=self.stock_obj.ohlc.index, dtype='float64')

        self.create_factors()
        self.create_signal()

    def create_factors(self):
        self.signal_df['ema'] = self.stock_obj.ohlc['close'].ewm(span=30).mean()
        self.signal_df['histogram'] = self.stock_obj.ohlc['close'] - self.signal_df['ema']
        self.signal_df['hist_norm'] = ((self.signal_df['histogram'] - self.signal_df['histogram'].min()) 
                            / (self.signal_df['histogram'].max() - self.signal_df['histogram'].min()))
        logger.debug(f'Computed EMA factors for {self.stock_obj.ticker}')

    def create_signal(self):
        hi_mark = self.stock_obj.config['strategy']['ema']['hist_hi']
        lo_mark = self.stock_obj.config['strategy']['ema']['hist_lo']

        self.signal_df['signal'] = 0
        self.signal_df.loc[self.signal_df['hist_norm'] < lo_mark, 'signal'] = -1
        self.signal_df.loc[self.signal_df['hist_norm'] > hi_mark, 'signal'] = 1
        logger.debug(f'Computed EMA signal for {self.stock_obj.ticker}')
        
class MACD(Strategy):

    # This needs to be updated and fixed.

    def __init__(self, stock_obj):
        self.stock_obj = stock_obj
        self.signal_df = pd.DataFrame(index=self.stock_obj.ohlc.index, dtype='float64')

        self.create_factors()
        self.create_signal()

    def create_factors(self):
        self.signal_df['macd_fast'] = self.stock_obj.ohlc['close'].ewm(span=12).mean()
        self.signal_df['macd_slow'] = self.stock_obj.ohlc['close'].ewm(span=26).mean()
        self.signal_df['macd']      = self.signal_df['macd_fast'] - self.signal_df['macd_slow']
        self.signal_df['macd_sig']  = self.signal_df['macd'].ewm(span=9).mean()
        self.signal_df['histogram'] = self.signal_df['macd'] - self.signal_df['macd_sig']
        logger.debug(f'Computed MACD factors for {self.stock_obj.ticker}')

        
    def create_signal(self):
        hi_mark = self.stock_obj.config['strategy']['macd']['hist_hi']
        lo_mark = self.stock_obj.config['strategy']['macd']['hist_lo']
        self.signal_df['signal'] = np.where(self.signal_df['histogram'] >= hi_mark, -1.0, 0.0)
        self.signal_df['signal'] = np.where(self.signal_df['histogram'] <= lo_mark, 1.0, 0.0)
        logger.debug(f'Computed MACD signal for {self.stock_obj.ticker}')

class StrategyFactory:

    strategies = {
                'ema': EMA,
                'macd': MACD
            }

    def __init__(self, stock_obj, strategy_name):

        self.stock_obj = stock_obj
        log_level = self.stock_obj.config['logging'].get('log_level', 'ERROR')
        logger.setLevel(log_level.upper())
        logger.debug(f'Selected strategy {strategy_name.upper()}')

        try:
            func = self.strategies[strategy_name]
            strategy_obj = func(stock_obj)
        except KeyError:
            raise AssertionError("Strategy non-existant")

        self.stock_obj.signal[strategy_name] = strategy_obj.signal_df