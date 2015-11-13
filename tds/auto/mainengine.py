# -*- coding: utf-8 -*-
__author__ = 'xujh'

from eventengine import *
from ma import *
from datetime import datetime


class MainEngine(object):
    def __init__(self, cf):
        self._eventEngine = EventEngine(3000)
        self._trade = Ma(cf, self._eventEngine)
        self._eventEngine.register(EVENT_TIMER, self.onTimer)
        self._eventEngine.register(EVENT_AXEAGLE, self.AxeagleListen)

        self._eventEngine.start()

    def logon(self):
        self._trade.logonEa()

    def onTimer(self,event):
        print u'MainEngine 处理每秒触发的计时器事件：%s' % str(datetime.now())

    def AxeagleListen(self,event):
        print "AxeagleListen"
        print event.dict_["pMsg"].decode("gbk")
        print event.dict_["iLen"]
        print event.dict_["pAccount"]






