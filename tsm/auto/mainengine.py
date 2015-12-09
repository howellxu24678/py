# -*- coding: utf-8 -*-
__author__ = 'xujh'

from eventengine import *
from ma import *
from datetime import datetime
from sendmail import *
from data_type import *
import time
import json
logger = logging.getLogger("run")


class Monitor(object):
    def __init__(self, cf, ee):
        self._eventEngine = ee

    def processRequireInput(self,cf):
        self._requireconfig = {}
        for i in cf.items('requireinput'):
            self._requireconfig[i[0].upper()] = i[1]
        self._requireconfig['CUACCT_CODE'] = cf.get("ma", "account")

        self._todolist = cf.get("monitor", "todolist").strip().split(',')
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

    def parseWorkTime(self,cf):
        worktime = cf.get("monitor", "workingtime").split(',')
        self._worktimerange = []
        for i in range(len(worktime)):
            self._worktimerange.append(worktime[i].split('~'))
        logger.info("worktimerange:%s", self._worktimerange)

    def monitor(self,cf):
        self._offlinetime = cf.getint("monitor", "offlinetime")
        self.processRequireInput(cf)
        self.processReplyFixCol(cf)
        self.parseWorkTime(cf)

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
        logger.info('funid:%s, funname:%s, ret:%s',
                    funid,
                    funNameDict[funid],
                    json.dumps(tinyret,ensure_ascii=False, indent=2))


    def checkAccStata(self):
        if self._trade.getAccState() == 1:
            self._accState = 1
            return

        #如果状态从正常状态到异常，表示有异常，需要按照特定规则 发送邮件
        if self._accState == 1:
            self._checkofflinetime = datetime.now()
            self._accState = 0

        elif self._accState == 0:
            timedelta_ms = (datetime.now() - self._checkofflinetime).total_seconds() * 1000
            if timedelta_ms > self._offlinetime:
                pass

                #sendmail


    def checkisworkingtime(self):
        time = datetime.now().strftime("%H:%M")
        for i in range(len(self._worktimerange)):
            if time >= self._worktimerange[i][0] and time <= self._worktimerange[i][1]:
                return True
        return False


class MainEngine(object):
    def __init__(self, cf):
        self._eventEngine = EventEngine(cf.getint("main", "timer"))
        self._trade = Ma(cf, self._eventEngine)
        self._mail = SendMail(cf, self._eventEngine)
        self._trade.logonEa()
        time.sleep(5)
        self.monitor(cf)
        self._accState = None
        self._eventEngine.register(EVENT_TIMER, self.onTimer)
        self._eventEngine.start()


    def onTimer(self, event):
        if not self.checkisworkingtime():
            logger.info("now is not working time")
            return

        self.checkAccStata()
        for fundid in self._todolist:
            logger.info("onTimer fundid:%s", fundid)
            self._trade.monitorQuery(fundid)