# -*- coding: utf-8 -*-
__author__ = 'xujh'

from eventengine import *
from ma import *
#from datetime import datetime
from sendmail import *
from data_type import *
from util import *
#import time
import json
logger = logging.getLogger()

class MainEngine(object):
    def __init__(self, cf):
        try:
            self._cf = cf
            self._eventEngine = EventEngine(cf.getint("main", "timer"))
            self._trade = Ma(cf, self._eventEngine)
            self._mail = SendMail(cf, self._eventEngine)

            self._logonBackendState = None

            self._eventEngine.start()
        except BaseException, e:
            logger.exception(e)


    #此函数会被Monito派生类重载，因为Monitor派生类需要根据状态变化发送提醒邮件
    def onLogonBackendRet(self, event_):
        logger.debug('onLogonBackendRet event type:%s', event_.type_)

        #EVENT_EA_ERROR
        if event_.type_ == EVENT_EA_ERROR:
            self._logonBackendState = False
        #EVENT_QUERY_RET EVENT_FIRST_TABLE_ERROR
        else:
            funid = event_.dict_['funid']
            if funid != '10301105':
                return

            if event_.type_ == EVENT_QUERY_RET + '10301105':
                self._logonBackendState = True
            elif event_.type_ == EVENT_FIRST_TABLE_ERROR:
                self._logonBackendState = False

    def onTimer(self, event):
        logger.debug("onTimer")

    def re_init(self):
        #后台登录状态，只有在后台登录状态为成功时，才可以其他业务操作（比如定时轮询业务功能或者批量下单）
        self._logonBackendState = None

    def start(self):
        self.re_init()

        self._eventEngine.register(EVENT_QUERY_RET + '10301105', self.onLogonBackendRet)
        self._eventEngine.register(EVENT_EA_ERROR, self.onLogonBackendRet)
        self._eventEngine.register(EVENT_FIRST_TABLE_ERROR, self.onLogonBackendRet)
        self._eventEngine.register(EVENT_TIMER, self.onTimer)

        #调用trade登录Ea接口，接口返回后会自动进行登录后台动作
        self._trade.logonEa()


    def stop(self):
        self._eventEngine.unregister(EVENT_QUERY_RET + '10301105', self.onLogonBackendRet)
        self._eventEngine.unregister(EVENT_EA_ERROR, self.onLogonBackendRet)
        self._eventEngine.unregister(EVENT_FIRST_TABLE_ERROR, self.onLogonBackendRet)
        self._eventEngine.unregister(EVENT_TIMER, self.onTimer)
        # self._eventEngine.stop()

        self._trade.closeEa()

'''
异常情况1：登录交易网关失败，会自动尝试登录，OnTime检测到当前网关连接状态为异常会发送邮件
异常情况2：登录交易网关成功，登录后台失败，需要定时尝试登录后台直到成功为止
            2.1 交易网关没有连上cos的GTU网关，会报“连接交易后台失败”，“交易服务发送指令失败”
            2.2 交易网关连上了cos的GTU网关，但是cos BPU或者柜台没有正常运行
            2.3 当mid正常运行时，getAccState获得的状态是正常状态，不管此时mid是否有成功连上后面的GTU网关
            会报“不存在路由信息”，“811处于非交易状态”
异常情况3：定时执行业务功能查询，出现状态变动时发送邮件提醒

需要处理的状态有：
1. 登录交易网关成功与否状态。如果状态为失败，不进行
2. 登录后台成功与否状态。如果状态为失败，不进行后续业务功能查询
'''


