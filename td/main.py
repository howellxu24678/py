# -*- coding: utf-8 -*-
import logging 
import logging.config
from autotrade.trade.trade_tdx import *
from autotrade import strategy
from autotrade import quote
import os
import ConfigParser 

baseconfdir="conf"
loggingconf= "logging.config"
quickfixconf= "quickfix.ini"
businessconf= "business.ini"

def DealSignal(logger, cf):
    codelist = cf.get("signal", "codelist").split(',')
    logger.info("signal, codelist:%s", codelist)
    code2handle = {}
    for code in codelist:
        logger.info("create Stg_Signal with code:%s", code)
        code2handle[code] = strategy.Stg_Signal(cf, code)
    return codelist, code2handle
    

def DealAutoTrade(trader, logger, cf):
    codelist = cf.get("autotrader", "codelist").split(',')
    logger.info("autotrader, codelist:%s", codelist)
    code2handle = {}
    for code in codelist:
        logger.info("create Stg_Autotrader with code:%s", code)
        code2handle[code] = strategy.Stg_Autotrader(cf, code, trader)
    return codelist, code2handle

try:
    logging.config.fileConfig(os.path.join(os.getcwd(), baseconfdir, loggingconf))
    logger = logging.getLogger("run")

    cf = ConfigParser.ConfigParser()
    cf.read(os.path.join(os.getcwd(), baseconfdir, businessconf))
    
    codelistSignal = []
    code2SignalHandle = {}
    codelistAutoTrade = []
    code2AutoTradeHandle = {}
    
    if(cf.getboolean("signal", "enable")):
        codelistSignal, code2SignalHandle = DealSignal(logger, cf)
    if(cf.getboolean("autotrader", "enable")):
        logger.info("create gui_trade")
        trader = tdx_trade(cf)
        codelistAutoTrade, code2AutoTradeHandle = DealAutoTrade(trader, logger, cf)
    
    logger.info("create and start RealTimeQuote schedule")
    quote.RealTimeQuote(cf, \
    list(set(codelistSignal).union(set(codelistAutoTrade))), \
    code2SignalHandle, \
    code2AutoTradeHandle).start()
    
except BaseException,e:
    logger.exception(e)

#trader = trade.fix_trade(os.path.join(os.getcwd(), baseconfdir, quickfixconf))
#trader.create()
#trader.UAN(9)
#trader.NewStockOrder()

#while(True):
#    pass


