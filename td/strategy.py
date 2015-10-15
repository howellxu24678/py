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


class Strategy(object):
    def __init__(self, cf, code):
        self._code = code
        self._quote = quote.Quote5mKline(cf, code)
        self._sched  = BackgroundScheduler(logger = logging.getLogger("schedule"))
        self._latestStatus = 'init'
        self._sendmail = sendmail.sendmail(cf.get("DEFAULT", "smtp_server"),
                                    cf.get("DEFAULT", "from_addr"),
                                    cf.get("DEFAULT", "password"))
    
    def start(self):
        self._sched.add_job(self._quote.TimerToDo, 'interval', args=(self.OnNewKLine,),  seconds=3)
        self._sched.start()
        logger.info('Strategy start')
        
    def stop(self):
        self._sched.shutdown()
        
    def OnNewKLine(self, kline):
        isNeedBuy, isNeedSell = td(kline)
        if isNeedBuy:
            if self._latestStatus == 'buy':
                return 
            
            self._latestStatus = 'buy'
            self.DealBuy()

            
        if isNeedSell:
            if self._latestStatus == 'sell':
                return
                
            self._latestStatus = 'sell'
            self.DealSell()
            
    def DealBuy(self):
        pass
    
    def DealSell(self):
        pass
        
class Stg_Signal(Strategy):
    def __init__(self, cf, code):
        super(Stg_Signal, self).__init__(cf, code)
        self.GenToAddrList(cf)
                
    def GenToAddrList(self, cf):
        toaddr_codelist = {}
        reveivers = cf.get("signal", "reveiver")
        reveivers = reveivers.split(',')
        
        for reveiver in reveivers:
            toaddr_codelist[reveiver] = cf.get("signal", reveiver).split(',')
            
        self._to_addr_list = []
        for toaddr,codelist in toaddr_codelist.items():
            if self._code in codelist:
                self._to_addr_list.append(toaddr)
                
        if len(self._to_addr_list) < 1:
            logger.warn("code:%s cant find the to_addr, will send to the from_addr:%s",
                        self._code, cf.get("signal", "from_addr"))
            self._to_addr_list.append(cf.get("signal", "from_addr"))
            
    def SendMail(self, status):
        logger.info('sendmail code:%s, 5min %s, to_addr:%s', self._code, status, self._to_addr_list)
        self._sendmail.send('code:%s, 5min %s' % (self._code, status), self._to_addr_list)
        
    def DealBuy(self):
        self.SendMail('buy')
    
    def DealSell(self):
        self.SendMail('sell')
        
    
class Stg_Autotrader(Strategy):
    def __init__(self, cf, code, trade_):
        super(Stg_Autotrader, self).__init__(cf, code)
        self._trade = trade_
        self._todayHaveBuy = False
        self.GenToAddrList(cf)
        self._iBuyIndex, self._iSellIndex = self.LookBackRealBuySellPoint()
        
        self._lastBuyPoint = self._quote._df5mKline.index[self._iBuyIndex-1]
        self._lastSellPoint = self._quote._df5mKline.index[self._iSellIndex-1]
        logger.info("code:%s, lastBuyPoint:%s, lastSellPoint:%s", 
                    self._code, self._lastBuyPoint, self._lastSellPoint)
                    
        self.LookBackToGetSignal()

        
    def GenToAddrList(self, cf):
        self._to_addr_list = []
        #需要将交易摘要发送给的接收者邮箱
        for toaddr in cf.get("autotrader", "reveiver").split(','):
            self._to_addr_list.append(toaddr)
            
    #往前回溯获取上一个有效信号
    def LookBackToGetSignal(self):
        for i in xrange(self._quote._df5mKline.shape[0], 61, -1):
            isNeedBuy, isNeedSell = td(self._quote._df5mKline[:i])
            if isNeedBuy or isNeedSell:
                break
        if isNeedBuy:
            self._latestStatus = 'buy'
        elif isNeedSell:
            self._latestStatus = 'sell'
            
        logger.info("LookBackToGetSignal and set the _latestStatus to %s", self._latestStatus)
        
            
    def LookBackRealBuySellPoint(self):
        iBuyIndex = 0
        iSellIndex = 0
        isHaveFoundBuy = False
        isHaveFoundSell = False
        lastHitStatus = 'init'
        
        for i in xrange(self._quote._df5mKline.shape[0], 61, -1):
            isNeedBuy, isNeedSell = td(self._quote._df5mKline[:i])
            if isNeedBuy or isNeedSell:
                if isNeedBuy:
                    if lastHitStatus == 'sell':
                        isHaveFoundSell = True
                    
                    lastHitStatus = 'buy'
                    if not isHaveFoundBuy:
                        iBuyIndex = i
                    
                if isNeedSell:
                    if lastHitStatus == 'buy':
                        isHaveFoundBuy = True
                        
                    lastHitStatus = 'sell'
                    if not isHaveFoundSell:
                        iSellIndex = i
                    
            if isHaveFoundBuy and isHaveFoundSell:
                break
            
        return iBuyIndex,iSellIndex
            
    def DealBuy(self):
        if self._todayHaveBuy:
            logger.info("code:%s today have buy, so dont want to buy again", 
                        *(self._code,))            
            return
            
        self._todayHaveBuy = True
        pass
    
    def DealSell(self):
        #if self._todayHaveBuy
        pass