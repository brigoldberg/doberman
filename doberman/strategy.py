# strategy.py
from abc import ABC, abstractmethod
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger()


class Strategy(ABC):

    @abstractmethod
    def create_factors(self):
        """
        Factors are the signals that indicate when to purchase or sell
        a stock. They are typically moving window calculations or other
        technical signals.
        """
        pass


    @abstractmethod
    def create_signal(self):
        """
        Signals are the series of sentiments to purchase or sell a stock.
        They are derived from 'factors' which are calculated previously.
        
        Singal(s) are used by the backtesting module to perform a trading
        simulation over a period of time. The simulator will buy or sell
        based upon the signal value (+1/-1) and position risk.
        """ 
        pass


class BollingerBands(Strategy):
    """
    Create trendlines of two standard deviations above and below a Simple Moving
    Average. Buy signal when price crosses bottom trendline and sell when price
    crossed top trendline.
    """
    pass


class EMA(Strategy):
    """
    EMA (exponential moving average) generates a moving average over a set window.
    """
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
        logger.info(f'Computed EMA factors for {self.stock_obj.ticker}')


    def create_signal(self):
        hi_mark = self.stock_obj.config['strategy']['ema']['hist_hi']
        lo_mark = self.stock_obj.config['strategy']['ema']['hist_lo']

        self.signal_df['signal'] = 0
        self.signal_df.loc[self.signal_df['hist_norm'] < lo_mark, 'signal'] = -1
        self.signal_df.loc[self.signal_df['hist_norm'] > hi_mark, 'signal'] = 1
        logger.info(f'Computed EMA signal for {self.stock_obj.ticker}')


class MACD(Strategy):
    # This needs to be updated and fixed.
    """
    Moving Average Crossover Divergence calculates a fast and slow EMA and generates a signal
    when they cross.
    """
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
        logger.info(f'Computed MACD factors for {self.stock_obj.ticker}')

        
    def create_signal(self):
        hi_mark = self.stock_obj.config['strategy']['macd']['hist_hi']
        lo_mark = self.stock_obj.config['strategy']['macd']['hist_lo']
        self.signal_df['signal'] = np.where(self.signal_df['histogram'] >= hi_mark, -1.0, 0.0)
        self.signal_df['signal'] = np.where(self.signal_df['histogram'] <= lo_mark, 1.0, 0.0)
        logger.info(f'Computed MACD signal for {self.stock_obj.ticker}')


class StrategyFactory:
    """
    Run strategy passed as parameter to class.  Return an object containing 
    both the stock object and a dataframe of signals from specified strategy.
    """
    strategies = {
                'ema': EMA,
                'macd': MACD
            }

    def __init__(self, stock_obj, strategy_name):

        self.stock_obj = stock_obj
        log_level = self.stock_obj.config['logging'].get('log_level', 'ERROR')
        logger.setLevel(log_level.upper())
        logger.info(f'Selected strategy {strategy_name.upper()}')

        try:
            func = self.strategies[strategy_name]
            strategy_obj = func(stock_obj)
        except KeyError:
            raise AssertionError("Strategy non-existant")

        self.stock_obj.signal[strategy_name] = strategy_obj.signal_df