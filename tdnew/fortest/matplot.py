# -*- coding: utf-8 -*-
__author__ = 'xujh'

import matplotlib.pyplot as plt
import os
import pandas as pd
import datetime
import matplotlib.dates as dt
from matplotlib.lines import Line2D
from matplotlib.dates import *
import math


class Twine(object):
    def __init__(self, isUp):
        self._isUp = isUp
        #shape 用于区分是顶分型还是底分型
        self._df = pd.DataFrame(columns=['high', 'low', 'shape'])
        #loc在df所处的index，shape顶分型还是底分型，value顶点或者底点的值
        self._pen = pd.DataFrame(columns=['loc', 'shape', 'value'])
        self._shapeVariableSet = ['na','u','d']
        self._penBeginSearch = 0

    def getDf(self):
        return self._df

    def getPen(self):
        return self._pen

    #是否存在包含关系
    @staticmethod
    def isContain(prekline, curkline):
        #向左包含 n+1包含n
        if curkline['high'] >= prekline['high']  and curkline['low'] <= prekline['low']:
            return True
        #向右包含 n包含n+1
        elif curkline['high'] <= prekline['high'] and curkline['low'] >= prekline['low']:
            return True
        else:
            return False

    #判断是上升趋势还是下降趋势,True为上升趋势，False为下降趋势
    @staticmethod
    def isUp(line1, line2):
        if line2['high'] >= line1['high'] and line2['low'] >= line1['low']:
            return True
        else:
            return False

    @staticmethod
    def getShape(line1, line2, line3):
        if line2['high'] > line1['high'] \
                and line2['high'] > line3['high'] \
                and line2['low'] > line1['low'] \
                and line2['low'] > line3['low']:
            return 'u'
        elif line2['high'] < line1['high'] \
                and line2['high'] < line3['high'] \
                and line2['low'] < line1['low'] \
                and line2['low'] < line3['low']:
            return 'd'
        else:
            return 'na'

    def onNewKline(self, newkline):
        self.procContain(newkline)
        self.procShape()
        self.procPen()
        self.procLine()

    #获取subDf中形态为顶分型的最高点
    def getUpHighPoint(self, subDf):
        return subDf[(subDf['shape'] == 'u') & (subDf['high'] == max(subDf['high'].values))]

    #获取subDf中形态为底分型的最低点
    def getDownLowPoint(self, subDf):
        return subDf[(subDf['shape'] == 'd') & (subDf['low'] == min(subDf['low'].values))]

    def procLine(self):
        pass

    def procPen(self):
        #首次开始
        if self._pen.shape[0] < 2:
            subDf = self._df[0: self._df.shape[0]]
            dh = self.getUpHighPoint(subDf)
            if dh.empty:
                return
            dl = self.getDownLowPoint(subDf)
            if dl.empty:
                return
            dhLoc = self._df.index.get_loc(dh.index[0])
            dlLoc = self._df.index.get_loc(dl.index[0])

            if abs(dhLoc - dlLoc) >= 4:
                if dhLoc > dlLoc:
                    self._pen.loc[self._pen.shape[0]] = {'loc': dlLoc, 'shape': dl['shape'][0], 'value': dl['low'][0]}
                    self._pen.loc[self._pen.shape[0]] = {'loc': dhLoc, 'shape': dh['shape'][0], 'value': dh['high'][0]}
                else:
                    self._pen.loc[self._pen.shape[0]] = {'loc': dhLoc, 'shape': dh['shape'][0], 'value': dh['high'][0]}
                    self._pen.loc[self._pen.shape[0]] = {'loc': dlLoc, 'shape': dl['shape'][0], 'value': dl['low'][0]}
        else:
            #前一趋势是向上时
            if self._pen.iloc[-1]['shape'] == 'u':
                dh = self.getUpHighPoint(self._df[int(self._pen.iloc[-2]['loc']): self._df.shape[0]])
                if dh.empty:
                    return
                dhLoc = self._df.index.get_loc(dh.index[0])
                if dhLoc > self._pen.iloc[-1]['loc']:
                    self._pen.iloc[-1, self._pen.columns.get_loc('loc')] = dhLoc
                    self._pen.iloc[-1, self._pen.columns.get_loc('value')] = dh['high'][0]
                dl = self.getDownLowPoint(self._df[int(dhLoc): self._df.shape[0]])
                if dl.empty:
                    return
                dlLoc = self._df.index.get_loc(dl.index[0])
                if abs(dlLoc - self._pen.iloc[-1]['loc']) >= 4:
                    self._pen.loc[self._pen.shape[0]] = {'loc': dlLoc, 'shape': dl['shape'][0], 'value': dl['low'][0]}
            #前一趋势是向下时
            else:
                dl = self.getDownLowPoint(self._df[int(self._pen.iloc[-2]['loc']): self._df.shape[0]])
                if dl.empty:
                    return
                dlLoc = self._df.index.get_loc(dl.index[0])
                if dlLoc > self._pen.iloc[-1]['loc']:
                    self._pen.iloc[-1, self._pen.columns.get_loc('loc')] = dlLoc
                    self._pen.iloc[-1, self._pen.columns.get_loc('value')] = dl['low'][0]
                dh = self.getUpHighPoint(self._df[int(dlLoc): self._df.shape[0]])
                if dh.empty:
                    return
                dhLoc = self._df.index.get_loc(dh.index[0])
                if abs(dhLoc - self._pen.iloc[-1]['loc']) >= 4:
                    self._pen.loc[self._pen.shape[0]] = {'loc': dhLoc, 'shape': dh['shape'][0], 'value': dh['high'][0]}

    def procShape(self):
        if self._df.shape[0] < 3:
            return
        for i in xrange(2, self._df.shape[0]):
            #性能优化，只做一次推断，不重复推断
            if self._df.iloc[-i, self._df.columns.get_loc('shape')] in self._shapeVariableSet:
                break

            self._df.iloc[-i, self._df.columns.get_loc('shape')] = self.getShape(
                self._df.iloc[-i-1],
                self._df.iloc[-i],
                self._df.iloc[-i+1])

    def procContain(self, newkline):
        if self._df.shape[0] < 1 or not self.isContain(self._df.ix[-1], newkline):
            self._setValue(newkline.name, high= newkline['high'],low = newkline['low'])
        elif self._df.shape[0] < 2:
            self._procContain(self._isUp, newkline)
        else:
            self._procContain(self.isUp(self._df.ix[-2], self._df.ix[-1]), newkline)

    def _setValue(self, loc, **kwargs):
        if not 'shape' in kwargs:
            kwargs['shape'] = 'un'
        self._df.loc[loc] = {k:kwargs[k] for k in sorted(kwargs.keys())}

    def _procContain(self, isUp, newkline):
        #高点取高值，低点也取高值，简单的说就是“上升取高高”
        if isUp:
            self._setValue(newkline.name,
                           high = max(self._df.ix[-1]['high'], newkline['high']),
                           low = max(self._df.ix[-1]['low'], newkline['low']))
        #高点取低值，低点也取低值，简单的说就是“下降取低低”
        else:
            self._setValue(newkline.name,
                           high = min(self._df.ix[-1]['high'], newkline['high']),
                           low = min(self._df.ix[-1]['low'], newkline['low']))
        #处理完包含关系后，将前一个删除，只保留最终处理完的结果
        self._df = self._df.drop(pd.Timestamp(self._df.index.values[-2]))


