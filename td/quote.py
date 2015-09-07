# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 17:11:33 2015

@author: guosen
"""

import tushare as ts
import datetime,time
from apscheduler.schedulers.background import BackgroundScheduler
import talib as ta
import logging
import pandas as pd
import numpy as np
logging.basicConfig()


def GetDayBefore(dayoffset):
    return datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=dayoffset), '%Y-%m-%d')
        
def GetRehabGene(code):
        #无复权日线        
    dfnfq1d = ts.get_hist_data(code,start=GetDayBefore(30),end=GetDayBefore(1))
        
    dffq1d = ts.get_h_data(code,start=GetDayBefore(30),end=GetDayBefore(1))
        
    rate = dffq1d['close'] / dfnfq1d['close']
    print rate
    
def GetRealTimeQuote(code):
    print 'time:',time.strftime("%H:%M:%S",time.localtime())
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
    print "minSlice:%d" %(minSlice)
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
        self.__df5mKline = GetHistData(code, '5')
        ma60 = ta.SMA(self.__df5mKline['close'].values, 60)
        ma60 = ma60.round(2)
        self.__df5mKline['ma60'] = ma60
        print self.__df5mKline
        
    def OnTick(self, tick):
        print 'onTick'
        #当前传过来的Tick价格
        curTickPrice = float(tick['price'].values[0])
        #当前传过来的Tick时间（加上当前日期）
        curTickDatetime = GetDatetimeFromTime(tick['time'].values[0])
        
        curTimeSlice = GetTimeSlice(curTickDatetime, 5)        
        strTimeSlice = Datetime2Str(curTimeSlice)
        
        strLastTimeStamp = self.__df5mKline.index.values[-1]
        lastTimeStamp = Str2Datetime(strLastTimeStamp)
        
        curMa60 = GetSMA(self.__df5mKline['close'].values[-60:])
        
        if(curTimeSlice > lastTimeStamp):
            self.__df5mKline.loc[strTimeSlice] = {'open':curTickPrice,'high':curTickPrice, 'close':curTickPrice, 'low':curTickPrice, 'volume': 0.0, 'ma60':curMa60}
            
        else:
            self.__df5mKline.loc[strLastTimeStamp, 'close'] = curTickPrice
            lastHigh = self.__df5mKline.loc[strLastTimeStamp, 'high']
            lastLow = self.__df5mKline.loc[strLastTimeStamp, 'low']
            self.__df5mKline.loc[strLastTimeStamp, 'high'] = max(curTickPrice, lastHigh) 
            self.__df5mKline.loc[strLastTimeStamp, 'low'] = min(curTickPrice, lastLow)
            
        print self.__df5mKline
            
        
#GetRehabGene('600783')

code = '000609'
q5mk = Quote5mKline(code)
#q5mk.OnTick(GetRealTimeQuote('000001'))
#q5mk.OnTick(GetRealTimeQuote('000001'))

def TimerToDo(_code):
    q5mk.OnTick(GetRealTimeQuote(_code))

sched = BackgroundScheduler()

# Schedule job_function to be called every two hours
#sched.add_job(TimerToDo, 'interval', args=(GetRealTimeQuote('000001'),),  seconds=3)
sched.add_job(TimerToDo, 'interval', args=(code,),  seconds=3)
#
sched.start()
print "hello"


#df = GetHistData('000001','5')
#ma60 = ta.SMA(df['close'].values, 60)
#ma60 = ma60.round(2)
#df['ma60'] = ma60
#
#strlastimestamp = df.index.values[-1]
#lastimestamp = datetime.datetime.strptime(strlastimestamp, "%Y-%m-%d %H:%M:%S")
#timenew = lastimestamp + datetime.timedelta(minutes=5)
#
#print timenew.strftime("%Y-%m-%d %H:%M:%S")


#df.loc[timenew]=[1.1,1.1,1.1,1.1,1.1,600]

#newQuote = GetRealTimeQuote('000001')
#curdatetime = datetime.datetime.strptime(datetime.datetime.strftime(datetime.date.today(),'%Y-%m-%d') + ' ' + newQuote['time'].values[0], "%Y-%m-%d %H:%M:%S")
#df.loc[timenew]={'close':125,'open':112,'high':113,'low':114,'volume':60000,'ma60':10.21}


###test###
df = GetHistData('000609', '5')
ma60 = ta.SMA(df['close'].values, 60)
ma60 = ma60.round(2)
df['ma60'] = ma60