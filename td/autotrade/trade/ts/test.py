#import  gxts
#
#
#cl = gxts.cvar.eagle
#print "loaddll", cl.LoadDll()
#print cl.test()


#>>> from ctypes import *
#>>>
#>>> class S(Structure):
#...     _fields_ = [
#...         ('a', c_byte),
#...         ('b', c_int),
#...         ('c', c_float),
#...         ('d', c_double)
#...     ]
#...
#>>> s = S(1, 2, 3, 4.0)
#>>>
#>>> for field_name, field_type in s._fields_:
#...     print field_name, getattr(s, field_name)

#import sys
#import os
#sys.path.append(os.getcwd())
#sys.path.append(os.path.join(os.getcwd(),"maClient"))

from ctypes import *
macliapi = WinDLL("maCliApi.dll")
hHandle = c_void_p(0)
macliapi.maCli_Init(byref(hHandle))

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
                
gxts = WinDLL("GxTS.dll")



macliapi.maCli_BeginWrite(hHandle)
macliapi.maCli_SetHdrValueC(hHandle, c_char('Q'), c_int(1052672))
macliapi.maCli_SetValueS(hHandle, c_char_p("127.0.0.1"), c_char_p("8812"))
macliapi.maCli_EndWrite(hHandle)
ilen = c_int(0)
p = create_string_buffer(1024)
macliapi.maCli_Make(hHandle,p, byref(ilen))
macliapi.maCli_Close(hHandle)
macliapi.maCli_Exit(hHandle)

#typedef void (* Fun_OnMsgPtr)(const char *msg, int len, const char *account, void *param);



def onMsg(pMsg, iLen, pAccount, pParam):
    print "onMsg"
    print pMsg.decode("gbk")
    print iLen
    print pAccount
    #print pAccount.values
    
#onMsgFv = WINFUNCTYPE(None, c_char_p, c_int, c_char_p, c_void_p)
#onMsgFv = CFUNCTYPE(None, POINTER(c_char), c_int, POINTER(c_char), c_void_p)
onMsgFv = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_void_p)
onMsgHandle = onMsgFv(onMsg)
null_ptr = POINTER(c_int)()
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

#gxts.AxE_NewMultiLogin(byref(loginfo))

    




