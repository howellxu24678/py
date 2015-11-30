# -*- coding: utf-8 -*-
__author__ = 'xujh'

from data_type import *
from eventengine import *

import datetime
import logging
import base64
import socket
logger = logging.getLogger("run")

defineDict = {}
defineDict['MACLI_HEAD_FID_PKT_LEN'] = c_int(0)
defineDict['MACLI_HEAD_FID_PKT_CRC'] = c_int(1)
defineDict['MACLI_HEAD_FID_PKT_ID'] = c_int(2)
defineDict['MACLI_HEAD_FID_PKT_VER'] = c_int(3)
defineDict['MACLI_HEAD_FID_PKT_TYPE'] = c_int(4)
defineDict['MACLI_HEAD_FID_MSG_TYPE'] = c_int(5)
defineDict['MACLI_HEAD_FID_RESEND_FLAG'] = c_int(6)
defineDict['MACLI_HEAD_FID_TIMESTAMP'] = c_int(7)
defineDict['MACLI_HEAD_FID_MSG_ID'] = c_int(8)
defineDict['MACLI_HEAD_FID_CORR_ID'] = c_int(9)
defineDict['MACLI_HEAD_FID_FUNC_ID'] = c_int(11)
defineDict['MACLI_HEAD_FID_SRC_NODE'] = c_int(12)
defineDict['MACLI_HEAD_FID_DEST_NODE'] = c_int(13)
defineDict['MACLI_HEAD_FID_PAGE_FLAG'] = c_int(14)
defineDict['MACLI_HEAD_FID_PAGE_NO'] = c_int(15)
defineDict['MACLI_HEAD_FID_PAGE_CNT'] = c_int(16)
defineDict['MACLI_HEAD_FID_BODY_LEN'] = c_int(21)
defineDict['MACLI_HEAD_FID_PKT_HEAD_END'] = c_int(25)
defineDict['MACLI_HEAD_FID_PKT_HEAD_LEN'] = c_int(35)
defineDict['MACLI_HEAD_FID_PKT_HEAD_MSG'] = c_int(41)
defineDict['MACLI_HEAD_FID_PKT_BODY_MSG'] = c_int(42)
defineDict['MACLI_HEAD_FID_PKT_MSG'] = c_int(43)
defineDict['MACLI_HEAD_FID_FUNC_TYPE'] = c_int(1052672)
defineDict['MACLI_HEAD_FID_BIZ_CHANNEL'] = c_int(1052674)
defineDict['MACLI_HEAD_FID_TOKEN_FLAG'] = c_int(1069056)
defineDict['MACLI_HEAD_FID_PUB_TOPIC'] = c_int(1073152)
defineDict['MACLI_HEAD_FID_USER_SESSION'] = c_int(1871872)

class STU(Structure):
    def __str__(self):
        ss = ""
        for filed_name,field_type in self._fields_:
            ss += "%s:%s|" % (filed_name, getattr(self, filed_name))
        return ss

class Server(STU):
    _fields_ = [("szIp", c_char * 50),
                ("nPort", c_int)]



class NewLoginInfo(STU):
    _fields_ = [("account", c_char * 50),
                ("accountName", c_char * 50),
                ("password", c_char * 50),
                ("accountType", c_int),
                ("autoReconnect", c_int),
                ("serverCount", c_int),
                ("servers", Server * 10)]


def onMsg(pMsg, iLen, pAccount, pParam):
    logger.debug("onAxEagle callback msgLen:%s", iLen)
    event = Event(type_=EVENT_AXEAGLE)
    event.dict_['pMsg'] = pMsg
    event.dict_['iLen'] = iLen
    event.dict_['pAccount'] = pAccount
    pParam.put(event)


onMsgFv = CFUNCTYPE (None, c_char_p, c_int, c_char_p, py_object)
onMsgHandle = onMsgFv(onMsg)


