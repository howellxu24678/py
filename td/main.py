# -*- coding: utf-8 -*-
import logging 
import logging.config
import trade
import strategy
import os
import ConfigParser 

baseconfdir="conf"
loggingconf= "logging.config"
quickfixconf= "quickfix.ini"
businessconf= "business.ini"

try:
    logging.config.fileConfig(os.path.join(os.getcwd(), baseconfdir, loggingconf))
    logger = logging.getLogger()

    cf = ConfigParser.ConfigParser()
    cf.read(os.path.join(os.getcwd(), baseconfdir, businessconf))
    
    role = cf.get("DEFAULT", "role")
    codelist = cf.get(role, "codelist")
    logger.info("role:%s, codelist:%s", *(role, codelist))
    
    
    if role == "signal":
        for code in codelist.split(','):
            logger.info("begin to start Stg_td_signal with code:%s", code)
            strategy.Stg_td_signal(cf, code).start()
            
    elif role == "trader":
        logger.info("begin to start trader")
        trader = trade.gui_trade()
        
        for code in codelist.split(','):
            logger.info("begin to start Stg_td_trade with code:%s", code)
            strategy.Stg_td_trade(cf, code, trader).start()


except BaseException,e:
    print(e)

#trader = trade.fix_trade(os.path.join(os.getcwd(), baseconfdir, quickfixconf))
#trader.create()
#trader.UAN(9)
#trader.NewStockOrder()

#while(True):
#    pass


