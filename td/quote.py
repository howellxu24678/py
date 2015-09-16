# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 17:11:33 2015

@author: guosen
"""

import tushare as ts
import datetime
#from apscheduler.schedulers.background import BackgroundScheduler
import talib as ta
#import logging
import pandas as pd
import numpy as np
#logging.basicConfig()

hqDataDir = "D:\TdxW_HuaTai\T0002\export"


def GetDayBefore(dayoffset):
    return datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=dayoffset), '%Y-%m-%d')
        
def GetRehabGene(code):
        #无复权日线        
    dfnfq1d = ts.get_hist_data(code,start=GetDayBefore(30),end=GetDayBefore(1))
        
    dffq1d = ts.get_h_data(code,start=GetDayBefore(30),end=GetDayBefore(1))
        
    rate = dffq1d['close'] / dfnfq1d['close']
    print rate
    
def GetRealTimeQuote(code):
    #print 'time:',time.strftime("%H:%M:%S",time.localtime())
    df = ts.get_realtime_quotes(code)
    return df[['code','name','price','bid','ask','volume','amount','time']]    
    
    
def GetHistData(code,_ktype):
    df = ts.get_hist_data(code, ktype=_ktype)
    return df[['open','high','close','low','volume']]
    
def Datetime2Str(_datetime):
    return datetime.datetime.strftime(_datetime, "%Y-%m-%d %H:%M:%S")
    
def Str2Datetime(strtime):
    return datetime.datetime.strptime(strtime, "%Y-%m-%d %H:%M:%S")
    
# 当前时间所在的段
def GetTimeSlice(curTickDatetime, min_offset):
    curTimeTuple = curTickDatetime.timetuple()
    minSlice = int(((curTimeTuple.tm_min / min_offset) + 1) * min_offset)
    #print "minSlice:%d" %(minSlice)
    if(minSlice > 59):
        return datetime.datetime(curTimeTuple.tm_year, curTimeTuple.tm_mon, 
                      curTimeTuple.tm_mday, curTimeTuple.tm_hour + 1, 
                      0, 0)
    return datetime.datetime(curTimeTuple.tm_year, curTimeTuple.tm_mon, 
                      curTimeTuple.tm_mday, curTimeTuple.tm_hour, 
                      minSlice, 0)
    
def GetSMA(data):
    return round(np.mean(data),2)
#将传入的时间加上当前的日期返回
def GetDatetimeFromTime(strTime):
    return Str2Datetime(datetime.datetime.strftime(datetime.date.today(),'%Y-%m-%d') + ' ' + strTime)
    
class Quote5mKline(object):
    def __init__(self,code):
        self.__code = code
#        self.__df5mKline = GetHistData(code, '5')
#        ma60 = ta.SMA(self.__df5mKline['close'].values, 60)
#        ma60 = ma60.round(2)
#        self.__df5mKline['ma60'] = ma60
#        print self.__df5mKline
        rnames = ['d','t', 'open', 'high', 'low', 'close', 'volume', 'amt']
        self.__df5mKline = pd.read_table(r"%s\%s.txt"%(hqDataDir, self.__code), 
                                         engine='python', sep = ',', 
                                         encoding='gbk', 
                                         names=rnames, 
                                         parse_dates = {'time':['d','t']},  
                                         index_col='time', 
                                         skiprows=2, 
                                         skipfooter=1)
                                         
        ma60_ = ta.SMA(self.__df5mKline['close'].values, 60)
        self.__df5mKline['ma60'] = ma60_
        
    def GetCode(self):
        return self.__code
        
    def OnTick(self, tick, calback):
        #print 'onTick'
        #当前传过来的Tick价格
        curTickPrice = float(tick['price'].values[0])
        #当前传过来的Tick时间（加上当前日期）
        curTickDatetime = GetDatetimeFromTime(tick['time'].values[0])
        
        dt64CurTimeSlice = pd.to_datetime(GetTimeSlice(curTickDatetime, 5))        
        dt64LastTimeStamp = pd.to_datetime(self.__df5mKline.index.values[-1])
        
        curMa60 = GetSMA(self.__df5mKline['close'].values[-60:])
        
        if(dt64CurTimeSlice > dt64LastTimeStamp):
            calback(self.__df5mKline)
            self.__df5mKline.loc[dt64CurTimeSlice] = {'open':curTickPrice, \
             'high':curTickPrice, \
             'close':curTickPrice, \
             'low':curTickPrice, \
             'volume': 0.0, \
             'ma60':curMa60, \
             'amt':0.0}
        else:
            self.__df5mKline.loc[dt64LastTimeStamp, 'close'] = curTickPrice
            lastHigh = self.__df5mKline.loc[dt64LastTimeStamp, 'high']
            lastLow = self.__df5mKline.loc[dt64LastTimeStamp, 'low']
            self.__df5mKline.loc[dt64LastTimeStamp, 'high'] = max(curTickPrice, lastHigh) 
            self.__df5mKline.loc[dt64LastTimeStamp, 'low'] = min(curTickPrice, lastLow)
                
        print self.__df5mKline
        print self.__code
    
    def TimerToDo(self, calback):
        self.OnTick(GetRealTimeQuote(self.__code), calback)
        #calback(self.__df5mKline)


#def td(kline):
#    iCount = -1
#    isNeedBuy = False
#    isNeedSell = False
#        
#    curRow = kline.ix[iCount]
#    #{第n根，close > ma60 且为阳线，然后开始从后往前看是否满足要求}
#    if curRow['close'] > curRow['ma60'] and curRow['close'] >= curRow['open']:
#        iCount = iCount - 1
#        curRow = kline.ix[iCount]
#        #{从第n-1一直到倒数第2根，close > ma60}
#        while (curRow['close'] >= curRow['ma60'] and abs(iCount) < 10):
#            dMin = min(curRow['open'], kline.ix[iCount - 1]['close'])
#            #{第1根K线 open< ma60 < close (即第一根为被ma60穿过实体的阳线)}
#            if abs(iCount) >= 3 and dMin < curRow['ma60'] and curRow['ma60'] < curRow['close']:
#                isNeedBuy = True
#                break
#            else:
#                iCount = iCount - 1
#                    
#    #{第n根，close < ma60 且为阴线，然后开始从后往前看是否满足要求}
#    elif curRow['close'] < curRow['ma60'] and curRow['close'] < curRow['open']:
#        iCount = iCount - 1
#        curRow = kline.ix[iCount]
#        #{从第n-1一直到倒数第2根，close < ma60}
#        while (curRow['close'] <= curRow['ma60'] and abs(iCount) < 10):
#            dMax = max(curRow['open'], kline.ix[iCount - 1]['close'])
#            #{第1根K线 open< ma60 < close (即第一根为被ma60穿过实体的阳线)}
#            if abs(iCount) >= 3 and dMax > curRow['ma60'] and curRow['ma60'] > curRow['close']:
#                isNeedSell = True
#                break
#            else:
#                iCount = iCount - 1
#                    
#    return isNeedBuy,isNeedSell
    
#def td2(kline):
#    iCount = -1
#    isNeedBuy = False
#    isNeedSell = False
#        
#    curRow = kline.ix[iCount]
#    #{第n根，close > ma60 且为阳线，然后开始从后往前看是否满足要求}
#    if curRow['close'] > curRow['ma60'] and curRow['close'] >= curRow['open']:
#        iCount = iCount - 1
#        curRow = kline.ix[iCount]
#        #{从第n-1一直到倒数第2根，close > ma60}
#        while (curRow['close'] >= curRow['ma60'] and abs(iCount) < 10):
#            dMin = min(curRow['open'], kline.ix[iCount - 1]['close'])
#            #{第1根K线 open< ma60 < close (即第一根为被ma60穿过实体的阳线)}
#            if abs(iCount) >= 3 and dMin < curRow['ma60'] and curRow['ma60'] < curRow['close']:
#                isNeedBuy = True
#                break
#            else:
#                iCount = iCount - 1
#                curRow = kline.ix[iCount]
#                    
#    #{第n根，close < ma60 且为阴线，然后开始从后往前看是否满足要求}
#    elif curRow['close'] < curRow['ma60'] and curRow['close'] < curRow['open']:
#        iCount = iCount - 1
#        curRow = kline.ix[iCount]
#        #{从第n-1一直到倒数第2根，close < ma60}
#        while (curRow['close'] <= curRow['ma60'] and abs(iCount) < 10):
#            dMax = max(curRow['open'], kline.ix[iCount - 1]['close'])
#            #{第1根K线 open< ma60 < close (即第一根为被ma60穿过实体的阳线)}
#            if abs(iCount) >= 3 and dMax > curRow['ma60'] and curRow['ma60'] > curRow['close']:
#                isNeedSell = True
#                break
#            else:
#                iCount = iCount - 1
#                curRow = kline.ix[iCount]
#                    
#    return isNeedBuy,isNeedSell
    
###test###
#df = GetHistData('000609', '5')
#ma60 = ta.SMA(df['close'].values, 60)
#ma60 = ma60.round(2)
#df['ma60'] = ma60
#td(df[:'2015-09-07 13:45:00'])


