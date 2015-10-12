# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 19:07:38 2015

@author: guosen
"""

from winguiauto import *
    
def findWantedControls(hwnd):
    # 获取双向委托界面level3窗体下所有控件句柄
    hwndChildLevel1 = dumpSpecifiedWindow(hwnd, wantedClass='AfxMDIFrame42s')
    hwndChildLevel2 = dumpSpecifiedWindow(hwndChildLevel1[0])
    for handler in hwndChildLevel2:
        hwndChildLevel3 = dumpSpecifiedWindow(handler)
        if len(hwndChildLevel3) == 70:  # 在hwndChildLevel3下，共有70个子窗体
            return hwndChildLevel3


def closePopupWindow(hwnd, wantedText=None, wantedClass=None):
    # 如果有弹出式窗口，点击它的确定按钮
    hwndPopup = findPopupWindow(hwnd)
    if hwndPopup:
        hwndControl = findControl(hwndPopup, wantedText, wantedClass)
        clickButton(hwndControl)
        time.sleep(1)
        return True
    return False
    
def buy(hwnd, stock_code, stock_number):
    pressKey(hwnd, win32con.VK_F6)
    hwndControls = findWantedControls(hwnd)
    if closePopupWindow(hwnd, wantedClass='Button'):
        time.sleep(5)
    click(hwndControls[2])
    time.sleep(.5)
    setEditText(hwndControls[2], stock_code)
    time.sleep(.5)
    click(hwndControls[7])
    time.sleep(.5)
    setEditText(hwndControls[7], stock_number)
    time.sleep(.5)
    clickButton(hwndControls[8])
    time.sleep(1)
    return not closePopupWindow(hwnd, wantedClass='Button')


def sell(hwnd, stock_code, stock_number):
    pressKey(hwnd, win32con.VK_F6)
    hwndControls = findWantedControls(hwnd)
    if closePopupWindow(hwnd, wantedClass='Button'):
        time.sleep(5)
    click(hwndControls[11])
    time.sleep(.5)
    setEditText(hwndControls[11], stock_code)
    time.sleep(.5)
    click(hwndControls[16])
    time.sleep(.5)
    setEditText(hwndControls[16], stock_number)
    time.sleep(.5)
    clickButton(hwndControls[17])
    time.sleep(1)
    return not closePopupWindow(hwnd, wantedClass='Button')
    
hwnd_parent1 = findSpecifiedTopWindow(wantedText = u'网上股票交易系统5.0')
buy(hwnd_parent1, '000001', '100')
hwnd_parent2 = findSpecifiedTopWindow(wantedText = u'国信金太阳网上交易专业版V6.51 - [行情表-沪深Ａ股]')

