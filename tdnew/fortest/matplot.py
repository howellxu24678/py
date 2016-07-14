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
import nanotime
import numba


from pylab import *
mpl.rcParams['font.sans-serif'] = ['SimHei']

class Twine(object):
    def __init__(self, isUp):
        self._isUp = isUp
        #shape 用于区分是顶分型还是底分型
        self._df = pd.DataFrame(columns=['high', 'low', 'shape'])
        #loc在df所处的index，shape顶分型还是底分型，value顶点或者底点的值(按照字母的顺序使之可以按照键值插入)
        self._pen = pd.DataFrame(columns=['loc', 'value', 'shape'])
        #特征序列
        self._sequence = pd.DataFrame(columns=['bloc', 'eloc', 'bvalue','evalue', 'high', 'low'])
        #线段
        self._line = pd.DataFrame(columns=['loc', 'shape', 'value'])

        self._shapeVariableSet = ['na','u','d']
        self._penBeginSearch = 0

    def getDf(self):
        return self._df

    def getPen(self):
        return self._pen

    def getSequence(self):
        return self._sequence

    #是否存在包含关系
    @staticmethod
    def isContain(prekline, curkline):
        #向左包含 n+1包含n
        if curkline['high'] >= prekline['high'] and curkline['low'] <= prekline['low']:
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
        #顶分型
        if line2['high'] > line1['high'] \
                and line2['high'] > line3['high'] \
                and line2['low'] > line1['low'] \
                and line2['low'] > line3['low']:
            return 'u'
        #底分型
        elif line2['high'] < line1['high'] \
                and line2['high'] < line3['high'] \
                and line2['low'] < line1['low'] \
                and line2['low'] < line3['low']:
            return 'd'
        #未知情况
        else:
            return 'na'

    @staticmethod
    #@profile
    def _setValue(df, dict_value):
        #用'un'填补df中没有的字段，否则会出现插入错误
        df_columns_set = set(df.columns.values)
        dict_value_set = set(dict_value.keys())

        andSet = df_columns_set & dict_value_set
        difSet = df_columns_set - dict_value_set

        #从dict_value中取df对应有的列和值，df缺失的列默认用'un'替代
        value_to_set = dict({k: dict_value[k] for k in andSet},
                           **{k: 'un' for k in difSet})

        df.loc[df.shape[0]] = value_to_set


    @staticmethod
    #@profile
    def _procContain(df, isUp, newkline):
        if df.shape[0] < 1 or not Twine.isContain(df.iloc[-1], newkline):
            Twine._setValue(df, newkline)
        else:
            # 高点取高值，低点也取高值，简单的说就是“上升取高高”
            if isUp:
                newkline['high'] = max(df.iloc[-1]['high'], newkline['high'])
                newkline['low'] = max(df.iloc[-1]['low'], newkline['low'])
            # 高点取低值，低点也取低值，简单的说就是“下降取低低”
            else:
                newkline['high'] = min(df.iloc[-1]['high'], newkline['high'])
                newkline['low'] = min(df.iloc[-1]['low'], newkline['low'])
            # 处理完包含关系后，将前一个删除，只保留最终处理完的结果
            df.drop(df.index[-1], inplace=True)
            #递归处理包含关系，有可能出现处理包含之后的元素和之前的元素还存在包含关系
            return Twine._procContain(df, isUp, newkline)


    #方向（属于向上笔还是向下笔）
    @staticmethod
    def getDirect(pen_start, pen_end):
        #向上笔
        if pen_start['value'] < pen_end['value']:
            return 'u'
        #向下笔
        elif pen_start['value'] > pen_end['value']:
            return 'd'
        #位置情况
        return 'na'

    @staticmethod
    def LineBreakByPen(dfPen, ):
        pass

    #获取subDf中形态为顶分型的最高点
    @staticmethod
    #@profile
    def getUpHighPoint(subDf):
        #subDf[(subDf['shape'] == 'u') & (subDf['high'] == max(subDf['high'].values))]
        return subDf[(subDf['high'] == max(subDf['high'].values)) & (subDf['shape'] == 'u')]

    #获取subDf中形态为底分型的最低点
    @staticmethod
    #@profile
    def getDownLowPoint(subDf):
        #subDf[(subDf['shape'] == 'd') & (subDf['low'] == min(subDf['low'].values))]
        return subDf[(subDf['low'] == min(subDf['low'].values)) & (subDf['shape'] == 'd')]

    #@profile
    def onNewKline(self, newkline):
        self.procKlineContain(self._df, newkline)
        self.procShape()
        #有新笔生成才需要进行线段的处理
        if self.procPen():
            self.procLine()

    def procLine(self):
        #生成的最后一笔是会变的
        #笔的方向可以通过终点的类型来判断，如果是'u'则是向上笔，如果是'd'则是向下笔
        #首次开始
        #笔的数量小于3时，不可能形成线段
        if self._pen.shape[0] < 3:
            return

        if self._line.shape[0] < 2:
            if self._pen.shape[0] % 2 == 0:
                newpen = {'bloc': self._pen.iloc[-3]['loc'],
                          'bvalue': self._pen.iloc[-3]['value'],
                          'eloc': self._pen.iloc[-2]['loc'],
                          'evalue': self._pen.iloc[-2]['value'],
                          'high': max(self._pen.iloc[-3]['value'], self._pen.iloc[-2]['value']),
                          'low': min(self._pen.iloc[-3]['value'], self._pen.iloc[-2]['value'])
                          }
                self._procContain(self._sequence,
                                  True if self._pen.iloc[0, self._pen.columns.get_loc('shape')] == 'd' else False,
                                  newpen)

                # self._sequence.loc[self._sequence.shape[0]] = {'bloc': self._pen.iloc[-3]['loc'],
                #                                                'bvalue': self._pen.iloc[-3]['value'],
                #                                                'eloc': self._pen.iloc[-2]['loc'],
                #                                                'evalue': self._pen.iloc[-2]['value'],
                #                                                'high': max(self._pen.iloc[-3]['value'], self._pen.iloc[-2]['value']),
                #                                                'low': min(self._pen.iloc[-3]['value'], self._pen.iloc[-2]['value'])
                #                                                }
            # shape = self._pen.iloc[0, self._pen.columns.get_loc('shape')] == 'u'
            # #向下笔开始，笔的起点为顶分型
            # if shape == 'u':
            #     self._sequence.loc[df.shape[0]] = {'loc': 25, 'shape': 'u', 'value': 2568}
            # #向上笔开始，笔的起点为底分型
            # elif shape == 'd':
            #     pass

        else:
            pass

    #@profile
    #返回值为True：有新笔生成，False：没有新笔生成
    def procPen(self):
        #首次开始
        if self._pen.shape[0] < 2:
            dh = self.getUpHighPoint(self._df)
            if dh.empty:
                return False
            dl = self.getDownLowPoint(self._df)
            if dl.empty:
                return False
            dhLoc = dh.index[0]
            dlLoc = dl.index[0]

            if abs(dhLoc - dlLoc) >= 4:
                if dhLoc > dlLoc:
                    self._pen.loc[self._pen.shape[0]] = {'loc': dlLoc, 'shape': dl.iloc[0]['shape'], 'value': dl.iloc[0]['low']}
                    self._pen.loc[self._pen.shape[0]] = {'loc': dhLoc, 'shape': dh.iloc[0]['shape'], 'value': dh.iloc[0]['high']}
                else:
                    self._pen.loc[self._pen.shape[0]] = {'loc': dhLoc, 'shape': dh.iloc[0]['shape'], 'value': dh.iloc[0]['high']}
                    self._pen.loc[self._pen.shape[0]] = {'loc': dlLoc, 'shape': dl.iloc[0]['shape'], 'value': dl.iloc[0]['low']}
                return True
            else:
                return False
        else:
            #前一趋势是向上时
            if self._pen.iloc[-1]['shape'] == 'u':
                dh = self.getUpHighPoint(self._df[int(self._pen.iloc[-2]['loc']): self._df.shape[0]])
                if dh.empty:
                    return False
                dhLoc = dh.index[0]
                if dhLoc > self._pen.iloc[-1]['loc']:
                    self._pen.iloc[-1,self._pen.columns.get_loc('loc')] = dhLoc
                    self._pen.iloc[-1,self._pen.columns.get_loc('value')] = dh.iloc[0]['high']
                dl = self.getDownLowPoint(self._df[int(dhLoc): self._df.shape[0]])
                if dl.empty:
                    return False
                dlLoc = dl.index[0]
                if abs(dlLoc - self._pen.iloc[-1]['loc']) >= 4:
                    self._pen.loc[self._pen.shape[0]] = {'loc': dlLoc, 'shape': dl.iloc[0]['shape'], 'value': dl.iloc[0]['low']}
                    return True
                else:
                    return False
            #前一趋势是向下时
            else:
                dl = self.getDownLowPoint(self._df[int(self._pen.iloc[-2]['loc']): self._df.shape[0]])
                if dl.empty:
                    return False
                dlLoc = dl.index[0]
                if dlLoc > self._pen.iloc[-1]['loc']:
                    self._pen.iloc[-1, self._pen.columns.get_loc('loc')] = dlLoc
                    self._pen.iloc[-1, self._pen.columns.get_loc('value')] = dl.iloc[0]['low']
                dh = self.getUpHighPoint(self._df[int(dlLoc): self._df.shape[0]])
                if dh.empty:
                    return False
                dhLoc = dh.index[0]
                if abs(dhLoc - self._pen.iloc[-1]['loc']) >= 4:
                    self._pen.loc[self._pen.shape[0]] = {'loc': dhLoc, 'shape': dh.iloc[0]['shape'], 'value': dh.iloc[0]['high']}
                    return True
                else:
                    return False

    #@profile
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

    #@profile
    def procKlineContain(self, df, newkline):
        if df.shape[0] < 2:
            self._procContain(df, self._isUp, newkline)
        else:
            self._procContain(df, self.isUp(df.iloc[-2], df.iloc[-1]), newkline)



