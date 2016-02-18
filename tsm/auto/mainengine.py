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

class MainEngine(object):
    def __init__(self, cf):
        self._eventEngine = EventEngine(cf.getint("main", "timer"))
        self._trade = Ma(cf, self._eventEngine)
        self._mail = SendMail(cf, self._eventEngine)
        self._trade.logonEa()
        time.sleep(5)

        self._eventEngine.register(EVENT_TIMER, self.onTimer)
        self._eventEngine.start()


    def onTimer(self, event):
        pass


class Monitor(MainEngine):
    def __init__(self, cf):
        try:
            super(Monitor, self).__init__(cf)
            self._eventEngine.register(EVENT_FIRST_TABLE_ERROR, self.onFirstTableError)
            self._name = cf.get("ma", "name")
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
        event.dict_['remarks'] = 'Monitor ' + self._name
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
        if not self.checkisworkingtime():
            logger.debug("now is not working time")
            return

        self.checkAccStata()

        #断线时不进行定时的业务查询
        if self._trade.getAccState() == 0:
            return
        for fundid in self._todolist:
            logger.debug("onTimer fundid:%s", fundid)
            self._trade.monitorQuery(fundid)

        # #for test
        # event = Event(type_=EVENT_FIRST_TABLE_ERROR)
        # event.dict_['funid'] = '10303001'
        # event.dict_['name'] = funNameDict['10388301']
        # event.dict_['msgcode'] = '123'
        # event.dict_['msglevel'] = '3'
        # event.dict_['msgtext'] = u"查询股份异常"
        # self._eventEngine.put(event)

    def onFirstTableError(self, event_):
        event = Event(type_=EVENT_SENDMAIL)
        event.dict_['remarks'] = 'Monitor ' + self._name
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


class BatchOrder(MainEngine):
    def __init__(self, cf):
        try:
            super(BatchOrder, self).__init__(cf)
            time.sleep(10)
            #self.orderByPricePerent(cf)
            #self.test()
            #self.orderByTime(cf)
            self.orderByPriceGrad(cf)

        except BaseException,e:
            logger.exception(e)
            raise e

    def test1(self):
        event = Event(type_= EVENT_TRADE)
        event.dict_['direction'] = 'buy'
        event.dict_['code'] = '000001'
        event.dict_['number'] = '100'
        self._eventEngine.put(event)


