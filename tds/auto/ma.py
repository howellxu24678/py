# -*- coding: utf-8 -*-
__author__ = 'xujh'

from data_type import *
from eventengine import *

import datetime
import logging
import base64
import socket
logger = logging.getLogger("run")


def onMsg(pMsg, iLen, pAccount, pParam):
    logger.info("onAxEagle callback msgLen:%s", iLen)
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
            #self._ea = WinDLL("testdll.dll")
            self._ea = WinDLL("GxTS.dll")
            self._eventEngine = eventEngine_
            self._eventEngine.register(EVENT_AXEAGLE, self.onRecvMsg)

            self._ip = cf.get("ma", "ip")
            self._port = cf.getint("ma","port")
            self._acc = c_char_p(cf.get("ma", "account"))
            self._pwd = c_char_p(cf.get("ma", "password"))
            self._session = None
            #self._reqid = 0

            self._dealReplyDict = {}
            self._dealReplyDict['10301105'] = self.dealLogonBackendReply
            self._dealReplyDict['10301105'] = self.dealQueryMoneyReply

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
            raise e

    def setRegular(self, hHandle_):
        try:
            self._ma.maCli_SetValueS(hHandle_, self._acc, fixDict['OP_USER'])
            self._ma.maCli_SetValueC(hHandle_, c_char('1'), fixDict['OP_ROLE'])
            self._ma.maCli_SetValueS(hHandle_, self._localIp, fixDict['OP_SITE'])
            self._ma.maCli_SetValueC(hHandle_, c_char('0'), fixDict['CHANNEL'])
            self._ma.maCli_SetValueS(hHandle_, c_char_p("10301105"), fixDict['FUNCTION'])
            if self._session is None:
                szVersion = create_string_buffer(32+1)
                self._ma.maCli_GetVersion(hHandle_, szVersion, len(szVersion))
                self._session = szVersion
            self._ma.maCli_SetValueS(hHandle_, self._session, fixDict['SESSION_ID'])
            self._ma.maCli_SetValueS(hHandle_,
                                     c_char_p(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
                                     fixDict['RUNTIME'])
            self._ma.maCli_SetValueN(hHandle_, c_int(0), fixDict['OP_ORG'])
        except BaseException,e:
            logger.exception(e)
            raise e
    def genReqId(self):
        # self._reqid += 1
        # return  self._reqid
        return int(datetime.datetime.now().strftime("%H%M%S%f")[0:-3])

    def sendReqMsg(self, b64bizdata_, reqid_, funid_, msgid_, cmdid_ = 40002):
        msg = "%d\1%d\1%s\1%s\1%s\1%s"%(cmdid_,
                                        reqid_,
                                        self._acc.value,
                                        funid_,
                                        msgid_.value,
                                        b64bizdata_)
        logger.info("AxE_SendMsg:%s", msg)
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

        iret = self._ea.AxE_NewMultiLogin(byref(loginfo))
        logger.info("loginfo:%s AxE_NewMultiLogin return:%s", loginfo, iret)

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
            raise e

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
            raise e

    def genBizData(self, hHandle_):
        ilen = c_int(0)
        pBizData = c_char_p(0)
        self._ma.maCli_Make(hHandle_, byref(pBizData), byref(ilen))

        logger.info("before b64encode:%s", pBizData.value)
        b64bizdata = base64.encodestring(pBizData.value)
        self._ma.maCli_Close(hHandle_)
        self._ma.maCli_Exit(hHandle_)
        return  b64bizdata

    def onRecvMsg(self,event):
        logger.info("pMsg:%s", event.dict_["pMsg"])
        msgSplitList = event.dict_["pMsg"].split('\1')
        cmdId = msgSplitList[0]
        if cmdId == "40002":
            msgstr = base64.decodestring(msgSplitList[5])
            logger.info("pMsg:%s, iLen:%s, pAccount:%s",
                        msgstr,
                        event.dict_["iLen"],
                        event.dict_["pAccount"])

            self.parseMsg(msgstr)

        if cmdId == "40000":
            self.logonBackend()

    def parseMsg(self, msgstr_):
        try:
            hHandle = c_void_p(0)
            self._ma.maCli_Init(byref(hHandle))
            self._ma.maCli_Parse(hHandle, c_char_p(msgstr_), c_int(len(msgstr_)))
            funid = create_string_buffer(8+1)
            self._ma.maCli_GetHdrValueS(hHandle, funid, len(funid), defineDict['MACLI_HEAD_FID_FUNC_ID'])
            logger.info("fundid:%s", funid.value)
            itablecount = c_int(0)
            self._ma.maCli_GetTableCount(hHandle, byref(itablecount))
            logger.debug("itablecount:%s", itablecount)
            msgcode, msglevel, msgtext = self.parseFirstTable(hHandle)
            logger.info("msgcode:%s, msglevel:%s, msgtext:%s", msgcode.value, msglevel.value, msgtext.value)

            if msgcode.value == 0:
                ret = self.parseSecondTable(hHandle, funid)
                logger.info("ret:%s", ret)
                if funid.value in self._dealReplyDict:
                    self._dealReplyDict[funid.value](ret)

            elif msgcode.value == 100:
                logger.info("reply funid:%s success but the result is empty", funid)
            else:
                logger.error("reply funid:%s failed errcode:%s", funid, msgcode.value)

            self._ma.maCli_Close(hHandle)
            self._ma.maCli_Exit(hHandle)

        except BaseException,e:
            logger.exception(e)
            raise e

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
            self._ma.maCli_ReadRow(hHandle_, 1)
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
        for retdict in ret_:
            if not 'SESSION_ID' in retdict:
                logger.error("SESSION_ID is not in the reply of 10301105")
                return
            if len(retdict['SESSION_ID']) > 0:
                self._session = c_char_p(retdict['SESSION_ID'])
                logger.info("set the _session to %s", retdict['SESSION_ID'])

    def dealQueryMoneyReply(self, ret_):
        pass