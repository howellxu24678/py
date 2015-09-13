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
        self.__sendmail = sendmail.sendmail('smtp.163.com', 'xujhaosysu@163.com', '465513')
        
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
        #{第n根，close > ma60 且为阳线，然后开始从后往前看是否满足要求}
        if curRow['close'] > curRow['ma60'] and curRow['close'] >= curRow['open']:
            iCount = iCount - 1
            curRow = kline.ix[iCount]
            #{从第n-1一直到倒数第2根，close > ma60}
            while (curRow['close'] >= curRow['ma60'] and abs(iCount) < 10):
                dMin = min(curRow['open'], kline.ix[iCount - 1]['close'])
                #{第1根K线 open< ma60 < close (即第一根为被ma60穿过实体的阳线)}
                if abs(iCount) >= 3 and dMin < curRow['ma60'] and curRow['ma60'] < curRow['close']:
                    isNeedBuy = True
                    break
                else:
                    iCount = iCount - 1
                    
        #{第n根，close < ma60 且为阴线，然后开始从后往前看是否满足要求}
        elif curRow['close'] < curRow['ma60'] and curRow['close'] < curRow['open']:
            iCount = iCount - 1
            curRow = kline.ix[iCount]
            #{从第n-1一直到倒数第2根，close < ma60}
            while (curRow['close'] <= curRow['ma60'] and abs(iCount) < 10):
                dMax = max(curRow['open'], kline.ix[iCount - 1]['close'])
                #{第1根K线 open< ma60 < close (即第一根为被ma60穿过实体的阳线)}
                if abs(iCount) >= 3 and dMax > curRow['ma60'] and curRow['ma60'] > curRow['close']:
                    isNeedSell = True
                    break
                else:
                    iCount = iCount - 1
                    
        return isNeedBuy,isNeedSell
                
        
        
    def OnNewKLine(self, kline):
        isNeedBuy, isNeedSell = self.td(kline)
        if isNeedBuy:
            #状态与之前一致，代表之前已经发送过信号，此时不需要再进行发送了
            if self.__curNotifyStatus == 'buy':
                return 
            
            #不一致则发送信号
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