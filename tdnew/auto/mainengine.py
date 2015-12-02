# -*- coding: utf-8 -*-
__author__ = 'xujh'

from eventengine import *
from ma import *
from datetime import datetime
from strategy import *
from quote import *
from sendmail import *
import base64
import time
logger = logging.getLogger("run")

class MainEngine(object):
    def __init__(self, cf):
        self._eventEngine = EventEngine(cf.getint("DEFAULT", "timer"))
        self._trade = Ma(cf, self._eventEngine)
        self._mail = SendMail(cf, self._eventEngine)
        self._trade.logonEa()
        #time.sleep(5)
        self.autoTrade(cf)
        self._eventEngine.register(EVENT_TIMER, self.onTimer)
        self._eventEngine.start()


        self.isSend = False
    def autoTrade(self,cf):
        self._stglist = []
        self._codeset = set()
        if(cf.getboolean("signal", "enable")):
            codelist_sig = cf.get("signal", "codelist").split(',')
            self._codeset = self._codeset.union(set(codelist_sig))
            for code in codelist_sig:
                self._stglist.append(Stg_Signal(cf, code, self._eventEngine))

        if(cf.getboolean("autotrader", "enable")):
            codelist_autotrade = cf.get("autotrader", "codelist").split(',')
            self._codeset = self._codeset.union(set(codelist_autotrade))
            for code in codelist_autotrade:
                self._stglist.append(Stg_Autotrader(cf, code, self._eventEngine))

        #一次批量获取代码的最新行情
        self._realtimequote = RealTimeQuote(cf, list(self._codeset), self._eventEngine)
        self._realtimequote.start()

    def monitor(self,cf):
        pass

    def logon(self):
        self._trade.logonEa()

    def onTimer(self, event):
        if int(datetime.datetime.now().strftime("%H%M%S")) % 10000 == 0:
            event = Event(type_= EVENT_TRADE)
            event.dict_['direction'] = 'sell'
            event.dict_['code'] = '000012'
            event.dict_['number'] = '200'
            self._eventEngine.put(event)
            logger.info("sell 000012")

        if not self.isSend:
            event = Event(type_= EVENT_TRADE)
            event.dict_['direction'] = 'buy'
            event.dict_['code'] = '002673'
            event.dict_['number'] = '400'
            self._eventEngine.put(event)
            logger.info("buy 002673")

            # event = Event(type_= EVENT_TRADE)
            # event.dict_['direction'] = 'sell'
            # event.dict_['code'] = '000012'
            # event.dict_['number'] = '200'
            # self._eventEngine.put(event)
            # logger.info("sell 000012")
            self.isSend = True
        # try:
        #     for func in self._todolist:
        #         logger.debug("timer to run %s", getattr(self._trade, func))
        #         getattr(self._trade, func)()
        # except BaseException,e:
        #     logger.exception(e)

    def AxeagleListen(self,event):
        pass