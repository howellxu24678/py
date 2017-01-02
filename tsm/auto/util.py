# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 15:14:32 2015

@author: guosen
"""

import datetime
import tushare as ts
import numpy as np
import socket
import requests
from bs4 import BeautifulSoup

import logging
logger = logging.getLogger("run")

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
        while (curRow['close'] >= curRow['ma60'] and abs(iCount) < 10):
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
    
def IsLastTradingDay(day):
    todayweekday = datetime.date.today().weekday()
    
    if (todayweekday == 0 and datetime.date.today() - day > datetime.timedelta(days=3)) \
        or (todayweekday != 0 and datetime.date.today() - day > datetime.timedelta(days=1)):
            return False
    return True
    #!!!这里后续要补上根据节假日的判断（需要每年的国务院放假时间安排）
    

def GetDayBefore(dayoffset):
    return datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=dayoffset), '%Y-%m-%d')
        
def GetRehabGene(code):
    #无复权日线
    dfnfq1d = ts.get_hist_data(code,start=GetDayBefore(30),end=GetDayBefore(1))
        
    dffq1d = ts.get_h_data(code,start=GetDayBefore(30),end=GetDayBefore(1))
        
    rate = dffq1d['close'] / dfnfq1d['close']
    print rate
    
def GetRealTimeQuote(code):
    logger.debug("GetRealTimeQuote %s", code)
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
    minSlice = int(((curTimeTuple.tm_min / min_offset) + 1) * min_offset)
    #print "minSlice:%d" %(minSlice)
    if(minSlice > 59):
        return datetime.datetime(curTimeTuple.tm_year, curTimeTuple.tm_mon, 
                      curTimeTuple.tm_mday, curTimeTuple.tm_hour + 1, 
                      0, 0)
    return datetime.datetime(curTimeTuple.tm_year, curTimeTuple.tm_mon, 
                      curTimeTuple.tm_mday, curTimeTuple.tm_hour, 
                      minSlice, 0)
    
def GetSMA(data):
    return round(np.mean(data),2)


#将传入的时间加上当前的日期返回
def GetDatetimeFromTime(strTime):
    return Str2Datetime(datetime.datetime.strftime(datetime.date.today(),'%Y-%m-%d') + ' ' + strTime)


#检测连通性
def is_connectable(host, port):
    try:
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.settimeout(1)
        sk.connect((host, port))
        ret = True
    except Exception,e:
        ret = False
        logger.exception(e)
    sk.close()
    return ret


# 获取外网IP
def get_outer_ip():
    try:
        url = r'http://ip.cn/'
        r = requests.get(url)
        bTag = BeautifulSoup(r.text, 'html.parser', from_encoding='utf-8').find('code')
        return ''.join(bTag.stripped_strings)
    except Exception,e:
        logger.exception(e)


#结合是否周末及当年的交易所放假安排判断当天是否为交易日
#需要根据当前年份获取相应配置文件中的值（跨年时要配置临近两个年份）
def is_trade_day(_cf):
    cur_date = datetime.datetime.now().date()
    #isoweekday 从周一到周日 为1~7
    if cur_date.isoweekday() > 5:
        return False

    #将当前日期转成字符串并且去掉前补0（因为配置的休市日期为了方便统一没有前补0）
    cur_date_str = cur_date.strftime('%m.%d').lstrip('0').replace('.0', '.')
    market_close_list = _cf.get('main', 'market_close_' + cur_date.strftime('%Y')).strip().split(',')
    if cur_date_str in market_close_list:
        return False

    return True


#解析工作时间
def parse_work_time(working_time_str):
    return [x.split('~') for x in working_time_str.split(',')]


#判断当前时间是否工作时间
def is_working_time(_working_time_range):
    now_time = datetime.datetime.now().strftime("%H:%M")
    for x in _working_time_range:
        if x[0] <= now_time <= x[1]:
            return True
    return False

