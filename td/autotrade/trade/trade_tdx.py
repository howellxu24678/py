# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 16:08:55 2015

@author: guosen
"""
from tradebase import *
from winguiauto_tdx import * 

class tdx_trade(trade):
    def __init__(self, cf):
        super(tdx_trade, self).__init__(cf)
        self.__hwnd = findTopWindow(wantedClass='TdxW_MainFrame_Class')
        if self.__hwnd == 0:
            logger.critical(u'华泰通达信交易软件没有运行！')
            raise RuntimeError, 'tdx_trade init failed'
        else:
            self.__button = {'refresh': 180, 'position': 145, 'deal': 112, 'withdrawal': 83, 'sell': 50, 'buy': 20}
            windows = dumpWindows(self.__hwnd)
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
            logger.info('tdx_trade init success')

    def buy(self, stock_code, stock_price, stock_number):
        """
        买入函数
        :param code: 股票代码，字符串
        :param quantity: 数量， 字符串
        """
        logger.info("begin to buy % with number %", stock_code, stock_number)
        self.clickRefreshButton()
        setEditText(self.__buy_sell_hwnds[0][0], stock_code)
        time.sleep(0.3)
        if stock_number != '0':
            setEditText(self.__buy_sell_hwnds[3][0], stock_number)
            time.sleep(0.3)
        click(self.__buy_sell_hwnds[5][0])
        time.sleep(0.3)
        closePopupWindows(self.__hwnd)
        logger.info("end to buy % with number %", stock_code, stock_number)

    def sell(self, stock_code, stock_price, stock_number):
        """
        卖出函数
        :param code: 股票代码， 字符串
        :param quantity: 数量， 字符串
        """
        logger.info("begin to sell % with number %", stock_code, stock_number)
        self.clickRefreshButton()
        setEditText(self.__buy_sell_hwnds[24][0], stock_code)
        time.sleep(0.3)
        if stock_number != '0':
            setEditText(self.__buy_sell_hwnds[27][0], stock_number)
            time.sleep(0.3)
        click(self.__buy_sell_hwnds[29][0])
        time.sleep(0.3)
        closePopupWindows(self.__hwnd)
        logger.info("end to sell % with number %", stock_code, stock_number)

    def clickRefreshButton(self):
        """
        点击刷新按钮
        """
        clickMenuButton(self.__menu_hwnds[0][0], self.__button['refresh'])

    def getMoneyInfo(self):
        """
        :return:可用资金
        """
        self.clickRefreshButton()
        setEditText(self.__buy_sell_hwnds[24][0], '999999')  # 测试时获得资金情况
        time.sleep(0.3)
        money = getWindowText(self.__buy_sell_hwnds[12][0]).strip()
        return float(money)

    def getPositionInfo(self):
        """获取持仓股票信息
        """
        self.clickRefreshButton()
        return getListViewInfo(self.__buy_sell_hwnds[64][0], 5)
  

if __name__ == "__main__":
    cf = ConfigParser.ConfigParser()
    tdx_trade = tdx_trade(cf)
    #tdx_trade.buy('000001', None, '100')
    print  tdx_trade.getPositionInfo()
    
    #time.sleep(10)
    #print result
#    for re in result:
#        for e in re:
#            print e

        
        
