# -*- coding: utf-8 -*-
__author__ = 'xujh'

from data_type import *
import datetime
import logging
import base64
logger = logging.getLogger("run")


#typedef void (* Fun_OnMsgPtr)(const char *msg, int len, const char *account, void *param);


    #print pAccount.values

#onMsgFv = WINFUNCTYPE(None, c_char_p, c_int, c_char_p, c_void_p)
#onMsgFv = CFUNCTYPE(None, POINTER(c_char), c_int, POINTER(c_char), c_void_p)


class Ma(object):
    def __init__(self, acc_, pwd_):
        try:
            self._ma = WinDLL("maCliApi.dll")
            self._ea = WinDLL("GxTS.dll")
            self._acc = c_char_p(acc_)
            self._pwd = c_char_p(pwd_)

            onMsgFv = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_void_p)
            onMsgHandle = onMsgFv(self.onMsg)
            iret = self._ea.AxE_Init(None, None, onMsgHandle, None)
            print iret

        except BaseException,e:
            logger.exception(e)
            raise e

    def onMsg(pMsg, iLen, pAccount, pParam):
        print "onMsg"
        print pMsg.decode("gbk")
        print iLen
        print pAccount
        
    def setPkgHead(self, hHandle_, pkgtype_, msgtype_, funtype_, funid_, msgid_):
        try:
            self._ma.maCli_SetHdrValueC(hHandle_, c_char(pkgtype_), defineDict['MACLI_HEAD_FID_PKT_TYPE'])
            self._ma.maCli_SetHdrValueC(hHandle_, c_char(msgtype_), defineDict['MACLI_HEAD_FID_MSG_TYPE'])
            self._ma.maCli_SetHdrValueC(hHandle_, c_char_p('01'), defineDict['MACLI_HEAD_FID_PKT_VER'])
            self._ma.maCli_SetHdrValueC(hHandle_, c_char(funtype_), defineDict['MACLI_HEAD_FID_FUNC_TYPE'])
            self._ma.maCli_SetHdrValueC(hHandle_, c_char_p(funid_), defineDict['MACLI_HEAD_FID_FUNC_ID'])
            self._ma.maCli_SetHdrValueC(hHandle_, msgid_, defineDict['MACLI_HEAD_FID_MSG_ID'])

        except BaseException,e:
            logger.exception(e)
            raise e

    def genReqId(self):
        return int(datetime.datetime.now().strftime("%H%M%S%f")[0:-3])

    #def setEagleMsgHead(self, ):
    def sendReqMsg(self, b64bizdata_, reqid_, funid_, msgid_, cmdid_ = 40002):
        msg = "%d\1%d\1%s\1%s\1%s\1%s"%(cmdid_, reqid_, self._acc, funid_, msgid_,b64bizdata_)
        print msg


    def logonEa(self):
        loginfo = NewLoginInfo()
        loginfo.account = self._acc.value
        loginfo.password = self._acc.value + "@GXTS"
        loginfo.accountType = c_int(6)
        loginfo.autoReconnect = c_int(0)
        loginfo.serverCount = c_int(1)
        loginfo.servers[0].szIp = "58.61.28.212"
        loginfo.servers[0].nPort = c_int(9104)
        print loginfo

        self._ea.AxE_NewMultiLogin(byref(loginfo))

    def logonBackend(self):
        try:
            hHandle = c_void_p(0)
            self._ma.maCli_Init(byref(hHandle))
            self._ma.maCli_BeginWrite(hHandle)
            reqid = self.genReqId()
            funid = "10301105"
            msgid = create_string_buffer(32)
            self._ma.maCli_GetUuid(hHandle, msgid, len(msgid))

            self.setPkgHead(hHandle, "B", "R", "Q", funid, msgid)
            self._ma.maCli_SetValueS(hHandle, c_char_p("Z"), fixDict['ACCT_TYPE'])
            self._ma.maCli_SetValueS(hHandle, self._acc, fixDict['ACCT_ID'])
            self._ma.maCli_SetValueS(hHandle, c_char_p("0"), fixDict['USE_SCOPE'])
            self._ma.maCli_SetValueS(hHandle, self._acc, fixDict['ENCRYPT_KEY'])
            self._ma.maCli_SetValueS(hHandle, c_char_p("0"), fixDict['AUTH_TYPE'])
            szVersion = create_string_buffer(32)
            self._ma.maCli_GetVersion(hHandle, szVersion, len(szVersion))
            self._ma.maCli_SetValueS(hHandle, szVersion, fixDict['SESSION_ID'])
            szAuthData = create_string_buffer(128)
            self._ma.maCli_ComEncrypt(hHandle, szAuthData, len(szAuthData), self._acc, self._pwd)
            self._ma.maCli_SetValueS(hHandle, szAuthData, fixDict['AUTH_DATA'])
            self._ma.maCli_EndWrite(hHandle)

            ilen = c_int(0)
            pBizData = c_char_p(0)
            self._ma.maCli_Make(hHandle, byref(pBizData), byref(ilen))
            b64bizdata = base64.b64encode(pBizData.value)
            self._ma.maCli_Close(hHandle)
            self._ma.maCli_Exit(hHandle)

            self.sendReqMsg(b64bizdata, reqid, funid, msgid)
        except BaseException,e:
            logger.exception(e)
            raise e