hqdatadir = 'D:\TdxW_HuaTai\T0002\export2'
code = '999999'
#code = '399006'
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


def resample(timedelta, df):
    times = int(math.ceil(pd.Timedelta(timedelta) / (df.iloc[1].name - df.iloc[0].name)))
    newdf = pd.DataFrame(columns=df.columns)
    for i in xrange(0, df.shape[0], times):
        end = i + times
        end = end if end <= df.shape[0] else df.shape[0]
        newdf.loc[df.ix[end-1].name] = {'high': max(df[i:i+times]['high'].values),
                                        'low': min(df[i:i+times]['low'].values)}
    return newdf



def addLine1(ax, df, **kwargs):
    for i in xrange(df.shape[0]):
        itDf = df.ix[i]
        vline = Line2D(xdata=(i+0.5, i+0.5), ydata=(itDf['low'], itDf['high']), linewidth = 5, **kwargs)
        ax.add_line(vline)

        if 'shape' in itDf:
            if itDf['shape'] == 'u':
                ax.text(i+0.5, itDf['high'], 'u', color = 'r')
            elif itDf['shape'] == 'd':
                ax.text(i+0.5, itDf['low'], 'd', color = 'g')

    ax.grid(True)
    ax.autoscale_view()

def addPen(ax, pen, **kwargs):
    #df.iloc[int(pen.iloc[0]['loc'])]['high']
    if pen.shape[0] < 2:
        return
    for i in xrange(pen.shape[0] - 1):
        itPen1 = pen.ix[i]
        itPen2 = pen.ix[i+1]
        vline = Line2D(xdata=(itPen1['loc'], itPen2['loc']), ydata=(itPen1['value'], itPen2['value']), **kwargs)
        ax.add_line(vline)
        ax.text(itPen1['loc'], itPen1['value'], i,color = 'cyan', fontsize='14')
    indexLast = pen.shape[0] - 1
    ax.text(pen.ix[indexLast]['loc'], pen.ix[indexLast]['value'], indexLast, color = 'cyan', fontsize='14')
    ax.autoscale_view()


