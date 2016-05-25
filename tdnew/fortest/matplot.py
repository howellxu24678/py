# -*- coding: utf-8 -*-
__author__ = 'xujh'

import matplotlib.pyplot as plt
import os
import pandas as pd
import datetime


class Twine(object):
    def __init__(self):
        # self._df = pd.DataFrame(columns={'high', 'low'})
        # self._df.loc[pd.to_datetime(datetime.datetime.now())] = {'high':60.2, 'low':32.3}
        pass

    #是否存在包含关系
    def isContain(self, pre_line, curkline):
        #向左包含 n+1包含n
        if curkline['high'] >= pre_line['high'] and curkline['low'] <= pre_line['low']:
            return  True
        #向右包含 n包含n+1
        elif curkline['high'] <= pre_line['high'] and curkline['low'] >= pre_line['low']:
            return  True
        else:
            return  False

    #判断是上升趋势还是下降趋势,True为上升趋势，False为下降趋势
    def upOrDown(self, line1, line2):
        if line2['high'] >= line1['high'] and line2['low'] >= line1['low']:
            return True
        else:
            return False


    def contain(self, curkline):
        if len(self._df) < 1:
            self._df.loc[curkline['time']] = {'high':curkline['high'],
                                              'low':curkline['low']}
            return

        if len(self._df) < 2:
            if self.isContain(self._df.ix[-1], curkline):
                pass


        if self.isContain(self._df.ix[-1], curkline):
            if self.upOrDown(self._df.ix[-2], self._df.ix[-1]):
                self._df.loc[curkline['time']] = {'high': max(self._df.ix[-1]['high'], curkline['high']),\
                                                  'low': max(self._df.ix[-1]['low'], curkline['low'])}
            else:
                self._df.loc[curkline['time']] = {'high': min(self._df.ix[-1]['high'], curkline['high']),\
                                                  'low': min(self._df.ix[-1]['low'], curkline['low'])}
            #处理完包含关系后，将前一个删除，只保留最终处理完的结果
            self._df = self._df.drop(pd.Timestamp(self._df.index.values[-2]))

    def procContain(self, df):
        for i in xrange(df.shape[0]):
            pass
                                 

def addLine(ax, df):
    for i in xrange(df.shape[0]):
        itDf = df.ix[i]
        vline = Line2D(xdata=(i, i), ydata=(itDf['low'], itDf['high']))
        ax.add_line(vline)
        ax.autoscale_view()

from matplotlib.lines import Line2D
fig, ax = plt.subplots(3,1)

hqdatadir = 'D:\TdxW_HuaTai\T0002\export'
code = '000778'
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
dft = df5mKline[['low','high']]
addLine(ax[0], dft)

#plt.axhspan(xmin=0, xmax=1.2, facecolor='0.5', alpha=0.5)
#plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
plt.show()


#import numpy as np
#import matplotlib.pyplot as plt
#
#def f(t):
#    return np.exp(-t) * np.cos(2 * np.pi * t)
#    
#t1 = np.arange(0.0, 5.0, 0.1)
#t2 = np.arange(0.0, 5.0, 0.02)
#
#plt.figure(1)
#plt.subplot(211)
#plt.plot(t1, f(t1), 'bo', t2, f(t2), 'k')
#
#plt.subplot(212)
#plt.plot(t2, np.cos(2 * np.pi * t2), 'r--')
#plt.show()

#start = dt.datetime(2015, 7, 1)
#data = pd.io.data.DataReader('AAPL', 'yahoo', start)
#data = data.reset_index()
#data['Date2'] = data['Date'].apply(lambda d: mdates.date2num(d.to_pydatetime()))
#tuples = [tuple(x) for x in data[['Date2','Open','High','Low','Close']].values]
#
#fig, ax = plt.subplots()
#ax.xaxis_date()
#ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
#plt.xticks(rotation=45)
#plt.xlabel("Date")
#plt.ylabel("Price")
#plt.title("AAPL")
#candlestick_ohlc(ax, tuples, width=.6, colorup='g', alpha =.4)