st = nanotime.now()
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
print ('load txt data cost:%d' % (nanotime.now() - st).milliseconds())


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
        vline = Line2D(xdata=(i+0.5, i+0.5), ydata=(itDf['low'], itDf['high']), linewidth = 3, **kwargs)
        ax.add_line(vline)

        #标识顶/底分型
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


def no_picture():
    st = nanotime.now()

    dft = df5mKline[['high', 'low']]
    tw = Twine(True)
    for i in xrange(dft.shape[0]):
        tw.onNewKline(dft.iloc[i])

    print ('tw cost:%d' % (nanotime.now() - st).milliseconds())

    print tw.getDf()
    print tw.getPen()
    # print tw.getSequence()

def picture1():
    fig, ax = plt.subplots(3,1)
    dft = df5mKline[['high','low']]

    tw = Twine(True)
    for i in xrange(dft.shape[0]):
        tw.onNewKline(dft.iloc[i])

    ax[0].set_title(u'原始数据')
    ax[1].set_title(u'处理包含关系并生成笔')
    ax[2].set_title(u'上一图中的笔')
    addLine1(ax[0], dft, color = 'b')
    addLine1(ax[1], tw.getDf(), color='b')
    addPen(ax[1], tw.getPen(), color='r')
    addPen(ax[2], tw.getPen(), color='r')
    #addLine1_(ax[1], tw.getdf())
    # print 'df'
    # print tw.getdf()

    print 'pen'
    print tw.getPen()

    # addLine1(ax[2], dft, color = 'r')
    # addLine1(ax[2], tw.getdf(), color = 'b', linestyle = ':')
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
        addPen(ax, tw.getPen(), color = 'r')
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

no_picture()
#picture3()

#
# ndt = sq.iloc[1].to_dict()
#
#
# df = pd.DataFrame(columns=['high', 'low', 'shape'])
#
# df_columns_set = set(df.columns.values)
# dict_value_set = set(ndt.keys())
#
# dict_to_set = dict({k: ndt[k] for k in df_columns_set & dict_value_set}, **{k: 'un' for k in df_columns_set - dict_value_set})
# dict_to_set = {k: ndt[k] for k in df_columns_set & dict_value_set}.update(
#     {k: 'un' for k in df_columns_set - dict_value_set})
#
# set(df.columns.values) & set(ndt.keys())
#
# for column in df.columns.values:
#     if not column in kwargs:
#         kwargs[column] = 'un'
#
#
# {k: ndt[k] for k in ndt.keys() and (k in df.columns.values)}

#picture1()

# import nanotime
# import time
# st = nanotime.now()
# time.sleep(1)
# print (nanotime.now() - st).milliseconds()

# def test(df):
#     df.loc[df.shape[0]] = {'loc': 25, 'shape': 'u', 'value': 2568}

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