# -*- coding: utf-8 -*-
__author__ = 'xujh'

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator,\
    DayLocator, MONDAY
from matplotlib.finance import quotes_historical_yahoo_ohlc, candlestick_ohlc


## (Year, month, day) tuples suffice as args for quotes_historical_yahoo
#date1 = (2016, 1, 5)
#date2 = (2016, 2, 17)
#
#
#mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
#alldays = DayLocator()              # minor ticks on the days
#weekFormatter = DateFormatter('%b/%d')  # e.g., Jan 12
#dayFormatter = DateFormatter('%d')      # e.g., 12
#
#quotes = quotes_historical_yahoo_ohlc('000001.SZ', date1, date2)
#if len(quotes) == 0:
#    raise SystemExit
#
#fig, ax = plt.subplots()
#fig.subplots_adjust(bottom=0.2)
#ax.xaxis.set_major_locator(mondays)
#ax.xaxis.set_minor_locator(alldays)
#ax.xaxis.set_major_formatter(weekFormatter)
##ax.xaxis.set_minor_formatter(dayFormatter)
#
##plot_day_summary(ax, quotes, ticksize=3)
#candlestick_ohlc(ax, quotes, width=0.6)
#
#ax.xaxis_date()
#ax.autoscale_view()
#plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
#
#plt.show()


import os
import pandas as pd


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
                                 

def addLine(ax, df):
    for i in range(df.shape[0]):
        itDf = df.ix[i]
        vline = Line2D(xdata=(i, i), ydata=(itDf['low'], itDf['high']))
        ax.add_line(vline)

from matplotlib.lines import Line2D
fig, ax = plt.subplots()

addLine(ax, df5mKline)


#vline = Line2D(xdata=(1.5, 1.5), ydata=(1.5,2.5), linewidth=10,antialiased=True)
#ax.add_line(vline)
#vline = Line2D(xdata=(1.7, 1.7), ydata=(2.5,3.5), linewidth=10,antialiased=True)
#ax.add_line(vline)
#vline = Line2D(xdata=(1.9, 1.9), ydata=(3.5,5.5), linewidth=10,antialiased=True)
#ax.add_line(vline)



# vline = Line2D(xdata=(1.0, 1.0), ydata=(0,0), linewidth=10,antialiased=True)
# ax.add_line(vline)
# vline = Line2D(xdata=(2.9, 2.9), ydata=(3.5,5.5), linewidth=1,antialiased=True)
# ax.add_line(vline)

#ax.autoscale()
ax.autoscale_view()

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