""" Utility Functions """

# For processing every stock object in a universe. 
# Pass in stock object. USED IN Universe OBJECT
def iterate_basket(func):
    def inner(obj, *args, **kwargs):
        for k in obj.stocks.keys():
            func(obj, obj.stocks[k], *args, **kwargs)
    return inner

# For processing every stock object in a universe. 
# USED IN Strategy OBJECT
def iterate_stocks(func):
    def wrapper(obj):
        for k in obj.universe.stocks.keys():
            func(obj, obj.universe.stocks[k])
    return wrapper

# For processing every day in an OHLC dataframe. 
# Pass in OHLC dataframe.
def iterate_tsdb(func):
    def wrapper(obj_symbol, col_name):
        for trade_date in obj_symbol.tsdb.index:
            func(obj_symbol.tsdb.loc[trade_date], col_name)
    return wrapper
