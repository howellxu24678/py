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
fixDict['STKEX'] = c_char_p("207")#交易市场
fixDict['STKBD'] = c_char_p("625")#交易板块
fixDict['STK_TRDACCT'] = c_char_p("448")#证券账户

fixDict['OP_USER'] = c_char_p("8810")#操作用户代码
fixDict['OP_ROLE'] = c_char_p("8811")#操作用户角色
fixDict['OP_SITE'] = c_char_p("8812")#操作站点
fixDict['CHANNEL'] = c_char_p("8813")#操作渠道
fixDict['SESSION_ID'] = c_char_p("8814")#会话凭证
fixDict['FUNCTION'] = c_char_p("8815")#功能代码
fixDict['RUNTIME'] = c_char_p("8816")#调用时间
fixDict['OP_ORG'] = c_char_p("8821")#操作机构

fixDict['CUST_CODE'] = c_char_p("8902")#客户代码
fixDict['INT_ORG'] = c_char_p("8911")#内部机构
fixDict['CUACCT_CODE'] = c_char_p("8920")#资产账户
fixDict['CUACCT_ATTR'] = c_char_p("8921")#资产账户属性
fixDict['TRDACCT_SN'] = c_char_p("8928")#账户序号
fixDict['TRDACCT_EXID'] = c_char_p("8929")#报盘账户
fixDict['TRDACCT_NAME'] = c_char_p("8932")#交易账户名称
fixDict['TRDACCT_STATUS'] = c_char_p("8933")#账户状态
fixDict['TREG_STATUS'] = c_char_p("8934")#指定状态
fixDict['BREG_STATUS'] = c_char_p("8935")#回购状态
fixDict['STKPBU'] = c_char_p("8943")#交易单元
fixDict['ACCT_TYPE'] = c_char_p("8987")#账户类型

fixDict['ACCT_ID'] = c_char_p("9081")#账户标识
fixDict['USE_SCOPE'] = c_char_p("9082")#使用范围
fixDict['AUTH_TYPE'] = c_char_p("9083")#认证类型
fixDict['AUTH_DATA'] = c_char_p("9084")#认证数据
fixDict['ENCRYPT_KEY'] = c_char_p("9086")#加密因子


fixDict['MSG_CODE'] = c_char_p("8817")#信息代码
fixDict['MSG_LEVEL'] = c_char_p("8818")#信息级别
fixDict['MSG_TEXT'] = c_char_p("8819")#信息正文


replyMsgParam = {}
replyMsgParam['10301105'] = {'CUST_CODE': 'l',
                             'CUACCT_CODE': 'l',
                             'STKEX' : 'c',
                             'STKBD' : 's,2',
                             'STK_TRDACCT' : 's,10',
                             'TRDACCT_SN': 'n',
                             'TRDACCT_EXID' : 's,10',
                             'TRDACCT_STATUS' : 'c',
                             'TREG_STATUS' : 'c',
                             'BREG_STATUS' : 'c',
                             'STKPBU' : 's,8',
                             'ACCT_TYPE' : 's,2',
                             'ACCT_ID' : 's,32',
                             'TRDACCT_NAME' : 's,32',
                             'SESSION_ID' : 's,128',
                             'INT_ORG' : 'n',
                             'CUACCT_ATTR' : 'c'
                             }


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