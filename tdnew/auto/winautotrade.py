# -*- coding: utf-8 -*-
__author__ = 'xujh'

import time
import pywinauto
from eventengine import *
import logging
logger = logging.getLogger("run")

class TdxWinTrade(object):
    def __init__(self, cf, eventEngine_):
        try:
            self._cf = cf
            self.initTradeHandle()
            self._eventEngine = eventEngine_
        except BaseException,e:
            logger.exception(e)
            raise e

    def initAsTrader(self):
        codelist = self._cf.get("tdx", "codelist").strip().split(',')
        for code in codelist:
            self._eventEngine.register(EVENT_TRADE_CONTRACT + code, self.onOrder)
        self._to_addr_list = self._cf.get("tdx", "reveiver")
        logger.info("ma deal with codelist:%s, toaddrlist:%s", codelist, self._to_addr_list)

    def initTradeHandle(self):
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

    def __buy(self, code, quantity):
        """
        买入函数
        :param code: 股票代码，字符串
        :param quantity: 数量， 字符串
        """
        self.__controls.Edit1.SetEditText(code)
        time.sleep(0.2)
        if quantity != '0':
            self.__controls.Edit3.SetEditText(quantity)
            time.sleep(0.2)
        self.__controls.Button1.Click()
        time.sleep(0.2)

    def __sell(self, code, quantity):
        """
        卖出函数
        :param code: 股票代码， 字符串
        :param quantity: 数量， 字符串
        """
        self.__controls.Edit4.SetEditText(code)
        time.sleep(0.2)
        if quantity != '0':
            self.__controls.Edit6.SetEditText(quantity)
            time.sleep(0.2)
        self.__controls.Button2.Click()
        time.sleep(0.2)

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


    def onOrder(self, event_):
        try:
            code =  event_.dict_['code']
            qty = int(event_.dict_['number'])
            if event_.dict_['direction'] == 'buy':
                self.__buy(code, qty)
            elif event_.dict_['direction'] == 'sell':
                self.__sell(code, qty)

            while self.__closePopupWindow():
                time.sleep(0.2)
        except BaseException,e:
            logger.exception(e)

    def order(self, code, direction, quantity):
        """
        下单函数
        :param code: 股票代码， 字符串
        :param direction: 买卖方向
        :param quantity: 数量， 字符串，数量为‘0’时，由交易软件指定数量
        """
        if direction == 'B':
            self.__buy(code, quantity)
        if direction == 'S':
            self.__sell(code, quantity)
        while self.__closePopupWindow():
            time.sleep(0.2)

    def maximizeWindow(self):
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

    def getMoney(self):
        """获取可用资金
        """
        self.__controls.Edit1.SetEditText('999999')  # 测试时获得资金情况
        time.sleep(0.2)
        money = self.__controls.Static6.WindowText()
        return float(money)

    def getPosition(self):
        """获取持仓股票信息
        """
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


if __name__ == "__main__":
    #import time
    import os
    import logging
    import logging.config
    import ConfigParser
    baseconfdir="conf"
    loggingconf= "logging.config"
    quickfixconf= "quickfix.ini"
    businessconf= "business.ini"
    logging.config.fileConfig(os.path.join(os.getcwd(), '..', baseconfdir, loggingconf))
    logger = logging.getLogger("run")

    cf = ConfigParser.ConfigParser()
    eventEngine = EventEngine()
    tdxa = TdxWinTrade(cf,eventEngine)
    while(True):
        try:
            logger.info("getMoney:%s", tdxa.getMoney())
            logger.info("getPosition:%s", tdxa.getPosition())
            time.sleep(10)
        except BaseException,e:
            logger.exception(e)