class Ma(object):
    def __init__(self, cf, eventEngine_):
        try:
            self._ma = WinDLL("maCliApi.dll")
            self._ea = WinDLL("GxTS.dll")
            self._eventEngine = eventEngine_
            self._eventEngine.register(EVENT_AXEAGLE, self.onRecvMsg)
            self._eventEngine.register(EVENT_TRADE, self.onQuantOrder)

            self._ip = cf.get("ma", "ip")
            self._port = cf.getint("ma","port")
            self._acc = c_char_p(cf.get("ma", "account"))
            self._pwd = c_char_p(cf.get("ma", "password"))
            logger.info("ip:%s, port:%s, account:%s, password:%s",
                        self._ip,
                        self._port,
                        self._acc,
                        self._pwd)
            self._session = None
            self._int_org = None
            self._bd2tradacc_dict = {}

            self._dealReplyDict = {}
            self._dealReplyDict['10301105'] = self.dealLogonBackendReply
            self._dealReplyDict['10303001'] = self.dealQueryMoneyReply
            self._dealReplyDict['10303002'] = self.dealQueryPositionReply
            self._dealReplyDict['10303003'] = self.dealQueryOrderTodayReply
            self._dealReplyDict['10303004'] = self.dealQueryMatchTodayReply
            self._dealReplyDict['10388101'] = self.dealQuantOrderReply

            self._localIp = c_char_p("1:" + socket.gethostbyname(socket.gethostname()))
            self._ea.AxE_Init(None, None, onMsgHandle, py_object(self._eventEngine))

        except BaseException,e:
            logger.exception(e)
            raise e

    def setPkgHead(self, hHandle_, pkgtype_, msgtype_, funtype_, funid_, msgid_):
        try:
            self._ma.maCli_SetHdrValueC(hHandle_, c_char(pkgtype_), defineDict['MACLI_HEAD_FID_PKT_TYPE'])
            self._ma.maCli_SetHdrValueC(hHandle_, c_char(msgtype_), defineDict['MACLI_HEAD_FID_MSG_TYPE'])
            self._ma.maCli_SetHdrValueS(hHandle_, c_char_p('01'), defineDict['MACLI_HEAD_FID_PKT_VER'])
            self._ma.maCli_SetHdrValueC(hHandle_, c_char(funtype_), defineDict['MACLI_HEAD_FID_FUNC_TYPE'])
            self._ma.maCli_SetHdrValueS(hHandle_, c_char_p(funid_), defineDict['MACLI_HEAD_FID_FUNC_ID'])
            self._ma.maCli_SetHdrValueS(hHandle_, msgid_, defineDict['MACLI_HEAD_FID_MSG_ID'])
        except BaseException,e:
            logger.exception(e)

    def setRegular(self, hHandle_):
        try:
            self._ma.maCli_SetValueS(hHandle_, self._acc, fixDict['F_OP_USER'])
            self._ma.maCli_SetValueC(hHandle_, c_char('1'), fixDict['F_OP_ROLE'])
            self._ma.maCli_SetValueS(hHandle_, self._localIp, fixDict['F_OP_SITE'])
            self._ma.maCli_SetValueC(hHandle_, c_char('0'), fixDict['F_CHANNEL'])
            self._ma.maCli_SetValueS(hHandle_, c_char_p("10301105"), fixDict['F_FUNCTION'])
            if self._session is None:
                szVersion = create_string_buffer(32+1)
                self._ma.maCli_GetVersion(hHandle_, szVersion, len(szVersion))
                self._session = szVersion
            self._ma.maCli_SetValueS(hHandle_, self._session, fixDict['F_SESSION'])
            self._ma.maCli_SetValueS(hHandle_,
                                     c_char_p(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                                     fixDict['F_RUNTIME'])
            if self._int_org is None:
                self._int_org = c_int(0)
            self._ma.maCli_SetValueN(hHandle_, self._int_org, fixDict['F_OP_ORG'])
        except BaseException,e:
            logger.exception(e)

    def genReqId(self):
        return int(datetime.datetime.now().strftime("%H%M%S%f")[0:-3])

    def sendReqMsg(self, b64bizdata_, reqid_, funid_, msgid_, cmdid_ = 40002):
        msg = "%d\1%d\1%s\1%s\1%s\1%s"%(cmdid_,
                                        reqid_,
                                        self._acc.value,
                                        funid_,
                                        msgid_.value,
                                        b64bizdata_)
        logger.debug("AxE_SendMsg:%s", msg)
        self._ea.AxE_SendMsg(self._acc, msg, len(msg))

    def logonEa(self):
        loginfo = NewLoginInfo()
        loginfo.account = self._acc.value
        loginfo.password = self._acc.value + "@GXTS"
        loginfo.accountType = c_int(6)
        loginfo.autoReconnect = c_int(1)
        loginfo.serverCount = c_int(1)
        loginfo.servers[0].szIp = self._ip
        loginfo.servers[0].nPort = c_int(self._port)
        self._ea.AxE_NewMultiLogin(byref(loginfo))

    def logonBackend(self):
        try:
            hHandle = c_void_p(0)
            self._ma.maCli_Init(byref(hHandle))
            self._ma.maCli_BeginWrite(hHandle)
            reqid = self.genReqId()
            funid = "10301105"
            msgid = create_string_buffer(32+1)
            self._ma.maCli_GetUuid(hHandle, msgid, len(msgid))

            self.setPkgHead(hHandle, "B", "R", "Q", funid, msgid)
            self.setRegular(hHandle)

            self._ma.maCli_SetValueS(hHandle, c_char_p("Z"), fixDict['ACCT_TYPE'])
            self._ma.maCli_SetValueS(hHandle, self._acc, fixDict['ACCT_ID'])
            self._ma.maCli_SetValueS(hHandle, c_char_p("0"), fixDict['USE_SCOPE'])
            self._ma.maCli_SetValueS(hHandle, self._acc, fixDict['ENCRYPT_KEY'])
            self._ma.maCli_SetValueS(hHandle, c_char_p("0"), fixDict['AUTH_TYPE'])

            szAuthData = create_string_buffer(256+1)
            self._ma.maCli_ComEncrypt(hHandle, szAuthData, len(szAuthData), self._pwd, self._acc)
            self._ma.maCli_SetValueS(hHandle, szAuthData, fixDict['AUTH_DATA'])
            self._ma.maCli_EndWrite(hHandle)

            b64bizdata = self.genBizData(hHandle)

            self.sendReqMsg(b64bizdata, reqid, funid, msgid)
        except BaseException,e:
            logger.exception(e)

    def subOrderAck(self):
        '''
        订阅委托确认
        :return:
        '''
        try:
            for trdacc in self._bd2tradacc_dict.values():
                hHandle = c_void_p(0)
                self._ma.maCli_Init(byref(hHandle))
                self._ma.maCli_BeginWrite(hHandle)
                reqid = self.genReqId()
                funid = "00102012"
                msgid = create_string_buffer(32+1)
                self._ma.maCli_GetUuid(hHandle, msgid, len(msgid))

                self.setPkgHead(hHandle, "S", "R", "Q", funid, msgid)
                self.setRegular(hHandle)
                self._ma.maCli_SetValueS(hHandle, c_char_p("TSU_ORDER"), c_char_p("TOPIC"))
                self._ma.maCli_SetValueS(hHandle, c_char_p(trdacc), c_char_p("FILTER"))
                self._ma.maCli_SetValueS(hHandle, c_char_p(trdacc), c_char_p("SUB_ID"))
                self._ma.maCli_SetValueC(hHandle, c_char('1'), c_char_p("DATA_SET"))
                self._ma.maCli_EndWrite(hHandle)

                b64bizdata = self.genBizData(hHandle)
                self.sendReqMsg(b64bizdata, reqid, funid, msgid)
                logger.info("subOrderAck %s", trdacc)
        except BaseException,e:
            logger.exception(e)

    def subMatchAck(self):
        '''
        订阅成交回报
        :return:
        '''
        try:
            for bd,trdacc in self._bd2tradacc_dict.iteritems():
                hHandle = c_void_p(0)
                self._ma.maCli_Init(byref(hHandle))
                self._ma.maCli_BeginWrite(hHandle)
                reqid = self.genReqId()
                funid = "00102012"
                msgid = create_string_buffer(32+1)
                self._ma.maCli_GetUuid(hHandle, msgid, len(msgid))

                self.setPkgHead(hHandle, "S", "R", "Q", funid, msgid)
                self.setRegular(hHandle)
                self._ma.maCli_SetValueS(hHandle, c_char_p("MATCH" + bd), c_char_p("TOPIC"))
                self._ma.maCli_SetValueS(hHandle, c_char_p(trdacc), c_char_p("FILTER"))
                self._ma.maCli_SetValueS(hHandle, c_char_p(trdacc), c_char_p("SUB_ID"))
                self._ma.maCli_SetValueC(hHandle, c_char('1'), c_char_p("DATA_SET"))
                self._ma.maCli_EndWrite(hHandle)

                b64bizdata = self.genBizData(hHandle)
                self.sendReqMsg(b64bizdata, reqid, funid, msgid)
                logger.info("subMatchAck %s,%s", bd, trdacc)
        except BaseException,e:
            logger.exception(e)

    def monitorQuery(self, funid_):
        try:
            hHandle = c_void_p(0)
            self._ma.maCli_Init(byref(hHandle))
            self._ma.maCli_BeginWrite(hHandle)
            reqid = self.genReqId()
            msgid = create_string_buffer(32+1)
            self._ma.maCli_GetUuid(hHandle, msgid, len(msgid))

            self.setPkgHead(hHandle, "B", "R", "Q", funid_, msgid)
            self.setRegular(hHandle)

            self._ma.maCli_SetValueS(hHandle, self._acc, fixDict['CUACCT_CODE'])
            self._ma.maCli_EndWrite(hHandle)

            b64bizdata = self.genBizData(hHandle)
            self.sendReqMsg(b64bizdata, reqid, funid_, msgid)

        except BaseException,e:
            logger.exception(e)

    def queryMoney(self):
        try:
            hHandle = c_void_p(0)
            self._ma.maCli_Init(byref(hHandle))
            self._ma.maCli_BeginWrite(hHandle)
            reqid = self.genReqId()
            funid = "10303001"
            msgid = create_string_buffer(32+1)
            self._ma.maCli_GetUuid(hHandle, msgid, len(msgid))

            self.setPkgHead(hHandle, "B", "R", "Q", funid, msgid)
            self.setRegular(hHandle)

            self._ma.maCli_SetValueS(hHandle, self._acc, fixDict['CUACCT_CODE'])
            self._ma.maCli_EndWrite(hHandle)

            b64bizdata = self.genBizData(hHandle)
            self.sendReqMsg(b64bizdata, reqid, funid, msgid)

        except BaseException,e:
            logger.exception(e)

    def queryPosition(self):
        try:
            hHandle = c_void_p(0)
            self._ma.maCli_Init(byref(hHandle))
            self._ma.maCli_BeginWrite(hHandle)
            reqid = self.genReqId()
            funid = "10303002"
            msgid = create_string_buffer(32+1)
            self._ma.maCli_GetUuid(hHandle, msgid, len(msgid))

            self.setPkgHead(hHandle, "B", "R", "Q", funid, msgid)
            self.setRegular(hHandle)

            self._ma.maCli_SetValueS(hHandle, self._acc, fixDict['CUACCT_CODE'])
            self._ma.maCli_EndWrite(hHandle)

            b64bizdata = self.genBizData(hHandle)
            self.sendReqMsg(b64bizdata, reqid, funid, msgid)

        except BaseException,e:
            logger.exception(e)
            raise e

    def queryOrderToday(self):
        try:
            hHandle = c_void_p(0)
            self._ma.maCli_Init(byref(hHandle))
            self._ma.maCli_BeginWrite(hHandle)
            reqid = self.genReqId()
            funid = "10303003"
            msgid = create_string_buffer(32+1)
            self._ma.maCli_GetUuid(hHandle, msgid, len(msgid))

            self.setPkgHead(hHandle, "B", "R", "Q", funid, msgid)
            self.setRegular(hHandle)

            self._ma.maCli_SetValueS(hHandle, self._acc, fixDict['CUACCT_CODE'])
            self._ma.maCli_EndWrite(hHandle)

            b64bizdata = self.genBizData(hHandle)
            self.sendReqMsg(b64bizdata, reqid, funid, msgid)

        except BaseException,e:
            logger.exception(e)

    def queryMatchToday(self):
        try:
            hHandle = c_void_p(0)
            self._ma.maCli_Init(byref(hHandle))
            self._ma.maCli_BeginWrite(hHandle)
            reqid = self.genReqId()
            funid = "10303004"
            msgid = create_string_buffer(32+1)
            self._ma.maCli_GetUuid(hHandle, msgid, len(msgid))

            self.setPkgHead(hHandle, "B", "R", "Q", funid, msgid)
            self.setRegular(hHandle)

            self._ma.maCli_SetValueS(hHandle, self._acc, fixDict['CUACCT_CODE'])
            self._ma.maCli_EndWrite(hHandle)

            b64bizdata = self.genBizData(hHandle)
            self.sendReqMsg(b64bizdata, reqid, funid, msgid)

        except BaseException,e:
            logger.exception(e)


    def getStkBdTrdAcc(self, code):
        try:
            if code[:2] == '00' or code[:2] == '300' or code[:2] == '15':
                return c_char_p('00'),self._bd2tradacc_dict['00']
            elif code[:2] == '60' or code[:2] == '15':
                return c_char_p('10'),self._bd2tradacc_dict['10']
        except BaseException,e:
            logger.exception(e)

        return 'unknow','unknow'

    def buySellOrder(self):
        try:
            hHandle = c_void_p(0)
            self._ma.maCli_Init(byref(hHandle))
            self._ma.maCli_BeginWrite(hHandle)
            reqid = self.genReqId()
            funid = "10302001"
            msgid = create_string_buffer(32+1)
            self._ma.maCli_GetUuid(hHandle, msgid, len(msgid))

            self.setPkgHead(hHandle, "B", "R", "T", funid, msgid)
            self.setRegular(hHandle)

            self._ma.maCli_SetValueS(hHandle, self._acc, fixDict['CUACCT_CODE'])
            self._ma.maCli_SetValueS(hHandle, '00', fixDict['STKBD'])
            self._ma.maCli_SetValueS(hHandle, '002227', fixDict['STK_CODE'])
            self._ma.maCli_SetValueN(hHandle, 100, fixDict['ORDER_QTY'])
            self._ma.maCli_SetValueN(hHandle, 100, fixDict['STK_BIZ'])
            self._ma.maCli_SetValueN(hHandle, 124, fixDict['STK_BIZ_ACTION'])
            self._ma.maCli_SetValueS(hHandle, self._bd2tradacc_dict['00'], fixDict['TRDACCT'])
            self._ma.maCli_EndWrite(hHandle)

            b64bizdata = self.genBizData(hHandle)
            self.sendReqMsg(b64bizdata, reqid, funid, msgid)

        except BaseException,e:
            logger.exception(e)
            raise e

    def onQuantOrder(self, event):
        code =  event.dict_['code']
        qty = int(event.dict_['number'])
        stkbiz = 0
        if event.dict_['direction'] == 'buy':
            stkbiz = 100
        elif event.dict_['direction'] == 'sell':
            stkbiz = 101

        try:
            hHandle = c_void_p(0)
            self._ma.maCli_Init(byref(hHandle))
            self._ma.maCli_BeginWrite(hHandle)
            reqid = self.genReqId()
            funid = "10388101"
            msgid = create_string_buffer(32+1)
            self._ma.maCli_GetUuid(hHandle, msgid, len(msgid))

            self.setPkgHead(hHandle, "B", "R", "T", funid, msgid)
            self.setRegular(hHandle)

            self._ma.maCli_SetValueS(hHandle, self._acc, fixDict['CUACCT_CODE'])
            stdbd, trdacct = self.getStkBdTrdAcc(code)
            self._ma.maCli_SetValueS(hHandle, stdbd, fixDict['STKBD'])
            self._ma.maCli_SetValueS(hHandle, trdacct, fixDict['TRDACCT'])
            self._ma.maCli_SetValueS(hHandle, code, fixDict['TRD_CODE'])
            self._ma.maCli_SetValueN(hHandle, qty, fixDict['ORDER_QTY'])
            self._ma.maCli_SetValueN(hHandle, stkbiz, fixDict['STK_BIZ'])
            self._ma.maCli_SetValueN(hHandle, 124, fixDict['STK_BIZ_ACTION'])
            self._ma.maCli_SetValueN(hHandle, 0, fixDict['ATTR_CODE'])
            self._ma.maCli_EndWrite(hHandle)

            b64bizdata = self.genBizData(hHandle)
            self.sendReqMsg(b64bizdata, reqid, funid, msgid)
        except BaseException,e:
            logger.exception(e)

    def genBizData(self, hHandle_):
        ilen = c_int(0)
        pBizData = c_char_p(0)
        self._ma.maCli_Make(hHandle_, byref(pBizData), byref(ilen))

        logger.debug("before b64encode:%s", pBizData.value)
        b64bizdata = base64.encodestring(pBizData.value)
        self._ma.maCli_Close(hHandle_)
        self._ma.maCli_Exit(hHandle_)
        return  b64bizdata

    def onRecvMsg(self,event):
        logger.debug("pMsg:%s", event.dict_["pMsg"])
        msgSplitList = event.dict_["pMsg"].split('\1')
        cmdId = msgSplitList[0]
        if cmdId == "40002" or cmdId == "40020":
            msgstr = base64.decodestring(msgSplitList[5])
            logger.debug("pMsg:%s, iLen:%s, pAccount:%s",
                        msgstr,
                        event.dict_["iLen"],
                        event.dict_["pAccount"])

            self.parseMsg(msgstr)

        if cmdId == "40000":
            self.logonBackend()

    def parseTsuOrderMsg(self, hHandle_):
        cuacc = c_int64(0)
        self._ma.maCli_GetValueL(hHandle_, byref(cuacc), 'CUACCT_CODE')
        orderno = c_int(0)
        self._ma.maCli_GetValueN(hHandle_, byref(orderno), 'ORDER_NO')
        stkcode = create_string_buffer(8+1)
        self._ma.maCli_GetValueS(hHandle_, byref(stkcode), len(stkcode), 'STK_CODE')
        stkbd = create_string_buffer(2+1)
        self._ma.maCli_GetValueS(hHandle_, byref(stkbd), len(stkbd), 'STKBD')
        orderqty = c_long(0)
        self._ma.maCli_GetValueL(hHandle_, byref(orderqty), 'ORDER_QTY')
        orderprice = c_double(0.0)
        self._ma.maCli_GetValueD(hHandle_, byref(orderprice), 'ORDER_PRICE')
        logger.info("CUACCT_CODE:%s,ORDER_NO:%s,STK_CODE:%s,STKBD:%s,ORDER_QTY:%s,ORDER_PRICE:%s",
                    cuacc.value,
                    orderno.value,
                    stkcode.value,
                    stkbd.value,
                    orderqty.value,
                    orderprice.value)

    def parseMatchMsg(self, hHandle_):
        pass

    def parseSubMsg(self, hHandle_):
        topic = create_string_buffer(12+1)
        self._ma.maCli_GetHdrValueS(hHandle_, topic, len(topic), defineDict['MACLI_HEAD_FID_PUB_TOPIC'])
        if topic.value == 'TSU_ORDER':
            self.parseTsuOrderMsg(hHandle_)
        elif topic.value[:5] == 'MATCH':
            self.parseMatchMsg(hHandle_)
        logger.info("topic:%s", topic.value)

    def parseMsg(self, msgstr_):
        try:
            hHandle = c_void_p(0)
            self._ma.maCli_Init(byref(hHandle))
            self._ma.maCli_Parse(hHandle, c_char_p(msgstr_), c_int(len(msgstr_)))
            funid = create_string_buffer(8+1)
            self._ma.maCli_GetHdrValueS(hHandle, funid, len(funid), defineDict['MACLI_HEAD_FID_FUNC_ID'])
            logger.debug("fundid:%s", funid.value)

            #处理订阅类消息
            if funid.value[:2] == '00':
                logger.info("00 msg:%s", msgstr_)
                return  self.parseSubMsg(hHandle)

            itablecount = c_int(0)
            self._ma.maCli_GetTableCount(hHandle, byref(itablecount))
            logger.debug("itablecount:%s", itablecount)
            msgcode, msglevel, msgtext = self.parseFirstTable(hHandle)
            logger.debug("msgcode:%s, msglevel:%s, msgtext:%s", msgcode.value, msglevel.value, msgtext.value)

            if msgcode.value == 0:
                logger.info("reply funid:%s name:%s success with second table result",
                            funid.value,
                            funNameDict[funid.value])
                ret = self.parseSecondTable(hHandle, funid)
                logger.debug("ret:%s", ret)

                if funid.value in self._dealReplyDict:
                    self._dealReplyDict[funid.value](ret)
            elif msgcode.value == 100:
                logger.info("reply funid:%s name:%s success without second table result",
                            funid.value,
                            funNameDict[funid.value])
            else:
                logger.error("reply funid:%s name:%s failed errcode:%s",
                             funid.value,
                             funNameDict[funid.value],
                             msgcode.value)
            self._ma.maCli_Close(hHandle)
            self._ma.maCli_Exit(hHandle)

        except BaseException,e:
            logger.exception(e)

    def parseFirstTable(self, hHandle_):
        self._ma.maCli_OpenTable(hHandle_, 1)
        self._ma.maCli_ReadRow(hHandle_, 1)
        msgcode = c_int(0)
        msglevel = c_char('0')
        msgtext = create_string_buffer(256+1)
        self._ma.maCli_GetValueN(hHandle_, byref(msgcode), fixDict['MSG_CODE'])
        self._ma.maCli_GetValueC(hHandle_, byref(msglevel), fixDict['MSG_LEVEL'])
        self._ma.maCli_GetValueS(hHandle_, byref(msgtext), len(msgtext), fixDict['MSG_TEXT'])

        return msgcode, msglevel, msgtext

    def parseSecondTable(self, hHandle_, funid_):
        if not funid_.value in replyMsgParam:
            logger.warn("funid:%s is not find in replyMsgParam", funid_.value)
            return

        self._ma.maCli_OpenTable(hHandle_, 2)
        ret = []
        irowcount = c_int(0)
        self._ma.maCli_GetRowCount(hHandle_, byref(irowcount))
        for i in range(1, irowcount.value + 1):
            self._ma.maCli_ReadRow(hHandle_, i)
            retdict = {}


            for fixidx_,type_ in replyMsgParam[funid_.value].iteritems():
                if type_ == 'l':
                    l = c_int64(0)
                    self._ma.maCli_GetValueL(hHandle_, byref(l), fixDict[fixidx_])
                    retdict[fixidx_] = l.value
                elif type_ == 'd':
                    d = c_double(0.0)
                    self._ma.maCli_GetValueD(hHandle_, byref(d), fixDict[fixidx_])
                    retdict[fixidx_] = d.value
                elif type_ == 'c':
                    c = c_char('0')
                    self._ma.maCli_GetValueC(hHandle_, byref(c), fixDict[fixidx_])
                    retdict[fixidx_] = c.value
                elif type_ == 'n':
                    n = c_int(0)
                    self._ma.maCli_GetValueN(hHandle_, byref(n), fixDict[fixidx_])
                    retdict[fixidx_] = n.value
                elif type_[0] == 's':
                    len_ = int(type_.split(',')[1]) + 1
                    s = create_string_buffer(len_)
                    self._ma.maCli_GetValueS(hHandle_, byref(s), len_, fixDict[fixidx_])
                    retdict[fixidx_] = s.value
            ret.append(retdict)
        return ret

    def dealLogonBackendReply(self, ret_):
        try:
            for retdict in ret_:
                if len(retdict['SESSION_ID']) > 0:
                    self._session = c_char_p(retdict['SESSION_ID'])
                    logger.info("set the _session to %s", retdict['SESSION_ID'])
                self._int_org = c_int(int(retdict["INT_ORG"]))
                logger.info("set the _int_org to %s", self._int_org)

                if not retdict["STKBD"] in self._bd2tradacc_dict:
                    self._bd2tradacc_dict[retdict["STKBD"]] = retdict["STK_TRDACCT"]

            self.subOrderAck()
            self.subMatchAck()

        except BaseException,e:
            logger.exception(e)

    def dealQueryMoneyReply(self, ret_):
        pass
    def dealQueryPositionReply(self, ret_):
        pass
    def dealQueryOrderTodayReply(self, ret_):
        pass
    def dealQueryMatchTodayReply(self, ret_):
        pass
    def dealQuantOrderReply(self, ret_):
        try:
            for retdict in ret_:
                logger.info("ORDER_BSN:%s, ORDER_NO:%s, ORDER_TIME:%s, EXE_STATUS:%s, EXE_INFO:%s, TRD_CODE:%s, TRD_BIZ:%s",
                            retdict["ORDER_BSN"],
                            retdict["ORDER_NO"],
                            retdict["ORDER_TIME"],
                            retdict["EXE_STATUS"],
                            retdict["EXE_INFO"],
                            retdict["TRD_CODE"],
                            retdict["TRD_BIZ"])

        except BaseException,e:
            logger.exception(e)
