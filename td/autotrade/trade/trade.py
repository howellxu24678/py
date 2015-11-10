# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 19:06:35 2015

@author: guosen
"""


import quickfix as fix
import fix_app


from winguiauto import *
import time
import datetime
import ConfigParser

import logging
logger = logging.getLogger("run")

class trade(object):
    def __init__(self, cf):
        self._cf = cf;

    def buy(self, stock_code, stock_price, stock_number):
        pass

    def sell(self, stock_code, stock_price, stock_number):
        pass


class ths_trade(trade):
    def __init__(self,cf):
        super(ths_trade, self).__init__(cf)
        self.__top_hwnd = findTopWindow(wantedText = u'网上股票交易系统5.0')
        if self.__top_hwnd == 0:
            logger.critical(u'华泰交易软件没有运行！')
            raise RuntimeError, 'gui_trade init failed'
        else:
            try:
                temp_hwnds = dumpWindows(self.__top_hwnd)
                self.__wanted_hwnds = findSubWindows(temp_hwnds, 70)  # 华泰专用版
                # self.__wanted_hwnds = findSubWindows(temp_hwnds, 73)   # 同花顺通用版
                self.__control_hwnds = []
                for hwnd, text_name, class_name in self.__wanted_hwnds:
                    if class_name in ('Button', 'Edit'):
                        self.__control_hwnds.append((hwnd, text_name, class_name))
                logger.info('gui_trade init success')
            except BaseException,e:
                logger.critical(e)
                raise e
    
    def buy(self, stock_code, stock_price, stock_number):
        try:
            if closePopupWindow(self.__top_hwnd, wantedClass='Button'):
                time.sleep(5)
            click(self._hwnd_child_controls[0][0])
            setEditText(self._hwnd_child_controls[0][0], stock_code)
            time.sleep(0.5)
            if not stock_price is None:
                setEditText(self._hwnd_child_controls[1][0], stock_price)
                time.sleep(0.5)       
            setEditText(self._hwnd_child_controls[2][0], stock_number)
            time.sleep(0.5)
            clickButton(self._hwnd_child_controls[3][0])
            time.sleep(1)
            return not closePopupWindow(self.__top_hwnd, wantedClass='Button')
        except BaseException,e:
            logger.exception(e)
        
    def sell(self, stock_code, stock_price, stock_number):
        try:
            if closePopupWindow(self.__top_hwnd, wantedClass='Button'):
                time.sleep(5)
            click(self._hwnd_child_controls[4][0])
            setEditText(self._hwnd_child_controls[4][0], stock_code)
            time.sleep(0.5)
            if not stock_price is None:
                setEditText(self._hwnd_child_controls[5][0], stock_price)
                time.sleep(0.5)
            setEditText(self._hwnd_child_controls[6][0], stock_number)
            time.sleep(0.5)
            clickButton(self._hwnd_child_controls[7][0])
            time.sleep(1)
            return not closePopupWindow(self.__top_hwnd, wantedClass='Button')
        except BaseException,e:
            logger.exception(e)

class tdx_trade(trade):
    def __init__(self, cf):
        try:
            super(tdx_trade, self).__init__(cf)
            self.__top_hwnd = findTopWindow(wantedClass='TdxW_MainFrame_Class')
            if self.__top_hwnd == 0:
                logger.critical(u'华泰通达信交易软件没有运行！')
                raise RuntimeError, 'tdx_trade init failed'
            else:
                self.__button = {'refresh': 180, 'position': 145, 'deal': 112, 'withdrawal': 83, 'sell': 50, 'buy': 20}
                windows = dumpWindows(self.__top_hwnd)
                temp_hwnd = 0
                for window in windows:
                    child_hwnd, window_text, window_class = window
                    if window_class == 'AfxMDIFrame42':
                        temp_hwnd = child_hwnd
                        break
                temp_hwnds = dumpWindow(temp_hwnd)
                temp_hwnds = dumpWindow(temp_hwnds[1][0])
                self.__menu_hwnds = dumpWindow(temp_hwnds[0][0])
                self.__buy_sell_hwnds = dumpWindow(temp_hwnds[4][0])
                if len(self.__buy_sell_hwnds) not in (68,):
                    logger.critical(u'无法获得通达信对买对卖界面的窗口句柄！')
                    raise RuntimeError, 'tdx_trade init failed'
                logger.info("money:%s", self.getMoneyInfo())
                #logger.info("positioninfo:%s", self.getPositionInfo())
                logger.info('tdx_trade init success')
        except BaseException,e:
            logger.exception(e)
            raise e

    def buy(self, stock_code, stock_price, stock_number):
        """
        买入函数
        :param code: 股票代码，字符串
        :param quantity: 数量， 字符串
        """
        logger.info("begin to buy %s with number %s", stock_code, stock_number)
        self.clickRefreshButton()
        setEditText(self.__buy_sell_hwnds[0][0], stock_code)
        time.sleep(0.3)
        if stock_number != '0':
            setEditText(self.__buy_sell_hwnds[3][0], stock_number)
            time.sleep(0.3)
        click(self.__buy_sell_hwnds[5][0])
        time.sleep(0.3)
        closePopupWindows(self.__top_hwnd)
        logger.info("end to buy %s with number %s", stock_code, stock_number)

    def sell(self, stock_code, stock_price, stock_number):
        """
        卖出函数
        :param code: 股票代码， 字符串
        :param quantity: 数量， 字符串
        """
        logger.info("begin to sell %s with number %s", stock_code, stock_number)
        self.clickRefreshButton()
        setEditText(self.__buy_sell_hwnds[24][0], stock_code)
        time.sleep(0.3)
        if stock_number != '0':
            setEditText(self.__buy_sell_hwnds[27][0], stock_number)
            time.sleep(0.3)
        click(self.__buy_sell_hwnds[29][0])
        time.sleep(0.3)
        closePopupWindows(self.__top_hwnd)
        logger.info("end to sell %s with number %s", stock_code, stock_number)

    def clickRefreshButton(self):
        """
        点击刷新按钮
        """
        clickWindow(self.__menu_hwnds[0][0], self.__button['refresh'])

    def getMoneyInfo(self):
        """
        :return:可用资金
        """
        self.clickRefreshButton()
        setEditText(self.__buy_sell_hwnds[24][0], '000001')  # 测试时获得资金情况
        time.sleep(0.3)
        money = getWindowText(self.__buy_sell_hwnds[12][0]).strip()
        return float(money)

    def getPositionInfo(self):
        """获取持仓股票信息
        """
        self.clickRefreshButton()
        return getListViewInfo(self.__buy_sell_hwnds[64][0], 5)

    def maximizeFocusWindow(self):
        '''
        最大化窗口，获取焦点
        '''
        maxFocusWindow(self.__top_hwnd)

    def minimizeWindow(self):
        """
        最小化窗体
        """
        minWindow(self.__top_hwnd)

if __name__ == "__main__":
    cf = ConfigParser.ConfigParser()
    tdx_trade = tdx_trade(cf)
    #tdx_trade.buy('000001', None, '100')
    #tdx_trade.buy('000001', None, '100')
    #print  tdx_trade.getMoneyInfo()

    #time.sleep(10)
    #print result
#    for re in result:
#        for e in re:
#            print e

        
class fix_trade(trade):
    def __init__(self, initfile):
        self._initfile = initfile
        

    def GetConfig(self):
        cf = ConfigParser.ConfigParser()
        cf.read(self._initfile)
        self._clordid_prefix = cf.get("DEFAULT", "clordid_prefix")
        self._UserName = cf.get("SESSION", "UserName")
        self._PassWord = cf.get("SESSION", "Password")
        self._SenderCompID = cf.get("SESSION", "SenderCompID")
        self._TargetCompID = cf.get("SESSION", "TargetCompID")
        self._AccountType = cf.get("SESSION", "AccountType")
        self._RawData = self._AccountType + ":" + self._UserName + ":" + self._PassWord
        
        logger.info('__UserName:' + self._UserName + \
            " __SenderCompID:" + self._SenderCompID + \
            " __TargetCompID:" + self._TargetCompID + \
            "__clordid_prefix:" + self._clordid_prefix + \
            "__AccountType:" + self._AccountType)
            
    def create(self):
        try:
            self.GetConfig()
            
            self._settings = fix.SessionSettings( self._initfile )
            self._application = fix_app.Application()
            self._application.setParm(self._RawData)
            self._factory = fix.FileStoreFactory( self._settings )
            self._log = fix.FileLogFactory(self._settings)
            self._initiator = fix.SocketInitiator( self._application,self._factory, self._settings, self._log )
            self._initiator.start()
            self._sessionID = fix.SessionID( "FIX.4.2",self._SenderCompID ,self._TargetCompID)
            
            logger.info('fix_trade create')
            time.sleep( 4 )
        except BaseException,e:
            logger.exception(e)
            
    def genOrderID(self):
        return self._clordid_prefix + time.strftime("%H%M%S",time.localtime()) + str(datetime.datetime.now().microsecond/1000)    
        
    def close(self):
        self._initiator.stop()
    #新订单        
    def NewStockOrder(self):
        msg = fix.Message()
        msg.getHeader().setField(fix.MsgType(fix.MsgType_NewOrderSingle))
        msg.setField(fix.ClOrdID(self.genOrderID()))
        msg.setField(fix.HandlInst('1'))
        msg.setField(fix.OrdType(fix.OrdType_MARKET))
        msg.setField(fix.Side('1'))
        msg.setField(fix.Symbol("000001"))
        msg.setField(fix.TransactTime())
        msg.setField(fix.OrderQty(12500))
        msg.setField(fix.Currency("CNY"))
        msg.setField(fix.SecurityExchange("XSHE"))
        
        fix.Session.sendToTarget(msg, self._sessionID)
    # 资金股份查询
    def UAN(self, reqType):
        msg = fix.Message()
        msg.getHeader().setField(fix.MsgType("UAN"))
        msg.setField(fix.PosReqID(self.genOrderID()))
        msg.setField(fix.PosReqType(reqType))
        msg.setField(fix.Currency("CNY"))
        
        fix.Session.sendToTarget(msg, self._sessionID)
        
    def CancleOrder(self):
        pass
    
    def buy(self, stock_code, stock_price, stock_number):
        pass
        
    def sell(self, stock_code, stock_price, stock_number):
        pass