def addLine1_(ax, df, **kwargs):
    id1,id2 = 3,10
    itDf1 = df.ix[id1]
    itDf2 = df.ix[id2]
    vline = Line2D(xdata=(id1+0.5, id2+0.5), ydata=(itDf1['high'], itDf2['low']),color = 'g')
    ax.add_line(vline)
    ax.text(id2+0.5, itDf2['low'], '^')

def picture1():
    fig, ax = plt.subplots(3,1)
    dft = df5mKline[['high','low']]
    #dft = resample('30min',dft)


    tw = Twine(True)
    for i in xrange(dft.shape[0]):
        tw.onNewKline(dft.ix[i])

    addLine1(ax[0], dft, color = 'b')
    addLine1(ax[1], tw.getDf(), color='b')
    addPen(ax[1], tw.getPen(), color='r')
    addPen(ax[2], tw.getPen(), color='r')
    #addLine1_(ax[1], tw.getDf())
    print tw.getDf()

    # addLine1(ax[2], dft, color = 'r')
    # addLine1(ax[2], tw.getDf(), color = 'b', linestyle = ':')
    #plt.axhspan(xmin=0, xmax=1.2, facecolor='0.5', alpha=0.5)
    #plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.show()
    
def picture3():    
    dft = df5mKline[['high','low']]
    #dft = resample('30min',dft)
    tw = Twine(True)
    for i in xrange(dft.shape[0]):
        fig, ax = plt.subplots(1,1)
        tw.onNewKline(dft.ix[i])
        addLine1(ax, tw.getDf(), color = 'b')
        addPen(ax, tw.getDf(), tw.getPen(), color = 'r')
        plt.show()

def addLine2(ax, df, **kwargs):
    for i in xrange(df.shape[0]):
        itDf = df.ix[i]
        vline = Line2D(xdata=(dt.date2num(itDf.name), dt.date2num(itDf.name)), ydata=(itDf['low'], itDf['high']), linewidth = 5, **kwargs)
        ax.add_line(vline)
        ax.autoscale_view()

def picture2():
    fig, ax = plt.subplots(2,1)
    fig.subplots_adjust(bottom=0.2)
    dft = df5mKline[['high','low']]
    addLine2(ax[0], dft)

    tw = Twine(True)
    for i in xrange(dft.shape[0]):
        tw.onNewKline(dft.ix[i])

    addLine2(ax[1], tw.getDf(), color = 'r')


    #mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
    # alldays = MinuteLocator(interval=5)              # minor ticks on the days
    # weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12
    # dayFormatter = DateFormatter('%d')      # e.g., 12
    # minuteFormatter = DateFormatter('%H:%M')

    autodates = AutoDateLocator()
    for _ax in ax:
        _ax.xaxis.set_major_locator(DayLocator())
        _ax.xaxis.set_minor_locator(MinuteLocator(interval=30))
        _ax.xaxis.set_major_formatter(DateFormatter('%m/%d'))
        _ax.xaxis.set_minor_formatter(DateFormatter('%H:%M'))
        _ax.xaxis_date()
        _ax.autoscale_view()

    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.show()

picture1()
#%timeit picture1()

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

#%matplotlib inline
#dd[0:5][dd[0:5]['shape'] == 'u']
#dd[dd['high'] == max(dd['high'].values)]
# d1 = dd[0:5]
# dd['high'] == max(dd['high'].values)]