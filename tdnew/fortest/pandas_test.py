# -*- coding: utf-8 -*-
__author__ = 'xujh'


import pandas as pd
import numba
import nanotime
from pandas import Series, DataFrame

sq = pd.DataFrame(columns=['bloc', 'eloc', 'bvalue','evalue', 'high', 'low'])
tsq = pd.DataFrame(index=['bloc', 'eloc', 'bvalue','evalue', 'high', 'low'])


df1 = pd.DataFrame(columns=['high', 'low', 'shape'])
df2 = pd.DataFrame(columns=['high', 'low', 'shape'])
tdf = pd.DataFrame(index=['high', 'low', 'shape'])



#a = [1,2,3,4,5,6]
# d = {'bloc':1, 'eloc':2, 'bvalue':3,'evalue':4, 'high':5, 'low':6}
# ds = Series(d)
#
#
# d1 = {'high':1, 'low':2, 'shape':'u'}
# ds1 = Series(d1)
#
class Df(object):
    def __init__(self, high, low, shape):
        self.high = high
        self.low = low
        self.shape = shape

    def __str__(self):
        return str(self.__dict__)
        #return "high:%d,low:%d,shape:%s" % (self._high, self._low, self._shape)


    def __repr__(self):
        return str(self)
    # def __format__(self):
    #     return "high:%d,low:%d,shape:%s" % (self._high, self._low, self._shape)
    #
    # def __doc__(self):
    #     return "high:%d,low:%d,shape:%s" % (self._high, self._low, self._shape)
dd = Df(1,2,'u')
# #print dd
d = []
#
# @numba.jit
# def testAddRow():
#     for i in xrange(10000):
#         sq.loc[sq.shape[0]] = d
#
# @numba.jit
# def testAddColumn():
#     for i in xrange(10000):
#         tsq[tsq.shape[1]] = ds
#
# @numba.jit
# def testAddRow1():
#     for i in xrange(10000):
#         df1.loc[df1.shape[0]] = d1
#
#
# @numba.jit
# def testAddRow_append():
#     for i in xrange(10000):
#         #df.loc[df.shape[0]] = d1
#         df2.append(d1, ignore_index=True)
#
#
# @numba.jit
# def testAddColumn1():
#     for i in xrange(10000):
#         tdf.append(ds1, ignore_index=True)
#         #tdf[tdf.shape[1]] = ds1
#
def testlist():
    for i in xrange(10):
        d.append(Df(i, i+1, 'u' if i % 2 == 0 else 'd'))
#
# # st = nanotime.now()
# # testAddRow1()
# # print ('testAddRow1 cost:%d' % (nanotime.now() - st).milliseconds())
# #
# # st = nanotime.now()
# # testAddRow_append()
# # print ('testAddRow_append cost:%d' % (nanotime.now() - st).milliseconds())
# #
# # st = nanotime.now()
# # testAddColumn1()
# # print ('testAddColumn1 cost:%d' % (nanotime.now() - st).milliseconds())
#
#
# st = nanotime.now()
# testlist()
# print ('testlist cost:%d' % (nanotime.now() - st).milliseconds())
#
# d

# class Base(object):
#     def __init__(self):
#         self.idx = 0
#
#     def __str__(self):
#         return str(self.__dict__) + '\n'
#
#     def __repr__(self):
#         return str(self)
#
# class Kline(Base):
#     def __init__(self, **kwargs):
#         Base.__init__(self)
#         #super(Kline, self).__init__(self)
#         # shape 用于区分是顶分型还是底分型
#         self.high = kwargs['high']
#         self.low = kwargs['low']
#         self.shape = kwargs['shape'] if 'shape' in kwargs else 'un'
#
# class PenPoint(Base):
#     def __init__(self, **kwargs):
#         Base.__init__(self)
#         #super(PenPoint, self).__init__(self)
#         # kidx在标准k线列表中所处的index，value顶点或者底点的值，shape顶分型还是底分型
#         self.kidx = kwargs['kidx']
#         self.value = kwargs['value']
#         self.shape = kwargs['shape'] if 'shape' in kwargs else 'un'
#         self.stable = 0
#
# class LinePoint(Kline, PenPoint):
#     def __init__(self, **kwargs):
#         Kline.__init__(self,**kwargs)
#         PenPoint.__init__(self,**kwargs)
#         #super(LinePoint, self).__init__(kwargs)
#         # kidx在标准k线列表中所处的index，pidx在笔列表中所处的index,value顶点或者底点的值，shape顶分型还是底分型
#         self.pidx = kwargs['pidx']



