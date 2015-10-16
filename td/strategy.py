# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 18:13:52 2015

@author: guosen
"""
#import trade
#import quote


import sendmail
import quote
from util import *
import logging
logger = logging.getLogger("run")


class Strategy(object):
    def __init__(self, cf, code):
        self._code = code
        self._quote = quote.Quote5mKline(cf, code)     
        self._latestStatus = 'init'

        
    def OnTick(self, tick):
        logger.debug("code：%s OnTick", self._code)        
        self._quote.OnTick(tick, self.OnNewKLine)
        self.OnTimerCall()
        
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
            
    def OnTimerCall(self):
        logger.debug("code：%s OnTimerCall", self._code)
            
    def DealBuy(self):
        pass
    
    def DealSell(self):
        pass
        
class Stg_Signal(Strategy):
    def __init__(self, cf, code):
        super(Stg_Signal, self).__init__(cf, code)
        self._sendmail = sendmail.sendmail(cf.get("DEFAULT", "smtp_server"),
                            cf.get("DEFAULT", "from_addr"),
                            cf.get("DEFAULT", "password"),
                            "Signal")
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
        self._sendmail = sendmail.sendmail(cf.get("DEFAULT", "smtp_server"),
            cf.get("DEFAULT", "from_addr"),
            cf.get("DEFAULT", "password"),
            "Autotrader")
        self._trade = trade_
        self._todayHaveBuy = False
        self._bNeedToSellAtOpen = False
        self._sellTime = datetime.datetime.strptime(cf.get("autotrader", "selltime"), "%H:%M").time()
        self._stock_number = cf.get("autotrader", self._code)
        self.GenToAddrList(cf)
        self._iBuyIndex, self._iSellIndex = self.LookBackRealBuySellPoint()
        
        self._lastBuyPoint = self._quote._df5mKline.index[self._iBuyIndex-1]
        self._lastSellPoint = self._quote._df5mKline.index[self._iSellIndex-1]
        logger.info("code:%s, lastBuyPoint:%s, lastSellPoint:%s", 
                    self._code, self._lastBuyPoint, self._lastSellPoint)
                    
        self.LookBackToGetSignal()
        
        if self.IsNeedToSellAtOpen():
            self._bNeedToSellAtOpen = True
            logger.info("code:%s NeedToSellAtOpen sellTime:%s", self._code, self._sellTime) 
            

                    
    #检测需不需要在开盘卖掉（如果最后一个真实的买入信号发生在上一个交易日，并且最后一个是卖出信号）
    def IsNeedToSellAtOpen(self):
        if IsLastTradingDay(self._lastBuyPoint.date()) and self._latestStatus == 'sell':
            return True
        return False 
             
        
        
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
            
    def OnTimerCall(self):
        if self._bNeedToSellAtOpen and datetime.datetime.now().time() > self._sellTime:
            logger.info("deal the sell at open issue")
            self.DealSell()
            self._bNeedToSellAtOpen = False
            
        
    def DealBuy(self):
        logger.info("start to buy:%s with number:%s", self._code, self._stock_number)
        if self._trade.buy(self._code, self._stock_number, None):
            msg = "success to buy:%s with number:%s"%(self._code, self._stock_number)
            logger.info(msg)
            self._sendmail.send(msg, self._to_addr_list)
        else:
            msg = "failed to buy:%s with number:%s"%(self._code, self._stock_number)
            logger.info(msg)
            self._sendmail.send(msg, self._to_addr_list)
    
    def DealSell(self):
        if self._todayHaveBuy:
            logger.warn("code:%s today have buy, so cant sell today")
        
        logger.info("start to sell:%s with number:%s", self._code, self._stock_number)
        if self._trade.buy(self._code, self._stock_number, None):
            msg = "success to sell:%s with number:%s"%(self._code, self._stock_number)
            logger.info(msg)
            self._sendmail.send(msg, self._to_addr_list)
        else:
            msg = "failed to sell:%s with number:%s"%(self._code, self._stock_number)
            logger.info(msg)
            self._sendmail.send(msg, self._to_addr_list)