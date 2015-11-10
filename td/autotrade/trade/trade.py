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
        self._cf = cf

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



import  pywinauto
class tdx_wa_trade(trade):
    def __init__(self,cf):
        try:
            super(tdx_wa_trade, self).__init__(cf)
            self.__app = pywinauto.application.Application()
            self.__app.connect(class_name='TdxW_MainFrame_Class')
            top_hwnd = pywinauto.findwindows.find_window(class_name='TdxW_MainFrame_Class')
            temp_hwnd = pywinauto.findwindows.find_windows(top_level_only=False, class_name='AfxWnd42', parent=top_hwnd)[-1]
            wanted_hwnd = pywinauto.findwindows.find_windows(top_level_only=False, parent=temp_hwnd)
            if len(wanted_hwnd) != 70:
                logger.critical(u'无法获得通达信双向委托界面的窗口句柄！')
                raise RuntimeError, 'tdx_trade init failed'
            menu_bar = wanted_hwnd[1]
            controls = wanted_hwnd[6]
            self.__main_window = self.__app.window_(handle=top_hwnd)
            self.__menu_bar = self.__app.window_(handle=menu_bar)
            self.__controls = self.__app.window_(handle=controls)

            logger.info("money:%s", self.getMoneyInfo())
            #logger.info("positioninfo:%s", self.getPositionInfo())
            logger.info('tdx_wa_trade init success')
        except BaseException,e:
            logger.exception(e)
            raise e
            
    def buy(self, stock_code, stock_price, stock_number):
        """
        买入函数
        :param stock_code: 股票代码，字符串
        :param stock_number: 数量， 字符串
        """
        logger.info("begin to buy %s with number %s", stock_code, stock_number)
        self.__controls.Edit1.SetEditText(stock_code)
        time.sleep(0.2)
        if stock_number != '0':
            self.__controls.Edit3.SetEditText(stock_number)
            time.sleep(0.2)
        self.__controls.Button1.Click()
        time.sleep(0.2)
        while self.__closePopupWindow():
            time.sleep(0.2)
        logger.info("end to buy %s with number %s", stock_code, stock_number)

    def sell(self, stock_code, stock_price, stock_number):
        """
        卖出函数
        :param stock_code: 股票代码， 字符串
        :param stock_number: 数量， 字符串
        """
        logger.info("begin to sell %s with number %s", stock_code, stock_number)
        self.__controls.Edit4.SetEditText(stock_code)
        time.sleep(0.2)
        if stock_number != '0':
            self.__controls.Edit6.SetEditText(stock_number)
            time.sleep(0.2)
        self.__controls.Button2.Click()
        time.sleep(0.2)
        while self.__closePopupWindow():
            time.sleep(0.2)
        logger.info("end to sell %s with number %s", stock_code, stock_number)

    def __closePopupWindow(self):
        """
        关闭一个弹窗。
        :return: 如果有弹出式对话框，返回True，否则返回False
        """
        popup_hwnd = self.__main_window.PopupWindow()
        if popup_hwnd:
            popup_window = self.__app.window_(handle=popup_hwnd)
            popup_window.SetFocus()
            popup_window.Button.Click()
            return True
        return False

    def maximizeFocusWindow(self):
        """
        最大化窗口
        """
        if self.__main_window.GetShowState() != 3:
            self.__main_window.Maximize()

    def minimizeWindow(self):
        """
        最小化窗体
        """
        self.__main_window.Minimize()

    def clickRefreshButton(self, t=0.5):
        """点击刷新按钮
        """
        self.__menu_bar.ClickInput(coords=(180, 12))
        time.sleep(t)

    def getMoneyInfo(self):
        """获取可用资金
        """
        self.clickRefreshButton()
        self.__controls.Edit1.SetEditText('000001')  # 测试时获得资金情况
        time.sleep(0.2)
        money = self.__controls.Static6.WindowText()
        return float(money)

    def getPositionInfo(self):
        """获取持仓股票信息
        """
        self.clickRefreshButton()
        position = []
        rows = self.__controls.ListView.ItemCount()
        cols = 10
        info = self.__controls.ListView.Texts()[1:]
        for row in range(rows):
            position.append(info[row * cols:(row + 1) * cols])
        return position

    def getDeal(self, code, pre_position, cur_position):
        """
        获取成交数量
        :param code: 股票代码
        :param pre_position: 下单前的持仓
        :param cur_position: 下单后的持仓
        :return: 0-未成交， 正整数是买入的数量， 负整数是卖出的数量
        """
        if pre_position == cur_position:
            return 0
        pre_len = len(pre_position)
        cur_len = len(cur_position)
        if pre_len == cur_len:
            for row in range(cur_len):
                if cur_position[row][0] == code:
                    return int(float(cur_position[row][1]) - float(pre_position[row][1]))
        if cur_len > pre_len:
            return int(float(cur_position[-1][1]))

        
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

if __name__ == "__main__":
    cf = ConfigParser.ConfigParser()
    tdx = tdx_wa_trade(cf)
    #tdx.buy('000001', None, '100')
    #tdx.buy('000001', None, '100')
    #tdx.getMoneyInfo()