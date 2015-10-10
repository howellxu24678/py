# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 10:53:59 2015

@author: xujhao
"""
import datetime

import talib as ta
import pandas as pd
import numpy as np
import os
import logging
import logging.config
#logger = logging.getLogger("example02")

baseconfdir="conf"
loggingconf= "logging.config"
quickfixconf= "quickfix.ini"

logdir='log'
logfilepath = os.path.join(os.getcwd(), logdir, datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')+'td.log')

logging.config.fileConfig(os.path.join(os.getcwd(), baseconfdir, loggingconf))
logger = logging.getLogger("example02")

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

hqDataDir = "D:\TdxW_HuaTai\T0002\export"


code = '002475'
rnames = ['d','t', 'open', 'high', 'low', 'close', 'volume', 'amt']
df5mKline = pd.read_table(r"%s\%s.txt"%(hqDataDir, code), 
                          engine='python', sep = ',', 
                          encoding='gbk', 
                          names=rnames, 
                          parse_dates = {'time':['d','t']},
                          index_col='time', 
                          skiprows=2, 
                          skipfooter=1)
                                         
ma60_ = ta.SMA(df5mKline['close'].values, 60)
df5mKline['ma60'] = ma60_
df5mKline.fillna(0.)

def backtest(code):
    rnames = ['d','t', 'open', 'high', 'low', 'close', 'volume', 'amt']
    df5mKline = pd.read_table(r"%s\%s.txt"%(hqDataDir, code), 
                              engine='python', sep = ',', 
                              encoding='gbk', 
                              names=rnames, 
                              parse_dates = {'time':['d','t']},
                              index_col='time', 
                              skiprows=2, 
                              skipfooter=1)
                                             
    ma60_ = ta.SMA(df5mKline['close'].values, 60)
    df5mKline['ma60'] = ma60_
    df5mKline.fillna(0.)
    
    curPosition = 0
    rop = 1
    lastSignal = 'init'
    
    for i in xrange(63,df5mKline.shape[0]):
        isNeedBuy, isNeedSell = td(df5mKline[:i])
        
        if isNeedBuy:
            lastSignal = "buy"
            if curPosition < 1:
                curPosition = curPosition + 1
                buyPrice = df5mKline.ix[i-1]['close']
                lastBuyTime = df5mKline.index[i-1]
                rop = rop * (1 - 0.0013)
                logger.info('code:%s buy at:%s with price: %s: rop:%s',
                            *(code,
                              datetime.datetime.strftime(lastBuyTime, "%Y-%m-%d %H:%M:%S"),
                              buyPrice,
                              rop))
            
        if isNeedSell or lastSignal == "sell":
            if isNeedSell:
                lastSignal = "sell"
                
            curSellTime = df5mKline.index[i-1]
            if curPosition > 0 and curSellTime.date() - lastBuyTime.date() >= datetime.timedelta(1):                
                sellPrice = df5mKline.ix[i-1]['close']
                rop = rop + (sellPrice - buyPrice) / buyPrice * (1 - 0.0013)
                logger.info('code:%s sell at:%s with price: %s: income:%s rop:%s',
                            *(code,
                              datetime.datetime.strftime(curSellTime, "%Y-%m-%d %H:%M:%S"),
                              sellPrice,
                              sellPrice - buyPrice,
                              rop))
                curPosition = curPosition - 1
                
                
                
    