def onMsg(pMsg, iLen, pAccount, pParam):
    print "onMsg"
    print pMsg.decode("gbk")
    print iLen
    print pAccount

onMsgFv = CFUNCTYPE (None, c_char_p, c_int, c_char_p, c_void_p)
onMsgHandle = onMsgFv(onMsg)

def test():
    gxts = WinDLL("GxTS.dll")

    #onMsgFv = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_void_p)
    
    gxts.AxE_Init(None, None, onMsgHandle, None)
    loginfo = NewLoginInfo()
    loginfo.account = "110000035019"
    loginfo.password = "110000035019@GXTS"
    loginfo.accountType = c_int(6)
    loginfo.autoReconnect = c_int(0)
    loginfo.serverCount = c_int(1)
    loginfo.servers[0].szIp = "58.61.28.212"
    loginfo.servers[0].nPort = c_int(9104)
    print loginfo
    
    gxts.AxE_NewMultiLogin(byref(loginfo))

CALLBACK = CFUNCTYPE (None, c_char_p, c_int, c_char_p, c_void_p)

class Myclass(object):
    def getCallbackFunc(self):
        def func(pMsg, iLen, pAccount, pParam):
            print "func"
            print pMsg.decode("gbk")
            print iLen
            print pAccount
            #self.doSomething(pMsg, iLen, pAccount, pParam)
        return CALLBACK(func)
    @staticmethod
    def cbfun(pMsg, iLen, pAccount, pParam):
        print "cbfun"
        print pMsg.decode("gbk")
        print iLen
        print pAccount       
        

    def doSomething(self, pMsg, iLen, pAccount, pParam):
        print "doSomething"
        print pMsg.decode("gbk")
        print iLen
        print pAccount

    def doRegister(self):
        gxts = WinDLL("GxTS.dll")
        onCB = CALLBACK(Myclass.cbfun)
        gxts.AxE_Init(None, None, onMsgHandle, None)

        loginfo = NewLoginInfo()
        loginfo.account = "110000035019"
        loginfo.password = "110000035019@GXTS"
        loginfo.accountType = c_int(6)
        loginfo.autoReconnect = c_int(0)
        loginfo.serverCount = c_int(1)
        loginfo.servers[0].szIp = "58.61.28.212"
        loginfo.servers[0].nPort = c_int(9104)
        print loginfo

        gxts.AxE_NewMultiLogin(byref(loginfo))

#if __name__ == "__main__":
#    import sys
#    import os
#    sys.path.append(os.getcwd())
    # matest = Ma("110000035019", "111111")
    # matest.logonEa()
    #matest.logonBackend()

#test()
ca = Myclass()
ca.doRegister()
#test()
while(True):
    pass

# CALLBACK = ctypes.CFUNCTYPE(None, ctypes.POINTER(Notification))
#
# class MyClass(object):
#
#     def getCallbackFunc(self):
#         def func(Notification):
#             self.doSomething(Notification)
#         return CALLBACK(func)
#
#     def doRegister(self):
#         myLib.RegisterNofityCallback(45454, 0, self.getCallbackFunc())