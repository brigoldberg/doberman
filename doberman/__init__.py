# __init__.py
import logging
from .backtester import BackTester
from .stock import Stock
from .strategy import StrategyFactory
from .universe import Universe

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
handler = logging.StreamHandler()
logger.addHandler(handler)

formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
