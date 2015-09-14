# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 18:13:52 2015

@author: guosen
"""
#import trade
#import quote

from apscheduler.schedulers.background import BackgroundScheduler
import sendmail
import datetime

class Stg_td(object):
    def __init__(self, quote_, trade_):
        self.__quote = quote_
        self.__trade = trade_
        
        self.__sched  = BackgroundScheduler()
        #self.__sendmail = sendmail.sendmail('smtp.163.com', 'xujhaosysu@163.com', '465513')
        self.__sendmail = sendmail.sendmail('smtp.qq.com', '727513059@qq.com', '0730xujh')
        self.__curNotifyStatus = 'init'
    
    def start(self):
        self.__sched.add_job(self.__quote.TimerToDo, 'interval', args=(self.OnNewKLine,),  seconds=3)
        self.__sched.start()
        print "Stg_td start"
        
    def stop(self):
        self.__sched.shutdown()
    
    def td(self, kline):
        iCount = -1
        isNeedBuy = False
        isNeedSell = False
        
        curRow = kline.ix[iCount]
        #{µÚn¸ù£¬close > ma60 ÇÒÎªÑôÏß£¬È»ºó¿ªÊ¼´ÓºóÍùÇ°¿´ÊÇ·ñÂú×ãÒªÇó}
        if curRow['close'] > curRow['ma60'] and curRow['close'] >= curRow['open']:
            iCount = iCount - 1
            curRow = kline.ix[iCount]
            #{´ÓµÚn-1Ò»Ö±µ½µ¹ÊýµÚ2¸ù£¬close > ma60}
            while (curRow['close'] >= curRow['ma60'] and abs(iCount) < 10):
                dMin = min(curRow['open'], kline.ix[iCount - 1]['close'])
                #{µÚ1¸ùKÏß open< ma60 < close (¼´µÚÒ»¸ùÎª±»ma60´©¹ýÊµÌåµÄÑôÏß)}
                if abs(iCount) >= 3 and dMin < curRow['ma60'] and curRow['ma60'] < curRow['close']:
                    isNeedBuy = True
                    break
                else:
                    iCount = iCount - 1
                    
        #{µÚn¸ù£¬close < ma60 ÇÒÎªÒõÏß£¬È»ºó¿ªÊ¼´ÓºóÍùÇ°¿´ÊÇ·ñÂú×ãÒªÇó}
        elif curRow['close'] < curRow['ma60'] and curRow['close'] < curRow['open']:
            iCount = iCount - 1
            curRow = kline.ix[iCount]
            #{´ÓµÚn-1Ò»Ö±µ½µ¹ÊýµÚ2¸ù£¬close < ma60}
            while (curRow['close'] <= curRow['ma60'] and abs(iCount) < 10):
                dMax = max(curRow['open'], kline.ix[iCount - 1]['close'])
                #{µÚ1¸ùKÏß open< ma60 < close (¼´µÚÒ»¸ùÎª±»ma60´©¹ýÊµÌåµÄÑôÏß)}
                if abs(iCount) >= 3 and dMax > curRow['ma60'] and curRow['ma60'] > curRow['close']:
                    isNeedSell = True
                    break
                else:
                    iCount = iCount - 1
                    
        return isNeedBuy,isNeedSell
                
        
        
    def OnNewKLine(self, kline):
        isNeedBuy, isNeedSell = self.td(kline)
        if isNeedBuy:
            #ç¶æä¸ä¹åä¸è´ï¼ä»£è¡¨ä¹åå·²ç»åéè¿ä¿¡å·ï¼æ­¤æ¶ä¸éè¦åè¿è¡åéäº
            if self.__curNotifyStatus == 'buy':
                return 
            
            #ä¸ä¸è´ååéä¿¡å
            self.__curNotifyStatus = 'buy'
            print 'sendmail code:%s, 5min buy'%self.__quote.GetCode()
            if self.__quote.GetCode() in ['600807', '200152']:
                self.__sendmail.send('code:%s, 5min buy'%(self.__quote.GetCode()), ['727513059@qq.com','6661651@qq.com'])
            else:
                self.__sendmail.send('code:%s, 5min buy'%(self.__quote.GetCode()), ['727513059@qq.com',])
        if isNeedSell:
            if self.__curNotifyStatus == 'sell':
                return
                
            self.__curNotifyStatus = 'sell'
            print 'sendmail code:%s, 5min sell'%self.__quote.GetCode()
            if self.__quote.GetCode() in ['600807', '200152']:
                self.__sendmail.send('code:%s, 5min sell'%(self.__quote.GetCode()), ['727513059@qq.com','6661651@qq.com'])
            else:
                self.__sendmail.send('code:%s, 5min sell'%(self.__quote.GetCode()), ['727513059@qq.com',])