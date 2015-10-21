# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 15:14:32 2015

@author: guosen
"""

import datetime
import tushare as ts
import numpy as np
import logging
logger = logging.getLogger("run")

def td(kline):
    iCount = -1
    isNeedBuy = False
    isNeedSell = False
    
    curRow = kline.ix[iCount]
    #第n根，close > ma60 且为阳线，然后开始从后往前看是否满足要求
    if curRow['close'] > curRow['ma60'] and curRow['close'] >= curRow['open']:
        iCount = iCount - 1
        curRow = kline.ix[iCount]
        #从第n-1一直到倒数第2根，close > ma60
        while (curRow['close'] >= curRow['ma60'] and abs(iCount) < 10):
            dMin = min(curRow['open'], kline.ix[iCount - 1]['close'])
            #第1根K线 open< ma60 < close (即第一根为被ma60穿过实体的阳线)
            if abs(iCount) >= 3 and dMin <= curRow['ma60'] and curRow['ma60'] <= curRow['close']:
                isNeedBuy = True
                break
            else:
                iCount = iCount - 1
                curRow = kline.ix[iCount]
                
    #第n根，close < ma60 且为阴线，然后开始从后往前看是否满足要求
    elif curRow['close'] < curRow['ma60'] and curRow['close'] < curRow['open']:
        iCount = iCount - 1
        curRow = kline.ix[iCount]
        #从第n-1一直到倒数第2根，close < ma60
        while (curRow['close'] <= curRow['ma60'] and abs(iCount) < 10):
            dMax = max(curRow['open'], kline.ix[iCount - 1]['close'])
            #第1根K线 open > ma60 > close (即第一根为被ma60穿过实体的阴线)
            if abs(iCount) >= 3 and dMax >= curRow['ma60'] and curRow['ma60'] >= curRow['close']:
                isNeedSell = True
                break
            else:
                iCount = iCount - 1
                curRow = kline.ix[iCount]
                
    return isNeedBuy,isNeedSell
    
def IsLastTradingDay(day):
    todayweekday = datetime.date.today().weekday()
    
    if (todayweekday == 0 and datetime.date.today() - day > datetime.timedelta(days=3)) \
        or (todayweekday != 0 and datetime.date.today() - day > datetime.timedelta(days=1)):
            return False
    return True
    #!!!这里后续要补上根据节假日的判断（需要每年的国务院放假时间安排）
    

def GetDayBefore(dayoffset):
    return datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=dayoffset), '%Y-%m-%d')
        
def GetRehabGene(code):
        #无复权日线        
    dfnfq1d = ts.get_hist_data(code,start=GetDayBefore(30),end=GetDayBefore(1))
        
    dffq1d = ts.get_h_data(code,start=GetDayBefore(30),end=GetDayBefore(1))
        
    rate = dffq1d['close'] / dfnfq1d['close']
    print rate
    
def GetRealTimeQuote(code):
    logger.debug("GetRealTimeQuote %s", code)
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