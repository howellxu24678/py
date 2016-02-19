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


logging.config.fileConfig(os.path.join(os.getcwd(), "..", baseconfdir, loggingconf))
logger = logging.getLogger()

def td(kline):
    iCount = -1
    isNeedBuy = False
    isNeedSell = False
    
    curRow = kline.ix[iCount]
    #第n根，close >= ma60 且为阳线或者十字星，然后开始从后往前看是否满足要求
    if curRow['close'] >= curRow['ma60'] and curRow['close'] >= curRow['open']:
        iCount = iCount - 1
        curRow = kline.ix[iCount]
        #从第n-1一直到倒数第2根，close >= ma60
        while (max(curRow['close'], kline.ix[iCount + 1]['open']) >= curRow['ma60'] and abs(iCount) < 10):
            dMin = min(curRow['open'], kline.ix[iCount - 1]['close'])
            #第1根K线 open <= ma60 <= close (即第一根为被ma60穿过实体的阳线或者十字星)
            if abs(iCount) >= 3 and dMin <= curRow['ma60'] and curRow['ma60'] <= curRow['close']:
                isNeedBuy = True
                break
            else:
                iCount = iCount - 1
                curRow = kline.ix[iCount]

    #第n根，close <= ma60 且为阴线或者十字星，然后开始从后往前看是否满足要求
    elif curRow['close'] <= curRow['ma60'] and curRow['close'] <= curRow['open']:
        iCount = iCount - 1
        curRow = kline.ix[iCount]
        #从第n-1一直到倒数第2根，close <= ma60
        while (curRow['close'] <= curRow['ma60'] and abs(iCount) < 10):
            dMax = max(curRow['open'], kline.ix[iCount - 1]['close'])
            #第1根K线 open >= ma60 >= close (即第一根为被ma60穿过实体的阴线或者十字星)
            if abs(iCount) >= 3 and dMax >= curRow['ma60'] and curRow['ma60'] >= curRow['close']:
                isNeedSell = True
                break
            else:
                iCount = iCount - 1
                curRow = kline.ix[iCount]
                
    return isNeedBuy,isNeedSell


class Twine(object):
    def __init__(self):
        self._df = pd.DataFrame(columns={'high', 'low'})
        self._df.loc[pd.to_datetime(datetime.datetime.now())] = {'high':60.2, 'low':32.3}
        pass

    #是否存在包含关系
    def isContain(self, pre_line, curkline):
        #向左包含 n+1包含n
        if curkline['high'] >= pre_line['high'] and curkline['low'] <= pre_line['low']:
            return  True
        #向右包含 n包含n+1
        elif curkline['high'] <= pre_line['high'] and curkline['low'] >= pre_line['low']:
            return  True
        else:
            return  False

    #判断是上升趋势还是下降趋势,True为上升趋势，False为下降趋势
    def upOrDown(self, line1, line2):
        if line2['high'] >= line1['high'] and line2['low'] >= line1['low']:
            return True
        else:
            return False


    def contain(self, curkline):
        if len(self._df) < 1:
            self._df.loc[curkline['time']] = {'high':curkline['high'],
                                              'low':curkline['low']}
            return

        if len(self._df) < 2:
            if self.isContain(self._df.ix[-1], curkline):
                pass


        if self.isContain(self._df.ix[-1], curkline):
            if self.upOrDown(self._df.ix[-2], self._df.ix[-1]):
                self._df.loc[curkline['time']] = {'high': max(self._df.ix[-1]['high'], curkline['high']),\
                                                  'low': max(self._df.ix[-1]['low'], curkline['low'])}
            else:
                self._df.loc[curkline['time']] = {'high': min(self._df.ix[-1]['high'], curkline['high']),\
                                                  'low': min(self._df.ix[-1]['low'], curkline['low'])}
            #处理完包含关系后，将前一个删除，只保留最终处理完的结果
            self._df = self._df.drop(pd.Timestamp(self._df.index.values[-2]))





hqDataDir = "D:\TdxW_HuaTai\T0002\export"


code = '002588'
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
                
                
if __name__ == "__main__":
    backtest("002588")

    