class Monitor(MainEngine):
    def __init__(self, cf):
        try:
            super(Monitor, self).__init__(cf)

            #保存每个查询funid的最新查询状态，True为成功，False为失败，None为未初始化
            self._funQueryState = {}

            self._name = cf.get("ma", "name")
            self._ip = cf.get("ma", "ip")
            self._port = cf.get("ma", "port")

            self._account = cf.get("ma", "account")
            self._node = cf.get("ma", "node")

            self._worktimerange = parse_work_time(cf.get("monitor", "workingtime"))
            self._to_addr_list = cf.get("monitor", "reveiver").strip().split(",")
            self.processRequireInput(cf)
            self.processReplyFixCol(cf)

            self._funidCosOnlyList = cf.get("monitor", "cos_only").strip().split(",")
            self._funidCosOrCounterList = cf.get("monitor", "cos_or_counter").strip().split(",")

            self._todolistalltrue = [True for x in range(len(self._todolist))]
            #发送邮件附带的系统参数
            self._sys_content = u'\n资金账号:[%s],网关参数:[ip:%s, port:%s]' % \
                                (self._account, self._ip, self._port)

            #检车网络连通性
            self._connect_addr_list = \
                [x.strip().split(':') for x in cf.get("monitor", "check_connect_addr").strip().split(",")]

            #容许连续发现连接断开的次数
            self._max_broken_times = cf.getint("monitor", "brokentimes")
            self._broken_count = 0

        except BaseException,e:
            logger.exception(e)
            raise e

    def re_init(self):
        super(Monitor, self).re_init()
        # 记录当前的外网ip
        #logger.info('the outer ip:%s', get_outer_ip())
        # 记录上一个账户状态（也即为登录交易网关Ea成功与否的状态）
        self._lastAccState = None
        # 是否已经发送登录交易网关Ea是否成功的邮件
        self._haveSendLogonEaMail = False
        # 是否已经发送登录后台是否成功的邮件
        self._haveSendLogonBackendMail = False
        # 是否已经发送登录后台成功后所有定时业务执行成功的邮件
        self._haveSendAllBisOKMail = False

        for todofunid in self._funQueryState:
            self._funQueryState[todofunid] = None

    def start(self):
        #如果发现当天并不是交易日的话，不启动监控
        if not is_trade_day(self._cf):
            logger.info('today is not a trade day, so the monitor will not be started')
            return
        super(Monitor, self).start()
        self._eventEngine.register(EVENT_FIRST_TABLE_ERROR, self.onFirstTableError)

    def stop(self):
        self._eventEngine.unregister(EVENT_FIRST_TABLE_ERROR, self.onFirstTableError)
        super(Monitor, self).stop()

    def processRequireInput(self,cf):
        self._requireconfig = {}
        for i in cf.items('requireinput'):
            self._requireconfig[i[0].upper()] = i[1]
        self._requireconfig['CUACCT_CODE'] = cf.get("ma", "account")

        self._todolist = cf.get("monitor", "todolist").strip().split(',')

        for todofunid in self._todolist:
            #记录每一个查询funid的状态
            self._funQueryState[todofunid] = None

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


    def updateFunQueryState(self, curQueryState, event_):
        funid = event_.dict_['funid']
        #首次查询时，一开始 self._funQueryState 中所有的状态都为None,此时要等到所有的查询结果都过来
        # 非初始赋值，并且状态发生更改时则发送邮件
        if funid in self._funQueryState:
            if self._funQueryState[funid] != curQueryState and \
                    (not curQueryState or not self._funQueryState[funid] is None):
                self.sendMailQueryState(curQueryState, event_)
            self._funQueryState[funid] = curQueryState

            if not self._haveSendAllBisOKMail and self._funQueryState.values() == self._todolistalltrue:
                self.sendMailAllOk()
                self._haveSendAllBisOKMail = True

    def onQueryRet(self, event_):
        self.updateFunQueryState(True, event_)

        funid = event_.dict_['funid']
        if not funid in self._replyFixCol:
            return

        ret = event_.dict_['ret']
        if ret is None:
            return

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

    #重载自基类，需要处理状态变化发送提醒邮件
    def onLogonBackendRet(self, event_):
        logger.debug('onLogonBackendRet event type:%s', event_.type_)
        err_msg = None

        #EVENT_EA_ERROR
        if event_.type_ == EVENT_EA_ERROR:
            curBackendState = False
            err_msg = event_.dict_['msgtext']
        #EVENT_QUERY_RET EVENT_FIRST_TABLE_ERROR
        else:
            funid = event_.dict_['funid']
            if funid != '10301105':
                return

            if event_.type_ == EVENT_QUERY_RET + '10301105':
                curBackendState = True
            elif event_.type_ == EVENT_FIRST_TABLE_ERROR:
                curBackendState = False
                err_msg = event_.dict_['msgtext']


        if not curBackendState and not self._haveSendLogonBackendMail:
            self.sendLogonBackendState(curBackendState, err_msg)
            self._haveSendLogonBackendMail = True
        elif curBackendState != self._logonBackendState and self._logonBackendState is not None:
            self.sendLogonBackendState(curBackendState, err_msg)
        self._logonBackendState = curBackendState

    def sendMailEvent(self, state, content):
        event = Event(type_=EVENT_SENDMAIL)
        event.dict_['remarks'] = u'%s,节点:%s,%s状态告知消息' % (self._name, self._node, u'正常' if state else u'异常')
        event.dict_['content'] = u'%s%s' % (content, self._sys_content)
        event.dict_['to_addr'] = self._to_addr_list
        self._eventEngine.put(event)

        logger.info("send mail %s to %s", event.dict_['content'], event.dict_['to_addr'])

    def sendMailAccState(self, acc_state):
        if acc_state == 0:
            self.sendMailEvent(False, u"交易网关连接断开！可能原因：1.交易网关没有正常运行;2.到交易网关的网络不稳定或者不连通")
        elif acc_state == 1:
            self.sendMailEvent(True, u"交易网关连接正常")

    def sendLogonBackendState(self, backend_state, err_msg):
        if not backend_state:
            self.sendMailEvent(False, u"登录后台失败！%s" % err_msg if err_msg is not None else '')
        else:
            self.sendMailEvent(True, u"登录后台成功")

    def sendMailQueryState(self, cur_query_state, event_):
        if cur_query_state:
            state = True
            content = u"功能编号:%s,名称:%s,执行成功" % (event_.dict_['funid'],event_.dict_['name'])
        else:
            state = False
            content = u"功能编号:%s,名称:%s,返回错误结果:[错误码:%s, 错误级别:%s, 错误信息:%s],可能原因:" % (event_.dict_['funid'],
                                                                                  event_.dict_['name'],
                                                                                  event_.dict_['msgcode'],
                                                                                  event_.dict_['msglevel'],
                                                                                  event_.dict_['msgtext'])
            if event_.dict_['funid'] in self._funidCosOnlyList:
                content += u"cos 交易服务运行异常"
            elif event_.dict_['funid'] in self._funidCosOrCounterList:
                content += u"cos 交易服务运行异常或者柜台运行异常"

        self.sendMailEvent(state, content)


    def sendMailAllOk(self):
        self.sendMailEvent(True, u'功能编号:[%s]执行成功' % ','.join(self._todolist))


    def checkAccStata(self):
        curAccState = self._trade.getAccState()

        #以下逻辑用于判断是否出现连续监测到与交易网关断开的情况
        if curAccState == 0:
            self._broken_count += 1
            if self._broken_count < self._max_broken_times:
                logger.info("Axeagle gateway is not connected, but count:%s is less than max_times:%s",
                            self._broken_count, self._max_broken_times)
                return
        self._broken_count = 0

        #1.初始时登录状态为异常（0）并且还没有发送邮件，则发送邮件并将发送状态置为已发送
        #2.其中状态发生改变时，发送邮件
        if curAccState == 0 and not self._haveSendLogonEaMail:
            self.sendMailAccState(curAccState)
            self._haveSendLogonEaMail = True
        elif curAccState != self._lastAccState and self._lastAccState is not None:
            self.sendMailAccState(curAccState)

        self._lastAccState = curAccState

    #连通性测试
    def check_connect(self):
        for x in self._connect_addr_list:
            logger.info("connect to %s:%s %s", x[0], x[1], 'success' if is_connectable(x[0], int(x[1])) else 'failed')

    def onTimer(self, event):
        super(Monitor, self).onTimer(event)

        if not is_working_time(self._worktimerange):
            logger.debug("now is not working time")
            return

        self.checkAccStata()

        #断线时不进行定时的业务查询
        if self._trade.getAccState() == 0:
            # 记录当前的外网ip
            #logger.info('the outer ip:%s', get_outer_ip())

            self.check_connect()
            return

        #没有成功登录后台，不会自动重新登录，需要在这里定时尝试登录
        if not self._logonBackendState:
            self._trade.logonBackend()
            return

        for fundid in self._todolist:
            logger.debug("onTimer fundid:%s", fundid)
            self._trade.monitorQuery(fundid)

    def onFirstTableError(self, event_):
        self.updateFunQueryState(False, event_)


class BatchOrder(MainEngine):
    def __init__(self, cf):
        try:
            super(BatchOrder, self).__init__(cf)
            super(BatchOrder, self).start()
            time.sleep(5)
            #self.orderByPricePerent(cf)
            #self.test()
            #self.orderByTime(cf)
            #self.orderByPriceGrad(cf)

            self.test1()

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