class Base(object):
    def __init__(self, **kwargs):
        print 'enter Base'
        self.idx = 0
        print 'leave Base'

    def __str__(self):
        return str(self.__dict__) + '\n'

    def __repr__(self):
        return str(self)


class Kline(Base):
    def __init__(self, **kwargs):
        print 'enter Kline'
        super(Kline, self).__init__(**kwargs)
        # shape 用于区分是顶分型还是底分型
        self.high = kwargs['high']
        self.low = kwargs['low']
        self.shape = kwargs['shape'] if 'shape' in kwargs else 'un'
        print 'leave Kline'


class PenPoint(Base):
    def __init__(self, **kwargs):
        print 'enter PenPoint'
        super(PenPoint, self).__init__(**kwargs)
        # kidx在标准k线列表中所处的index，value顶点或者底点的值，shape顶分型还是底分型
        print
        self.kidx = kwargs['kidx']
        self.value = kwargs['value']
        self.shape = kwargs['shape'] if 'shape' in kwargs else 'un'
        self.stable = 0
        print 'leave PenPoint'


class LinePoint(Kline, PenPoint):
    def __init__(self, **kwargs):
        print 'enter LinePoint'
        super(LinePoint, self).__init__(**kwargs)
        # kidx在标准k线列表中所处的index，pidx在笔列表中所处的index,value顶点或者底点的值，shape顶分型还是底分型
        self.pidx = kwargs['pidx']
        print 'leave LinePoint'

l = LinePoint(high = 1, low = 2, shape = 'u', kidx = 3, value = 4, pidx = 5)

print l


# class A(object):
#     def __init__(self):
#         print 'enter a'
#         print 'leave a'
#
# class B(A):
#     def __init__(self):
#         print 'enter b'
#         A.__init__(self)
#         print 'leave b'
#
# class C(A):
#     def __init__(self):
#         print 'enter c'
#         A.__init__(self)
#         print 'leave c'
#
#
# class D(B,C):
#     def __init__(self):
#         print 'enter d'
#         B.__init__(self)
#         C.__init__(self)
#         print 'leave d'
#
#
# d = D()
#
#
# class Foo(object):
#     def __init__(self, frob, frotz):
#         self.frobnicate = frob
#         self.frotz = frotz
#
#
# class Bar(Foo):
#     def __init__(self, frob, frizzle):
#         super(Bar, self).__init__(frob, 34)
#         self.frazzle = frizzle
#
# b = Bar(34,56)
#
#
# class A(object):
#     def __init__(self, **kw):
#         self.frobnicate = kw['a']
#         self.frotz = kw['b']
#
#
# class B(A):
#     def __init__(self, **kw):
#         super(B, self).__init__(**kw)
#
# b = B(a = 34,b = 56)

        # l = LinePoint(high = 1, low = 2, shape = 'u', kidx = 3, value = 4, pidx = 5)
# print l


# newpen1 = {'bloc': 1,'bvalue': 2,'eloc': 3,'evalue': 4,'high': 5,'low': 6}
# sq.loc[sq.shape[0]] = newpen1
# newpen2 = {'bloc': 11,'bvalue': 12,'eloc': 13,'evalue': 14,'high': 15,'low': 16}
# sq.loc[sq.shape[0]] = newpen2
# newpen3 = {'bloc': 21,'bvalue': 22,'eloc': 23,'evalue': 24,'high': 25,'low': 26}
# sq.loc[sq.shape[0]] = newpen3