#000007060457 MAP01BR0 201601221547140005dcf4d304c0e4b2baef5848e46da4c6e00000000000000000000000000000000103881010000000000001000100000541AQAAAAAAAAAAAAAA0005T    3706{"207":"0","38":"500","40":"121","44":"0.00000000","448":"0000035079","48":"000001","625":"00","66":"61","8810":"110000035079","8811":"1","8812":"0005056c00001","8813":"F","8814":"1391000000009c8355071601221601222359590000000001TbCo1359MbQ=BBsXK/b7JY2+U2TQ1BOdZyBMmb9NMba7Xi4opzbI3oQ=","8815":"10388101","8816":"20160122154714000","8821":"1100","8834":"20160122","8842":"100","8902":"110000035079","8920":"110000035079","8970":"0","8975":"0.00000000","9080":"1","9100":"TIM=07:58:07;","9101":"1010","9102":"Oxujhaoxx5914a109","916":"155807"}
    #时间触发
    def test2(self):
        event = Event(type_= EVENT_CON_TRADE)
        event.dict_['code'] = '000001'
        event.dict_['number'] = 100
        event.dict_['ATTR_CODE'] = 1010
        event.dict_['STK_BIZ'] = 100
        event.dict_['BGN_EXE_TIME'] = 93500
        event.dict_['STOP_PRICE'] = 0.0
        self._eventEngine.put(event)

    def test(self):
        #市价止损买入
        event = Event(type_=EVENT_CON_TRADE)
        event.dict_['code'] = '000001'
        event.dict_['number'] = 100
        #市价止盈止损
        event.dict_['ATTR_CODE'] = 1112
        #100为买入 101为卖出
        event.dict_['STK_BIZ'] = 100
        event.dict_['STOP_PRICE'] = 9.91
        self._eventEngine.put(event)

        event = Event(type_=EVENT_CON_TRADE)
        event.dict_['code'] = '000001'
        event.dict_['number'] = 100
        #市价止盈止损
        event.dict_['ATTR_CODE'] = 1112
        #100为买入 101为卖出
        event.dict_['STK_BIZ'] = 101
        event.dict_['STOP_PRICE'] = 9.89
        self._eventEngine.put(event)


    def test3(self):
        #市价止损买入
        event = Event(type_=EVENT_CON_TRADE)
        event.dict_['code'] = '603999'
        event.dict_['number'] = 100
        #市价止盈止损
        event.dict_['ATTR_CODE'] = 1112
        #100为买入 101为卖出
        event.dict_['STK_BIZ'] = 100
        event.dict_['STOP_PRICE'] = 41.45
        self._eventEngine.put(event)

        event = Event(type_=EVENT_CON_TRADE)
        event.dict_['code'] = '000001'
        event.dict_['number'] = 100
        #市价止盈止损
        event.dict_['ATTR_CODE'] = 1112
        #100为买入 101为卖出
        event.dict_['STK_BIZ'] = 101
        event.dict_['STOP_PRICE'] = 41.39
        self._eventEngine.put(event)

    #基于时间触发的批量委托
    def orderByTime(self,cf):
        for i in range(cf.getint("timebase", "count")):
            code = cf.get("timebase", "code")
            time = cf.getint("timebase", "time")
            number = cf.getint("timebase", "number")

            event = Event(type_= EVENT_CON_TRADE)
            event.dict_['code'] = code
            event.dict_['number'] = number
            event.dict_['ATTR_CODE'] = 1010
            event.dict_['STK_BIZ'] = 100
            event.dict_['BGN_EXE_TIME'] = time
            event.dict_['STOP_PRICE'] = 0.0
            self._eventEngine.put(event)



    def orderByPricePerent(self, cf):
        fmkt = open(cf.get("batchorder", "hqdatapath").decode('utf8'))
        pricecount = cf.getint("batchorder", "pricecount")
        pricegrad = cf.getfloat("batchorder", "pricegrad")
        for line in fmkt:
            content = line.strip().split('\t')
            if content[0].isdigit() and float(content[3]) > 0.01:
                for i in range(1, pricecount+1):
                    #市价止损买入
                    event = Event(type_=EVENT_CON_TRADE)
                    event.dict_['code'] = content[0]
                    event.dict_['number'] = 100
                    #市价止盈止损
                    event.dict_['ATTR_CODE'] = 1112
                    #100为买入 101为卖出
                    event.dict_['STK_BIZ'] = 100
                    event.dict_['STOP_PRICE'] = round(float(content[3]) * (1 + pricegrad * i),2)
                    self._eventEngine.put(event)

                    #市价止损买入
                    event = Event(type_=EVENT_CON_TRADE)
                    event.dict_['code'] = content[0]
                    event.dict_['number'] = 100
                    #市价止盈止损
                    event.dict_['ATTR_CODE'] = 1112
                    #100为买入 101为卖出
                    event.dict_['STK_BIZ'] = 101
                    event.dict_['STOP_PRICE'] = round(float(content[3]) * (1 - pricegrad * i),2)
                    self._eventEngine.put(event)
                    time.sleep(0.01)


    def orderByPriceGrad(self, cf):
        fmkt = open(cf.get("batchorder", "hqdatapath").decode('utf8'))
        pricecount = cf.getint("batchorder", "pricecount")
        pricegrad = cf.getfloat("batchorder", "pricegrad")
        for line in fmkt:
            content = line.strip().split('\t')
            if content[0].isdigit() and float(content[3]) > 0.01:
                for i in range(1, pricecount+1):
                    #市价止损买入
                    event = Event(type_=EVENT_CON_TRADE)
                    event.dict_['code'] = content[0]
                    event.dict_['number'] = 100
                    #市价止盈止损
                    event.dict_['ATTR_CODE'] = 1112
                    #100为买入 101为卖出
                    event.dict_['STK_BIZ'] = 100
                    event.dict_['STOP_PRICE'] = round(float(content[3]) + pricegrad * i, 2)
                    self._eventEngine.put(event)

                    #市价止损买入
                    event = Event(type_=EVENT_CON_TRADE)
                    event.dict_['code'] = content[0]
                    event.dict_['number'] = 100
                    #市价止盈止损
                    event.dict_['ATTR_CODE'] = 1112
                    #100为买入 101为卖出
                    event.dict_['STK_BIZ'] = 101
                    event.dict_['STOP_PRICE'] = round(float(content[3]) - pricegrad * i, 2)
                    self._eventEngine.put(event)









