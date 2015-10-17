# -*- coding: utf-8 -*-
import logging 
import logging.config
import trade
import strategy
import quote
import os
import ConfigParser 

baseconfdir="conf"
loggingconf= "logging.config"
quickfixconf= "quickfix.ini"
businessconf= "business.ini"

try:
    logging.config.fileConfig(os.path.join(os.getcwd(), baseconfdir, loggingconf))
    logger = logging.getLogger("run")

    cf = ConfigParser.ConfigParser()
    cf.read(os.path.join(os.getcwd(), baseconfdir, businessconf))
    
    role = cf.get("DEFAULT", "role")
    codelist = cf.get(role, "codelist").split(',')
    logger.info("role:%s, codelist:%s", role, codelist)
    
    code2handle = {}
    
    if role == "signal":
        for code in codelist:
            logger.info("create Stg_Signal with code:%s", code)
            code2handle[code] = strategy.Stg_Signal(cf, code)
            
    elif role == "autotrader":
        logger.info("create gui_trade")
        trader = trade.gui_trade(cf)
        
        for code in codelist:
            logger.info("create Stg_Autotrader with code:%s", code)
            code2handle[code] = strategy.Stg_Autotrader(cf, code, trader)
    
    logger.info("create and start RealTimeQuote schedule")
    quote.RealTimeQuote(cf, codelist, code2handle).start()
    
except BaseException,e:
    logger.exception(e)

#trader = trade.fix_trade(os.path.join(os.getcwd(), baseconfdir, quickfixconf))
#trader.create()
#trader.UAN(9)
#trader.NewStockOrder()

#while(True):
#    pass


