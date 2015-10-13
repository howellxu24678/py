# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 21:35:47 2015

@author: xujhao
"""

import quickfix as fix
import logging
import quickfix42
#import curses
logger = logging.getLogger()

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
     
    def setParm(self, RawData):
        self.__RawData = RawData
         
    def reset( self ):
        self.orderIDs = {}

    def onCreate(self, sessionID):
        self.reset()
        session = fix.Session.lookupSession( sessionID )
        if session == None:
            session.reset()
        #logger.info(sessionID + "onCreate")

    def onLogon(self, sessionID):
        #print "*****************************************************************"
        #print "onLogon...", sessionID
        logger.info("onLogon: " + sessionID.__str__())
        return

    def onLogout(self, sessionID):
        logger.info("onLogout: " + sessionID.__str__())        
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
        logger.info("toAdmin:" + message.__str__())

    def fromAdmin(self, message, sessionID):
        #print "fromAdmin...", sessionID, message
        msgType = fix.MsgType()        
        message.getHeader().getField( msgType )
        if(msgType.getValue() == fix.MsgType_Heartbeat):
            return 
            
        logger.info("fromAdmin:" + message.__str__())
        return

    def toApp(self, message, sessionID):
        #print "toApp...", sessionID, message
        logger.info("toApp:" + message.__str__())
        return

    def OnNoPositions(self, message):
        logger.info("OnNoPositions")
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
        logger.info( "NoPos:" + NoPos.getString() + symbol.getString() + "." + exch.getString())                
        for i in range(NoPos.getValue()):
            message.getGroup(i+1,groupRead)
            groupRead.getFieldIfSet(PosType)
            groupRead.getFieldIfSet(LongQty)
            groupRead.getFieldIfSet(ShortQty)
            if(PosType.getString() == "SB"):
                logger.info("股份余额:" + LongQty.getString())
            elif (PosType.getString() == "SAV"):
                logger.info("股份可用余额:" + LongQty.getString())
            elif (PosType.getString() == "SQ"):
                logger.info("当前拥股数:" + LongQty.getString())
            elif (PosType.getString() == "LB"):
                logger.info("昨日余额:" + LongQty.getString())
            elif (PosType.getString() == "SBQ"):
                logger.info("今日买入数量:" + LongQty.getString())
            elif (PosType.getString() == "SS"):
                logger.info("卖出冻结数:" + ShortQty.getString())
            elif (PosType.getString() == "SF"):
                logger.info("人工冻结数:" + ShortQty.getString())
                
            #logger.info("PosType:" +  PosType.getString() + " LongQty:" + LongQty.getString())
           
    def OnNoPosAmt(self, message):
        logger.info("OnNoPositions")
        groupRead = UapGroup.NoPosAmtCus()
        PosAmtType = fix.PosAmtType()
        PosAmt = fix.PosAmt()

                
        NoPos = fix.NoPosAmt()
        message.getField(NoPos)
        logger.info( "NoPos:" + NoPos.getString())                
        for i in range(NoPos.getValue()):
            message.getGroup(i+1,groupRead)
            groupRead.getFieldIfSet(PosAmtType)
            groupRead.getFieldIfSet(PosAmt)
            if(PosAmtType.getString() == "FB"):
                logger.info("资金余额:" + PosAmt.getString())
            elif (PosAmtType.getString() == "FAV"):
                logger.info("资金可用余额:" + PosAmt.getString())
            elif (PosAmtType.getString() == "MV"):
                logger.info("资产总值:" + PosAmt.getString())
            elif (PosAmtType.getString() == "F"):
                logger.info("资金资产:" + PosAmt.getString())
            elif (PosAmtType.getString() == "SV"):
                logger.info("市值:" + PosAmt.getString())
            elif (PosAmtType.getString() == "FBF"):
                logger.info("资金买入冻结:" + PosAmt.getString())       
    
    def fromApp(self, message, sessionID):
        logger.info("fromApp:" + message.__str__())
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
            logger.info( "PosReqType.getValue():" + PosReqType.getString())
            if(PosReqType.getValue() == 0):
                self.OnNoPositions(message)
            elif (PosReqType.getValue() == 9):
                self.OnNoPosAmt(message)

                    
#            elif(PosReqType.getValue() == 9):
#                pass
            #else:
                #raise fix.UnsupportedMessageType()


