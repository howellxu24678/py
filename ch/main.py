# -*- coding: utf-8 -*-
__author__ = 'xujh'

import nanotime
from pylab import *
import pandas as pd
import os

from chan import *

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['figure.subplot.top'] = 0.96
mpl.rcParams['figure.subplot.bottom'] = 0.03
mpl.rcParams['figure.subplot.left'] = 0.03
mpl.rcParams['figure.subplot.right'] = 0.98
st = nanotime.now()
hqdatadir = 'D:\TdxW_HuaTai\T0002\export2'
code = '999999'
# code = '399006'
filepath = os.path.join(hqdatadir, (code + '.txt'))


rnames = ['d', 't', 'open', 'high', 'low', 'close', 'volume', 'amt']
df5mKline = pd.read_table(filepath,
                          engine='python', sep=',',
                          encoding='gbk',
                          names=rnames,
                          parse_dates={'time': ['d', 't']},
                          index_col='time',
                          skiprows=2,
                          skipfooter=1)
print ('load txt data cost:%d' % (nanotime.now() - st).milliseconds())

def resample(timedelta, df):
    times = int(math.ceil(pd.Timedelta(timedelta) / (df.ikidx[1].name - df.ikidx[0].name)))
    newdf = pd.DataFrame(columns=df.columns)
    for i in xrange(0, df.shape[0], times):
        end = i + times
        end = end if end <= df.shape[0] else df.shape[0]
        newdf.kidx[df.ix[end - 1].name] = {'high': max(df[i:i + times].high.values),
                                          'low': min(df[i:i + times].low.values)}
    return newdf


def addVerticalLineDf(ax, df, **kwargs):
    for i in xrange(df.shape[0]):
        itDf = df.ix[i]
        vline = Line2D(xdata=(i, i), ydata=(itDf['low'], itDf['high']), **kwargs)
        ax.add_line(vline)

    ax.grid(True)
    ax.autoscale_view()

#垂直线
def addVerticalLine(ax, list, **kwargs):
    for i in xrange(len(list)):
        item = list[i]
        vline = Line2D(xdata=(i, i), ydata=(item.low, item.high), **kwargs)
        ax.add_line(vline)

        if item.shape:
            if item.shape == 'u':
                ax.text(i, item.high, u'↑',  horizontalalignment='center', verticalalignment='bottom', color='r')
            elif item.shape == 'd':
                ax.text(i, item.low - 1, u'↓', horizontalalignment='center', verticalalignment='top', color='g')

    ax.grid(True)
    ax.autoscale_view()


#折线
def addBrokenLine(ax, list, btext = True, **kwargs):
    # df.ikidx[int(list.ikidx[0]['kidx'])].high
    if len(list) < 2:
        return
    for i in xrange(len(list) - 1):
        itPen1 = list[i]
        itPen2 = list[i + 1]
        vline = Line2D(xdata=(itPen1.kidx, itPen2.kidx), ydata=(itPen1.value, itPen2.value), **kwargs)
        ax.add_line(vline)
        if btext:
            ax.text(itPen1.kidx, itPen1.value, i, color='magenta', fontsize='10')
    indexLast = len(list) - 1
    if btext:
        ax.text(list[indexLast].kidx, list[indexLast].value, indexLast, color='magenta', fontsize='10')
    ax.autoscale_view()

def addLine1_(ax, df, **kwargs):
    id1, id2 = 3, 10
    itDf1 = df.ix[id1]
    itDf2 = df.ix[id2]
    vline = Line2D(xdata=(id1 + 0.5, id2 + 0.5), ydata=(itDf1.high, itDf2['low']), color='g')
    ax.add_line(vline)
    ax.text(id2 + 0.5, itDf2['low'], '^')


def no_picture():
    st = nanotime.now()

    dft = df5mKline[['high', 'low']]
    ch = Chan(True)
    for i in xrange(dft.shape[0]):
        ch.onNewKline(dft.iloc[i])

    print ('ch cost:%d' % (nanotime.now() - st).milliseconds())

    #print ch._PenPointList
    #print ch._KlineList
    #print ch._LinePointList
    #print tw.getSequence()


def picture1():
    st = nanotime.now()
    fig, ax = plt.subplots(3, 1)
    dft = df5mKline[['high', 'low']]
    # dft = resample('30min',dft)

    ch = Chan(True)
    for i in xrange(dft.shape[0]):
        ch.onNewKline(dft.iloc[i])

    ax[0].set_title(u'原始数据')
    ax[1].set_title(u'处理包含关系并生成笔')
    ax[2].set_title(u'上图中的笔生成的线段')
    addVerticalLineDf(ax[0], dft, color='b')
    addVerticalLine(ax[1], ch._KlineList, color='cyan')
    addBrokenLine(ax[1], ch._PenPointList, color='b', linestyle="-")
    addBrokenLine(ax[2], ch._PenPointList, color='g', linestyle="-.")
    addBrokenLine(ax[2], [ch._PenPointList[lp.pidx] for lp in ch._LinePointList], False, color='b')


    #print ch._PenPointList
    print ('ch cost:%d' % (nanotime.now() - st).milliseconds())
    print ch._PenPointList
    plt.show()

def picture3():
    dft = df5mKline[['high', 'low']]
    # dft = resample('30min',dft)
    ch = Chan(True)
    for i in xrange(dft.shape[0]):
        fig, ax = plt.subplots(1, 1)
        ch.onNewKline(dft.ix[i])
        addVerticalLine(ax, ch._KlineList, color='b')
        addBrokenLine(ax, ch._PenPointList, color='r')
        plt.show()


no_picture()
#picture1()