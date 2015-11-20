# -*- coding: utf-8 -*-
import logging 
import logging.config
from auto import strategy
from auto import quote

import os
import ConfigParser
import sys

baseconfdir="conf"
loggingconf= "logging.config"
businessconf= "business.ini"

def test():
    import time
    logconfilepath = os.path.join(os.getcwd(), baseconfdir, loggingconf)
    print logconfilepath
    logging.config.fileConfig(logconfilepath)
    logger = logging.getLogger()
    logger.debug("debug test")
    time.sleep(1)

def main():
    from auto.mainengine import MainEngine
    from PyQt4.QtCore import QCoreApplication
    """主程序入口"""
    app = QCoreApplication(sys.argv)

    logging.config.fileConfig(os.path.join(os.getcwd(), baseconfdir, loggingconf))
    logger = logging.getLogger("run")
    logger.debug("debug test")

    cf = ConfigParser.ConfigParser()
    cf.read(os.path.join(os.getcwd(), baseconfdir, businessconf))

    ee = MainEngine(cf)
    ee.logon()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()



# from ctypes import *
#
# class Test(object):
#     def __init__(self):
#         pass
#
#     def pp(self):
#         print  "Test print"
#
# te = Test()
# py_object(te)

# def DealSignal(logger, cf):
#     codelist = cf.get("signal", "codelist").split(',')
#     logger.info("signal, codelist:%s", codelist)
#     code2handle = {}
#     for code in codelist:
#         logger.info("create Stg_Signal with code:%s", code)
#         code2handle[code] = strategy.Stg_Signal(cf, code)
#     return codelist, code2handle
#
#
# def DealAutoTrade(trader, logger, cf):
#     codelist = cf.get("autotrader", "codelist").split(',')
#     logger.info("autotrader, codelist:%s", codelist)
#     code2handle = {}
#     for code in codelist:
#         logger.info("create Stg_Autotrader with code:%s", code)
#         code2handle[code] = strategy.Stg_Autotrader(cf, code, trader)
#     return codelist, code2handle
#
# try:
#     logging.config.fileConfig(os.path.join(os.getcwd(), baseconfdir, loggingconf))
#     logger = logging.getLogger("run")
#
#     cf = ConfigParser.ConfigParser()
#     cf.read(os.path.join(os.getcwd(), baseconfdir, businessconf))
#
#     codelistSignal = []
#     code2SignalHandle = {}
#     codelistAutoTrade = []
#     code2AutoTradeHandle = {}
#
#     if(cf.getboolean("signal", "enable")):
#         codelistSignal, code2SignalHandle = DealSignal(logger, cf)
#     if(cf.getboolean("autotrader", "enable")):
#         logger.info("create trade")
#         trader = trade.tdx_wa_trade(cf)
#         codelistAutoTrade, code2AutoTradeHandle = DealAutoTrade(trader, logger, cf)
#
#     logger.info("create and start RealTimeQuote schedule")
#     quote.RealTimeQuote(cf, \
#     list(set(codelistSignal).union(set(codelistAutoTrade))), \
#     code2SignalHandle, \
#     code2AutoTradeHandle).start()
#
# except BaseException,e:
#     logger.exception(e)



