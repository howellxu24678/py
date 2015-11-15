# -*- coding: utf-8 -*-
__author__ = 'xujh'

from eventengine import *
from ma import *
from datetime import datetime
logger = logging.getLogger("run")
import time

class MainEngine(object):
    def __init__(self, cf):
        self._eventEngine = EventEngine(10000)
        time.sleep(10)
        self._trade = Ma(cf, self._eventEngine)
        self._eventEngine.register(EVENT_TIMER, self.onTimer)
        self._eventEngine.register(EVENT_AXEAGLE, self.AxeagleListen)

        self._eventEngine.start()

    def logon(self):
        self._trade.logonEa()

    def onTimer(self,event):
        print "want to logonBackend again"
        self._trade.logonBackend()
        #print u'MainEngine 处理每秒触发的计时器事件：%s' % str(datetime.now())

    def AxeagleListen(self,event):
        logger.info("pMsg:%s, iLen:%s, pAccount:%s",
                    event.dict_["pMsg"],
                    event.dict_["iLen"],
                    event.dict_["pAccount"])

        if event.dict_["pMsg"].split('\1')[0] == "40000":
            self._trade.logonBackend()






