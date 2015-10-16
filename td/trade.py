# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 19:06:35 2015

@author: guosen
"""
import time
import datetime

import quickfix as fix
import fix_app
import ConfigParser 

import logging
logger = logging.getLogger()

from winguiauto import *

class trade(object):
    def __init__(self, initfile):
        self._initfile = initfile;
    
    def buy(self, stock_code, stock_number, stock_price):
        pass
        
    def sell(self, stock_code, stock_number, stock_price):
        pass
        
class gui_trade(trade):
    def __init__(self):
        self._hwnd_parent = findSpecifiedTopWindow(wantedText = u'网上股票交易系统5.0')
        if self._hwnd_parent == 0:
            logger.critical(u'华泰交易软件没有运行！')
            raise RuntimeError, 'gui_trade init failed'
        else:
            logger.info('gui_trade init success')

    
    def buy(self, stock_code, stock_number, stock_price):
        try:
            pressKey(self._hwnd_parent, win32con.VK_F6)
            hwndControls = findWantedControls(self._hwnd_parent)
            if closePopupWindow(self._hwnd_parent, wantedClass='Button'):
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
            return not closePopupWindow(self._hwnd_parent, wantedClass='Button')
        except BaseException,e:
            logger.exception(e)
        
    def sell(self, stock_code, stock_number, stock_price):
        try:
            pressKey(self._hwnd_parent, win32con.VK_F6)
            hwndControls = findWantedControls(self._hwnd_parent)
            if closePopupWindow(self._hwnd_parent, wantedClass='Button'):
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
            return not closePopupWindow(self._hwnd_parent, wantedClass='Button')
        except BaseException,e:
            logger.exception(e)
    

        
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
    
    def buy(self, stock_code, stock_number, stock_price):
        pass
        
    def sell(self, stock_code, stock_number, stock_price):
        pass