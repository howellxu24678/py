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
        self._eventEngine = EventEngine(cf.getint("main", "timer"))
        self._trade = Ma(cf, self._eventEngine)
        self._mail = SendMail(cf, self._eventEngine)
        self._trade.logonEa()
        time.sleep(5)
        self.monitor(cf)
        self._eventEngine.register(EVENT_TIMER, self.onTimer)
        self._eventEngine.start()



    def processRequireInput(self,cf):
        self._requireconfig = {}
        for i in cf.items('requireinput'):
            self._requireconfig[i[0].upper()] = i[1]
        self._requireconfig['CUACCT_CODE'] = cf.get("ma", "account")

        self._todolist = cf.get("ma", "todolist").strip().split(',')
        for todofunid in self._todolist:
            self._eventEngine.register(EVENT_QUERY_RET + todofunid, self.onQueryRet)

            if todofunid in requireFixColDict:
                for k in requireFixColDict[todofunid].iterkeys():
                    if not k in self._requireconfig:
                        raise RuntimeError, "cant find the %s in %s" % (k, self._requireconfig)
                    else:
                        requireFixColDict[todofunid][k] = self._requireconfig[k]

    def processReplyFixCol(self,cf):
        self._replyFixCol = {}
        for i in cf.items('replyfixcol'):
            self._replyFixCol[i[0]] = i[1]

        print "_replyFixCol is ", self._replyFixCol

    def monitor(self,cf):
        self.processRequireInput(cf)
        self.processReplyFixCol(cf)

    def onQueryRet(self, event_):
        funid = event_.type_.split('.')[1]
        if not funid in self._replyFixCol:
            return

        ret = event_.dict_['ret']
        tinyret = []
        for r in ret:
            tinyretdict = {}
            for k,v in r.items():
                if k in self._replyFixCol[funid] or self._replyFixCol[funid].strip() == '':
                    tinyretdict[k] = v
            tinyret.append(tinyretdict)
        logger.info('funid:%s, funname:%s, ret:%s', funid, funNameDict[funid], tinyret)

    def logon(self):
        self._trade.logonEa()

    def onTimer(self, event):
        for fundid in self._todolist:
            logger.info("onTimer fundid:%s", fundid)
            self._trade.monitorQuery(fundid)