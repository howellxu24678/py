# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 17:11:33 2015

@author: guosen
"""

import os
import tushare as ts
import datetime
import talib as ta
import pandas as pd
import numpy as np
import logging
logger = logging.getLogger()



def GetDayBefore(dayoffset):
    return datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=dayoffset), '%Y-%m-%d')
        
def GetRehabGene(code):
        #无复权日线        
    dfnfq1d = ts.get_hist_data(code,start=GetDayBefore(30),end=GetDayBefore(1))
        
    dffq1d = ts.get_h_data(code,start=GetDayBefore(30),end=GetDayBefore(1))
        
    rate = dffq1d['close'] / dfnfq1d['close']
    print rate
    
def GetRealTimeQuote(code):
    logger.info("GetRealTimeQuote %s", code)
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
    def __init__(self,cf, code):
        self._code = code
        
        markettime = cf.get("DEFAULT", "markettime").split(',')
        self._marketimerange = []
        for i in range(len(markettime)):
            self._marketimerange.append(markettime[i].split('~'))
        
        self.GetHistDataFromFile(cf.get("DEFAULT", "hqdatadir"))
        self.CheckHistoryData()
        
    def GetHistDataFromFile(self, hqdatadir):
        filepath = r"%s\%s.txt"%(hqdatadir, self._code)
        if not os.path.exists(filepath):
            logger.critical("filepath %s does not exist", filepath)
            raise RuntimeError, 'filepath does not exist'
            
        rnames = ['d','t', 'open', 'high', 'low', 'close', 'volume', 'amt']
        self._df5mKline = pd.read_table(filepath, 
                                         engine='python', sep = ',', 
                                         encoding='gbk', 
                                         names=rnames, 
                                         parse_dates = {'time':['d','t']},  
                                         index_col='time', 
                                         skiprows=2, 
                                         skipfooter=1)
                                      
        ma60_ = ta.SMA(self._df5mKline['close'].values, 60)
        self._df5mKline['ma60'] = ma60_
        self._df5mKline.fillna(0.)

        
    def CheckHistoryData(self):
        dataLastDay = self._df5mKline.index[-1].date()
        todayweekday = datetime.date.today().weekday()
        
        if (todayweekday == 0 and datetime.date.today() - dataLastDay > datetime.timedelta(days=3)) \
            or (todayweekday != 0 and datetime.date.today() - dataLastDay > datetime.timedelta(days=1)):
            logger.critical("code:%s the history data is out of date, lastday:%s", self._code, dataLastDay)
            raise RuntimeError, 'the history data is out of date'
            
        #!!!这里后续要补上根据节假日的判断（需要每年的国务院放假时间安排）
        
    def CheckIfInTheMarketTimeRange(self, time):
        for i in range(len(self._marketimerange)):
            if time >= self._marketimerange[i][0] and time <= self._marketimerange[i][1]:
                return True
        return False
        
    def OnTick(self, tick, calback):
        if not self.CheckIfInTheMarketTimeRange(tick['time'].values[0]):
            logger.warn("code:%s, time:%s is not in the market time range", self._code, tick['time'].values[0])            
            return
            
        #当前传过来的Tick价格
        curTickPrice = float(tick['price'].values[0])
        #当前传过来的Tick时间（加上当前日期）
        curTickDatetime = GetDatetimeFromTime(tick['time'].values[0])
        
        dt64CurTimeSlice = pd.to_datetime(GetTimeSlice(curTickDatetime, 5))        
        dt64LastTimeStamp = pd.to_datetime(self._df5mKline.index.values[-1])
        
        curMa60 = GetSMA(self._df5mKline['close'].values[-60:])
        
        if(dt64CurTimeSlice > dt64LastTimeStamp):
            calback(self._df5mKline)
            self._df5mKline.loc[dt64CurTimeSlice] = {'open':curTickPrice, \
             'high':curTickPrice, \
             'close':curTickPrice, \
             'low':curTickPrice, \
             'volume': 0.0, \
             'ma60':curMa60, \
             'amt':0.0}
        else:
            self._df5mKline.loc[dt64LastTimeStamp, 'close'] = curTickPrice
            lastHigh = self._df5mKline.loc[dt64LastTimeStamp, 'high']
            lastLow = self._df5mKline.loc[dt64LastTimeStamp, 'low']
            self._df5mKline.loc[dt64LastTimeStamp, 'high'] = max(curTickPrice, lastHigh) 
            self._df5mKline.loc[dt64LastTimeStamp, 'low'] = min(curTickPrice, lastLow)
                
        logger.info("code:%s, kline:%s", self._code, self._df5mKline.tail().to_string())
    
    def TimerToDo(self, calback):
        self.OnTick(GetRealTimeQuote(self._code), calback)