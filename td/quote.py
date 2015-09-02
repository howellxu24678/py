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
    minSlice = ((curTimeTuple.tm_min / min_offset) + 1) * min_offset
    return datetime.datetime(curTimeTuple.tm_year, curTimeTuple.tm_mon, 
                      curTimeTuple.tm_mday, curTimeTuple.tm_hour, 
                      minSlice, 0)
    
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
        
        if(curTimeSlice > lastTimeStamp):
            self.__df5mKline.loc[strTimeSlice] = {'open':curTickPrice,'high':curTickPrice, 'close':curTickPrice, 'low':curTickPrice, 'volume': 0.0, 'ma60':0.0}
            
        else:
            self.__df5mKline.loc[strLastTimeStamp, 'close'] = curTickPrice
            lastHigh = self.__df5mKline.loc[strLastTimeStamp, 'high']
            lastLow = self.__df5mKline.loc[strLastTimeStamp, 'low']
            self.__df5mKline.loc[strLastTimeStamp, 'high'] = max(curTickPrice, lastHigh) 
            self.__df5mKline.loc[strLastTimeStamp, 'low'] = min(curTickPrice, lastLow)
            
        print self.__df5mKline
            
        
#GetRehabGene('600783')


#sched = BackgroundScheduler()
#
## Schedule job_function to be called every two hours
#sched.add_job(GetRealTimeQuote, 'interval', args=('600000',),  seconds=3)
#
#sched.start()
#print "hello"


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

q5mk = Quote5mKline('000001')
q5mk.OnTick(GetRealTimeQuote('000001'))
q5mk.OnTick(GetRealTimeQuote('000001'))
#df.loc[timenew]=[1.1,1.1,1.1,1.1,1.1,600]

#newQuote = GetRealTimeQuote('000001')
#curdatetime = datetime.datetime.strptime(datetime.datetime.strftime(datetime.date.today(),'%Y-%m-%d') + ' ' + newQuote['time'].values[0], "%Y-%m-%d %H:%M:%S")
#df.loc[timenew]={'close':125,'open':112,'high':113,'low':114,'volume':60000,'ma60':10.21}




#import time, os, sched 
#    
## 第一个参数确定任务的时间，返回从某个特定的时间到现在经历的秒数 
## 第二个参数以某种人为的方式衡量时间 
#schedule = sched.scheduler(time.time, time.sleep) 
#    
#def perform_command(inc): 
#    # 安排inc秒后再次运行自己，即周期运行 
#    schedule.enter(inc, 0, perform_command, (inc,)) 
#    print 'hello world, time:',time.strftime("%H:%M:%S",time.localtime())
#        
#def timming_exe(inc = 60): 
#    # enter用来安排某事件的发生时间，从现在起第n秒开始启动 
#    schedule.enter(inc, 0, perform_command, (inc,)) 
#    # 持续运行，直到计划时间队列变成空为止 
#    schedule.run() 
#        
#    
#print("show time after 10 seconds:") 
#timming_exe(3)

##无复权60分钟线
#dfnfq60m = ts.get_hist_data('600783',ktype='60',start='2015-07-06',end='2015-08-14')
#
##复权日线
#dffq1d = ts.get_h_data('600783',start='2015-07-06',end='2015-08-14')
#
##无复权日线
#dfnfq1d = ts.get_h_data('600783',autype=None,start='2015-07-06',end='2015-08-14')
#
##复权/无复权比率
#rate = (dffq1d['close'] / dfnfq1d['close'])




#sched = BlockingScheduler()
#
#@sched.scheduled_job('cron',id='showtime',second=3)
#def showtime():
#    print 'hello world, time:',time.strftime("%H:%M:%S",time.localtime())
#    
#sched.start()




#import time
##from datetime import date
#from datetime import datetime
#
#
#from apscheduler.schedulers.background import BackgroundScheduler
#
##from apscheduler.schedulers.blocking import BlockingScheduler
#
#
#def job_function():
#     print 'hello world, time:',time.strftime("%H:%M:%S",time.localtime())
#
#sched = BackgroundScheduler()
#
## Schedule job_function to be called every two hours
#sched.add_job(job_function, 'interval', seconds=3)
#
#sched.start()
#print "hello"