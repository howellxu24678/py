# -*- coding: utf-8 -*-
__author__ = 'xujh'
from ctypes import *

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

fixDict = {}
fixDict['ACCT_TYPE'] = c_char_p("8987")
fixDict['ACCT_ID'] = c_char_p("9081")
fixDict['USE_SCOPE'] = c_char_p("9082")
fixDict['ENCRYPT_KEY'] = c_char_p("9086")
fixDict['AUTH_TYPE'] = c_char_p("9083")
fixDict['AUTH_DATA'] = c_char_p("9084")
fixDict['SESSION_ID'] = c_char_p("8814")


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