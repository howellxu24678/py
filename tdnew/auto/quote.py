# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 17:11:33 2015

@author: guosen
"""

import os

from apscheduler.schedulers.background import BackgroundScheduler
import talib as ta
import pandas as pd

from util import *

logger = logging.getLogger()
from eventengine import *
    
    
#根据传入的代码列表批量获取实时行情，并将行情通过dict - code2handle 找到对应的句柄调用各自代码的处理函数
class RealTimeQuote(object):
    def __init__(self, cf, codelist, eventEngine_):
        self._codelist = codelist
        logger.info("codelist:%s", self._codelist)
        self._eventEngine = eventEngine_
        #self._eventEngine.register(EVENT_TIMER, self.TimerCall)
        self._sched  = BackgroundScheduler()

    def start(self):
        self._sched.add_job(self.TimerCall, 'interval',  seconds=3)
        self._sched.start()
        logger.info('RealTimeQuote start')

    def stop(self):
        logger.info('RealTimeQuote stop')
        self._sched.shutdown()

    def TimerCall(self):
        '''
        定时根据代码列表获取最新行情
        :return:
        '''
        if len(self._codelist) < 1:
            return

        rtQuote = GetRealTimeQuote(self._codelist)
        for i in range(rtQuote.shape[0]):
            itQuote = rtQuote.ix[i]
            if float(itQuote['amount']) <= 0.01:
                continue
            event = Event(type_=EVENT_MARKETDATA_CONTRACT + itQuote['code'])
            event.dict_['tick'] = itQuote
            self._eventEngine.put(event)

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
        filepath = os.path.join(hqdatadir, (self._code + '.txt'))
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
        self._name = open(filepath).readline().split(' ')[1].decode('gbk').encode('utf-8')
        
    def CheckHistoryData(self):
        dataLastDay = self._df5mKline.index[-1].date()
        if not IsLastTradingDay(dataLastDay):
            logger.critical("code:%s the history data is out of date, lastday:%s", self._code, dataLastDay)
            raise RuntimeError, 'the history data is out of date'
            
       
        
    def CheckIfInTheMarketTimeRange(self, time):
        for i in range(len(self._marketimerange)):
            if time >= self._marketimerange[i][0] and time <= self._marketimerange[i][1]:
                return True
        return False
        
    def OnTick(self, tick, calback):
        if not self.CheckIfInTheMarketTimeRange(tick['time']):
            logger.warn("code:%s, time:%s is not in the market time range", self._code, tick['time'])            
            return
            
        #当前传过来的Tick价格
        curTickPrice = float(tick['price'])
        #当前传过来的Tick时间（加上当前日期）
        curTickDatetime = GetDatetimeFromTime(tick['time'])
        
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
                
        logger.info("code:%s, kline: \n %s", self._code, self._df5mKline.tail().to_string())