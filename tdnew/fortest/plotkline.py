# -*- coding: utf-8 -*-
__author__ = 'xujh'

#%matplotlib inline

import matplotlib.pyplot as plt
from matplotlib.finance import candlestick_ohlc
import os
import pandas as pd
import talib as ta


hqdatadir = 'D:\TdxW_HuaTai\T0002\export'
code = '000738'
filepath = os.path.join(hqdatadir, (code + '.txt'))
# if not os.path.exists(filepath):
#     logger.critical("filepath %s does not exist", filepath)
#     raise RuntimeError, 'filepath does not exist'

rnames = ['d','t', 'open', 'high', 'low', 'close', 'volume', 'amt']
df5mKline = pd.read_table(filepath,
                                 engine='python', sep = ',',
                                 encoding='gbk',
                                 names=rnames,
                                 parse_dates = {'time':['d','t']},
                                 index_col='time',
                                 skiprows=2,
                                 skipfooter=1)

# ma60_ = ta.SMA(df5mKline['close'].values, 60)
# df5mKline['ma60'] = ma60_
df5mKline.fillna(0.)

fig, ax = plt.subplots()
fig.subplots_adjust(bottom=0.2)
candlestick_ohlc(ax, df5mKline, width=0.6)

ax.xaxis_date()
ax.autoscale_view()
plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

plt.show()

fig, axes = plt.subplots(2, 3)