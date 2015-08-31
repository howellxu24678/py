# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 21:35:47 2015

@author: xujhao
"""

import quickfix as fix
#import logging
import quickfix42
#import curses


class UapGroup(quickfix42.Message):
    def __init__(self):
        quickfix42.Message.__init__(self)
        self.getHeader().setField( fix.MsgType("UAP"))

    class NoPositions(fix.Group):
        def __init__(self):
            order = fix.IntArray(4)
            order[0] = 703
            order[1] = 704
            order[2] = 705
            order[3] = 0
            fix.Group.__init__(self, 702, 703, order)
            
    class NoPosAmtCus(fix.Group):
        def __init__(self):
            order = fix.IntArray(3)
            order[0] = 707
            order[1] = 708
            order[2] = 0
            fix.Group.__init__(self, 753, 707, order)
            

class Application(fix.Application):
    orderIDs = {}
     
    def setParm(self, logger, RawData):
        self.__logger = logger
        self.__RawData = RawData
         
    def reset( self ):
        self.orderIDs = {}

    def onCreate(self, sessionID):
        self.reset()
        session = fix.Session.lookupSession( sessionID )
        if session == None:
            session.reset()
        #self.__logger.info(sessionID + "onCreate")

    def onLogon(self, sessionID):
        #print "*****************************************************************"
        #print "onLogon...", sessionID
        self.__logger.info("onLogon: " + sessionID.__str__())
        return

    def onLogout(self, sessionID):
        self.__logger.info("onLogout: " + sessionID.__str__())        
        #print "onLogout...", sessionID
        #print "*****************************************************************"
        #curses.beep()
        return

    def toAdmin(self, message, sessionID):
        
        msgType = fix.MsgType()
        #RawData = fix.RawData()
        
        message.getHeader().getField( msgType )
        if(msgType.getValue() == fix.MsgType_Heartbeat):
            return 
        elif( msgType.getValue() == fix.MsgType_Logon ):
            #RawData="Z:110000000572:135790:"
            message.setField( fix.RawData(self.__RawData) )
            #print "toAdmin...", sessionID, message
        self.__logger.info("toAdmin:" + message.__str__())

    def fromAdmin(self, message, sessionID):
        #print "fromAdmin...", sessionID, message
        msgType = fix.MsgType()        
        message.getHeader().getField( msgType )
        if(msgType.getValue() == fix.MsgType_Heartbeat):
            return 
            
        self.__logger.info("fromAdmin:" + message.__str__())
        return

    def toApp(self, message, sessionID):
        #print "toApp...", sessionID, message
        self.__logger.info("toApp:" + message.__str__())
        return

    def OnNoPositions(self, message):
        self.__logger.info("OnNoPositions")
        symbol = fix.Symbol()
        exch = fix.SecurityExchange()
        message.getField(symbol)
        message.getField(exch)
        groupRead = UapGroup.NoPositions()
        PosType = fix.PosType()
        LongQty = fix.LongQty()
        ShortQty = fix.ShortQty()
                
                
        NoPos = fix.UapGroup()
        message.getField(NoPos)
        self.__logger.info( "NoPos:" + NoPos.getString() + symbol.getString() + "." + exch.getString())                
        for i in range(NoPos.getValue()):
            message.getGroup(i+1,groupRead)
            groupRead.getFieldIfSet(PosType)
            groupRead.getFieldIfSet(LongQty)
            groupRead.getFieldIfSet(ShortQty)
            if(PosType.getString() == "SB"):
                self.__logger.info("股份余额:" + LongQty.getString())
            elif (PosType.getString() == "SAV"):
                self.__logger.info("股份可用余额:" + LongQty.getString())
            elif (PosType.getString() == "SQ"):
                self.__logger.info("当前拥股数:" + LongQty.getString())
            elif (PosType.getString() == "LB"):
                self.__logger.info("昨日余额:" + LongQty.getString())
            elif (PosType.getString() == "SBQ"):
                self.__logger.info("今日买入数量:" + LongQty.getString())
            elif (PosType.getString() == "SS"):
                self.__logger.info("卖出冻结数:" + ShortQty.getString())
            elif (PosType.getString() == "SF"):
                self.__logger.info("人工冻结数:" + ShortQty.getString())
                
            #self.__logger.info("PosType:" +  PosType.getString() + " LongQty:" + LongQty.getString())
           
    def OnNoPosAmt(self, message):
        self.__logger.info("OnNoPositions")
        groupRead = UapGroup.NoPosAmtCus()
        PosAmtType = fix.PosAmtType()
        PosAmt = fix.PosAmt()

                
        NoPos = fix.NoPosAmt()
        message.getField(NoPos)
        self.__logger.info( "NoPos:" + NoPos.getString())                
        for i in range(NoPos.getValue()):
            message.getGroup(i+1,groupRead)
            groupRead.getFieldIfSet(PosAmtType)
            groupRead.getFieldIfSet(PosAmt)
            if(PosAmtType.getString() == "FB"):
                self.__logger.info("资金余额:" + PosAmt.getString())
            elif (PosAmtType.getString() == "FAV"):
                self.__logger.info("资金可用余额:" + PosAmt.getString())
            elif (PosAmtType.getString() == "MV"):
                self.__logger.info("资产总值:" + PosAmt.getString())
            elif (PosAmtType.getString() == "F"):
                self.__logger.info("资金资产:" + PosAmt.getString())
            elif (PosAmtType.getString() == "SV"):
                self.__logger.info("市值:" + PosAmt.getString())
            elif (PosAmtType.getString() == "FBF"):
                self.__logger.info("资金买入冻结:" + PosAmt.getString())       
    
    def fromApp(self, message, sessionID):
        self.__logger.info("fromApp:" + message.__str__())
        #print "fromApp...", sessionID, message
        msgType = fix.MsgType()
        clOrdID = fix.ClOrdID()
        orderStatus=fix.OrdStatus()
        message.getHeader().getField( msgType )
        if( msgType.getValue() == fix.MsgType_ExecutionReport ):
            echo = fix.Message( message )
            message.getField( orderStatus )
            if(orderStatus.getString()=="8"):
                print "reject"
            elif(orderStatus.getString()=="0"):
                print "new"
                
        elif (msgType.getValue() ==  "UAP"):
            PosReqType = fix.PosReqType()
            message.getField(PosReqType)
            self.__logger.info( "PosReqType.getValue():" + PosReqType.getString())
            if(PosReqType.getValue() == 0):
                self.OnNoPositions(message)
            elif (PosReqType.getValue() == 9):
                self.OnNoPosAmt(message)

                    
#            elif(PosReqType.getValue() == 9):
#                pass
            #else:
                #raise fix.UnsupportedMessageType()


