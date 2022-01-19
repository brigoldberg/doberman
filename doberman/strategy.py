from .utils import iterate_stocks as iterate_stocks

class Strategy:

    def __init__(self, universe, *args, **kwargs):
        self.universe   = universe
        self.sig_high   = kwargs.get('sig_high', 1)
        self.sig_low    = kwargs.get('sig_low', -1)
        self.ohlc_col   = 'adj_close'

    @iterate_stocks
    def _paper_trade(self, stock_obj):
        
        for trade_date in stock_obj.signal.index:

            price = stock_obj.tsdb.loc[trade_date][self.ohlc_col]
            signal = stock_obj.signal['signal'].loc[trade_date]

            if signal >= 1 and stock_obj.shares_held > 0: # Sell
                stock_obj.cash_position = stock_obj.cash_position + (100 * price)
                log_entry = f'SELL {stock_obj.symbol} 100 @ {price}'
                stock_obj.trade_log.append(log_entry)
                stock_obj.shares_held = 0

            elif signal <= -1 and stock_obj.shares_held == 0: # Buy
                stock_obj.cash_position = stock_obj.cash_position - (100 * price)
                log_entry = f'BUY {stock_obj.symbol} 100 @ {price}'
                stock_obj.trade_log.append(log_entry)
                stock_obj.shares_held = 100

    @iterate_stocks
    def results(self, stock_obj):
        """
        Loop thru each trade and calculate PnL.  Take current stock
        and convert to cash value to give estimate of holdings.
        """
        share_value = stock_obj.shares_held * stock_obj.tsdb[self.ohlc_col].iloc[-1]
        total_holdings = stock_obj.cash_position + share_value
        print(f"{stock_obj.symbol.upper()} PnL: {total_holdings:.2f}")
