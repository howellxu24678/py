# -*- coding: utf-8 -*-
__author__ = 'xujh'


import pandas as pd
import numba
import nanotime
from pandas import Series, DataFrame

sq = pd.DataFrame(columns=['bloc', 'eloc', 'bvalue','evalue', 'high', 'low'])
tsq = pd.DataFrame(index=['bloc', 'eloc', 'bvalue','evalue', 'high', 'low'])


df = pd.DataFrame(columns=['high', 'low', 'shape'])
tdf = pd.DataFrame(index=['high', 'low', 'shape'])

#a = [1,2,3,4,5,6]
d = {'bloc':1, 'eloc':2, 'bvalue':3,'evalue':4, 'high':5, 'low':6}
ds = Series(d)


d1 = {'high':1, 'low':2, 'shape':'u'}
ds1 = Series(d)

class Df(object):
    def __init__(self, high, low, shape):
        self._high = high
        self._low = low
        self._shape = shape

    def __str__(self):
        return "high:%d,low:%d,shape:%s" % (self._high, self._low, self._shape)


    def __dict

dd = Df(1,2,'u')
d = []

@numba.jit
def testAddRow():
    for i in xrange(10000):
        sq.loc[sq.shape[0]] = d

@numba.jit
def testAddColumn():
    for i in xrange(10000):
        tsq[tsq.shape[1]] = ds


@numba.jit
def testAddRow1():
    for i in xrange(100000):
        df.loc[sq.shape[0]] = d1


@numba.jit
def testAddColumn1():
    for i in xrange(100000):
        tdf[tsq.shape[1]] = ds1

@numba.jit
def testlist():
    for i in xrange(100000):
        d.append(Df(i, i+1, 'u' if i % 2 == 0 else 'd'))

st = nanotime.now()
testAddColumn1()
print ('testAddColumn1 cost:%d' % (nanotime.now() - st).milliseconds())


st = nanotime.now()
testlist()
print ('testlist cost:%d' % (nanotime.now() - st).milliseconds())

# newpen1 = {'bloc': 1,'bvalue': 2,'eloc': 3,'evalue': 4,'high': 5,'low': 6}
# sq.loc[sq.shape[0]] = newpen1
# newpen2 = {'bloc': 11,'bvalue': 12,'eloc': 13,'evalue': 14,'high': 15,'low': 16}
# sq.loc[sq.shape[0]] = newpen2
# newpen3 = {'bloc': 21,'bvalue': 22,'eloc': 23,'evalue': 24,'high': 25,'low': 26}
# sq.loc[sq.shape[0]] = newpen3