# -*- coding: utf-8 -*-
__author__ = 'xujh'

from eventengine import *
from ma import *
from datetime import datetime
from sendmail import *
from data_type import *
import time
import json
from winautotrade import *
logger = logging.getLogger("run")

class BaseEngine(object):
    def __init__(self, cf):
        self._eventEngine = EventEngine(cf.getint("main", "timer"))
        self._mail = SendMail(cf, self._eventEngine)
        self._eventEngine.register(EVENT_TIMER, self.onTimer)

    def start(self):
        self._eventEngine.start()

    def stop(self):
        self._eventEngine.stop()

    def onTimer(self, event):
        pass


class Monitor(BaseEngine):
    def __init__(self, cf):
        try:
            super(Monitor, self).__init__(cf)
            self._trade = Ma(cf, self._eventEngine)

            self._eventEngine.register(EVENT_FIRST_TABLE_ERROR, self.onFirstTableError)
            self._ip = cf.get("ma", "ip")
            self._port = cf.get("ma", "port")

            #记录上一个账号状态
            self._lastAccState = None
            self._haveSendMail = False
            self._to_addr_list = cf.get("monitor", "reveiver").strip().split(",")
            self.processRequireInput(cf)
            self.processReplyFixCol(cf)
            self.parseWorkTime(cf)

            self._funidCosOnlyList = cf.get("monitor", "cos_only").strip().split(",")
            self._funidCosOrCounterList = cf.get("monitor", "cos_or_counter").strip().split(",")
        except BaseException,e:
            logger.exception(e)
            raise e

    def start(self):
        try:
            super(Monitor, self).start()
            self._trade.logonEa()
            #需要等处理登录应答后才处理定时消息
            time.sleep(5)

        except BaseException,e:
            logger.exception(e)
            raise e

    def stop(self):
        try:
            super(Monitor, self).stop()
        except BaseException,e:
            logger.exception(e)
            raise e

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

        logger.info("replyFixCol:%s", self._replyFixCol)

    def parseWorkTime(self,cf):
        worktime = cf.get("monitor", "workingtime").split(',')
        self._worktimerange = []
        for i in range(len(worktime)):
            self._worktimerange.append(worktime[i].split('~'))
        logger.info("worktimerange:%s", self._worktimerange)

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

    def sendMail(self, state):
        event = Event(type_=EVENT_SENDMAIL)
        event.dict_['remarks'] = 'Monitor'
        content = ""
        if state == 0:
            content = u"交易网关连接断开！可能原因：1.交易网关没有正常运行;2.到交易网关的网络不稳定或者不连通"
        elif state == 1:
            content = u"交易网关连接正常"

        event.dict_['content'] = u'%s 网关参数:[ip:%s, port:%s]' % (content, self._ip, self._port)
        event.dict_['to_addr'] = self._to_addr_list
        self._eventEngine.put(event)

    def checkAccStata(self):
        curAccState = self._trade.getAccState()
        if curAccState == 0 and not self._haveSendMail:
            self.sendMail(curAccState)
            self._haveSendMail = True
            self._lastAccState = curAccState
        elif curAccState != self._lastAccState:
            self.sendMail(curAccState)
            self._lastAccState = curAccState

    def checkisworkingtime(self):
        time = datetime.now().strftime("%H:%M")
        for i in range(len(self._worktimerange)):
            if time >= self._worktimerange[i][0] and time <= self._worktimerange[i][1]:
                return True
        return False

    def onTimer(self, event):
        super(Monitor, self).onTimer()

        if not self.checkisworkingtime():
            logger.debug("now is not working time")
            return

        self.checkAccStata()

        #断线时不进行定时的业务查询
        if self._trade.getAccState() == 0:
            return
        for fundid in self._todolist:
            logger.info("onTimer fundid:%s", fundid)
            self._trade.monitorQuery(fundid)

    def onFirstTableError(self, event_):
        event = Event(type_=EVENT_SENDMAIL)
        event.dict_['remarks'] = 'Monitor'
        content = u"功能编号:%s 名称:%s,返回错误结果:[错误码:%s, 错误级别:%s, 错误信息:%s],可能原因:" % (event_.dict_['funid'],
                                                       event_.dict_['name'],
                                                       event_.dict_['msgcode'],
                                                       event_.dict_['msglevel'],
                                                       event_.dict_['msgtext'])

        if event_.dict_['funid'] in self._funidCosOnlyList:
            content += u"cos 交易服务运行异常"
        elif event_.dict_['funid'] in self._funidCosOrCounterList:
            content += u"cos 交易服务运行异常或者柜台运行异常"

        event.dict_['content'] = u'%s 网关参数:[ip:%s, port:%s]' % (content, self._ip, self._port)
        event.dict_['to_addr'] = self._to_addr_list
        self._eventEngine.put(event)

from quote import *
from strategy import *
class Business(BaseEngine):
    def __init__(self, cf):
        try:
            super(Business, self).__init__(cf)

        except BaseException,e:
            logger.exception(e)
            raise e


    def start(self):
        try:
            super(Business, self).start()

            self._stglist = []
            self._codeset = set()
            if(self._cf.getboolean("signal", "enable")):
                codelist_sig = self._cf.get("signal", "codelist").split(',')
                self._codeset = self._codeset.union(set(codelist_sig))
                for code in codelist_sig:
                    self._stglist.append(Stg_Signal(self._cf, code, self._eventEngine))

            if(self._cf.getboolean("autotrader", "enable")):
                self._traders_handle = []
                self._codeset_autotrade = set()

                if self._cf.getboolean("ma", "enable"):
                    logger.info("create trader:ma")
                    ma = Ma(self._cf, self._eventEngine)
                    ma.initAsTrader()
                    ma.logonEa()
                    self._traders_handle.append(ma)
                    codelist_ma = self._cf.get("ma", "codelist").strip().split(',')
                    for code in codelist_ma:
                        self._stglist.append(Stg_Autotrader(self._cf, code, "ma", self._eventEngine))
                    self._codeset_autotrade = self._codeset_autotrade.union(set(codelist_ma))

                if self._cf.getboolean("tdx", "enable"):
                    logger.info("create trader:tdx")
                    tdx = TdxWinTrade(self._cf, self._eventEngine)
                    tdx.initAsTrader()
                    self._traders_handle.append(tdx)
                    codelist_tdx = self._cf.get("tdx", "codelist").strip().split(',')
                    for code in codelist_tdx:
                        self._stglist.append(Stg_Autotrader(self._cf, code, "tdx", self._eventEngine))
                    self._codeset_autotrade = self._codeset_autotrade.union(set(codelist_tdx))

                self._codeset = self._codeset.union(self._codeset_autotrade)

            #一次批量获取代码的最新行情
            self._realtimequote = RealTimeQuote(self._cf, list(self._codeset), self._eventEngine)
            self._realtimequote.start()

        except BaseException,e:
            logger.exception(e)
            raise e

    def stop(self):
        try:
            super(Business, self).stop()
        except BaseException,e:
            logger.exception(e)
            raise e