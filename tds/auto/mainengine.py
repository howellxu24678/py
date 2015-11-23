# -*- coding: utf-8 -*-
__author__ = 'xujh'

from eventengine import *
from ma import *
from datetime import datetime
import base64
logger = logging.getLogger("run")

class MainEngine(object):
    def __init__(self, cf):
        self._eventEngine = EventEngine(cf.getint("ma", "timer"))
        self._todolist = cf.get("ma", "todolist").strip().split(',')
        logger.info("todolist:%s", self._todolist)

        self._trade = Ma(cf, self._eventEngine)
        self._eventEngine.register(EVENT_TIMER, self.onTimer)
        self._eventEngine.register(EVENT_AXEAGLE, self.AxeagleListen)

        self._eventEngine.start()

    def logon(self):
        self._trade.logonEa()



    def onTimer(self,event):
        try:
            for func in self._todolist:
                logger.debug("timer to run %s", getattr(self._trade, func))
                getattr(self._trade, func)()
        except BaseException,e:
            logger.exception(e)

    def AxeagleListen(self,event):
        pass