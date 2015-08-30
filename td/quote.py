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
    df = ts.get_realtime_quotes(code)
    print df[['code','name','price','bid','ask','volume','amount','time']]
    print 'time:',time.strftime("%H:%M:%S",time.localtime())
    
    
def GetHistData(code,_ktype):
    df = ts.get_hist_data(code, ktype=_ktype)
    return df[['open','high','close','low','volume']]
    
    
#GetRehabGene('600783')


#sched = BackgroundScheduler()
#
## Schedule job_function to be called every two hours
#sched.add_job(GetRealTimeQuote, 'interval', args=('600000',),  seconds=3)
#
#sched.start()
#print "hello"


df = GetHistData('000001','5')
ma60 = ta.SMA(df['close'].values, 60)
ma60 = ma60.round(2)






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