# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 18:13:52 2015

@author: guosen
"""
#import trade
#import quote

from apscheduler.schedulers.background import BackgroundScheduler
import sendmail
import quote
import logging
logger = logging.getLogger()

class Stg_td(object):
    def __init__(self, cf, code):
        self._code = code
        self.__quote = quote.Quote5mKline(cf, code)
        self.__sched  = BackgroundScheduler()      
        self.__curNotifyStatus = 'init'
    
    def start(self):
        self.__sched.add_job(self.__quote.TimerToDo, 'interval', args=(self.OnNewKLine,),  seconds=3)
        self.__sched.start()
        logger.info('Stg_td start')
        
    def stop(self):
        self.__sched.shutdown()
    
    def td(self, kline):
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
                if abs(iCount) >= 3 and dMin < curRow['ma60'] and curRow['ma60'] < curRow['close']:
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
                if abs(iCount) >= 3 and dMax > curRow['ma60'] and curRow['ma60'] > curRow['close']:
                    isNeedSell = True
                    break
                else:
                    iCount = iCount - 1
                    curRow = kline.ix[iCount]
                    
        return isNeedBuy,isNeedSell
        
    def OnNewKLine(self, kline):
        isNeedBuy, isNeedSell = self.td(kline)
        if isNeedBuy:
            if self.__curNotifyStatus == 'buy':
                return 
            
            self.__curNotifyStatus = 'buy'
            self.DealBuy()

            
        if isNeedSell:
            if self.__curNotifyStatus == 'sell':
                return
                
            self.__curNotifyStatus = 'sell'
            self.DealSell()
            
    def DealBuy(self):
        pass
    
    def DealSell(self):
        pass
        
class Stg_td_signal(Stg_td):
    def __init__(self, cf, code):
        super(Stg_td_signal, self).__init__(cf, code)
        self.__sendmail = sendmail.sendmail(cf.get("signal", "smtp_server"),
                                            cf.get("signal", "from_addr"),
                                            cf.get("signal", "password"))
        
        #初始化发给自己
        self.__to_addr = cf.get("signal", "from_addr")
        
        toaddr_codelist = {}
        reveivers = cf.get("signal", "reveiver")
        reveivers = reveivers.split(',')
        
        for reveiver in reveivers:
            toaddr_codelist[reveiver] = cf.get("signal", reveiver).split(',')
            
        for toaddr,codelist in toaddr_codelist.items():
            if code in codelist:
                self.__to_addr = toaddr
                
    def SendMail(self, status):
        logger.info('sendmail code:%s, 5min %s, to_addr:%s', *(self._code, status, self.__to_addr))
        self.__sendmail.send('code:%s, 5min %s'%(self._code, status), [self.__to_addr,])
        
    def DealBuy(self):
        self.SendMail('buy')
    
    def DealSell(self):
        self.SendMail('sell')
        
    
class Stg_td_trade(Stg_td):
    def __init__(self, cf, code, trade_):
        super(Stg_td_trade, self).__init__(cf, code)
        self.__trade = trade_
        
    def DealBuy(self):
        pass
    
    def DealSell(self):
        pass