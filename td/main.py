# -*- coding: utf-8 -*-
import logging 
import logging.config
import trade
import quote
import strategy
import os
import datetime

baseconfdir="conf"
loggingconf= "logging.config"
quickfixconf= "quickfix.ini"

logdir='log'
logfilepath = os.path.join(os.getcwd(), logdir, datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')+'td.log')

logging.config.fileConfig(os.path.join(os.getcwd(), baseconfdir, loggingconf))
logger = logging.getLogger("example02")


trader = trade.fix_trade(os.path.join(os.getcwd(), baseconfdir, quickfixconf))
trader.create()
#trader.UAN(9)
#trader.NewStockOrder()

#code = '002407'
#q5mk = quote.Quote5mKline(code)

codelist = ['600807', '200152','002407']
for code in codelist:
    strategy.Stg_td(quote.Quote5mKline(code), trader).start()


#while(True):
#    pass

#stgtd.stop()

