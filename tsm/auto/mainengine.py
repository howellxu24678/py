# -*- coding: utf-8 -*-
__author__ = 'xujh'

from eventengine import *
from ma import *
from datetime import datetime
from sendmail import *
from data_type import *
import time
logger = logging.getLogger("run")

class MainEngine(object):
    def __init__(self, cf):
        self._eventEngine = EventEngine(cf.getint("DEFAULT", "timer"))
        self._trade = Ma(cf, self._eventEngine)
        self._mail = SendMail(cf, self._eventEngine)
        self._trade.logonEa()
        time.sleep(5)
        self.monitor(cf)
        self._eventEngine.register(EVENT_TIMER, self.onTimer)
        self._eventEngine.start()

        self._todolist = cf.get("ma", "todolist").strip().split(',')
        for re in requireFixColDict.iterkeys():
            pass

    def monitor(self,cf):
        pass

    def logon(self):
        self._trade.logonEa()

    def onTimer(self, event):
        for fundid in self._todolist:
            self._trade.monitorQuery(fundid)