#!/usr/bin/env python3

import os
import pprint
import pandas as pd

tick_ds = os.path.expanduser('~/tick_data/ohlc_ds.h5')
store = pd.HDFStore(tick_ds, 'r')
pprint.pprint(store.keys())
