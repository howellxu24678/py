# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 21:35:47 2015

@author: xujhao
"""

import quickfix as fix
#import logging
import quickfix42
#import curses


class apptest(fix.Application):
    def __init__(self, logger):
        self.__logger = logger
        
    def onCreate(self, sessionID):
        #self.__logger.info(sessionID + "onCreate")
        return

    def onLogon(self, sessionID):
        return

    def onLogout(self, sessionID):
        return

    def toAdmin(self, message, sessionID):
        return

    def fromAdmin(self, message, sessionID):
        return

    def toApp(self, message, sessionID):
        return

    def fromApp(self, message, sessionID):
        return

class NoUap(quickfix42.Message):
	def __init__(self):
		quickfix42.Message.__init__(self)
		self.getHeader().setField( fix.MsgType("UAP"))
  
	class NoCustom(fix.Group):
		def __init__(self):
			order = fix.IntArray(4)
			order[0] = 703
			order[1] = 704
			order[2] = 705
			order[3] = 0
			fix.Group.__init__(self, 702, 703, order)

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
        self.__logger.info("toAdmin: " + sessionID.__str__() + " " + message.__str__())

    def fromAdmin(self, message, sessionID):
        #print "fromAdmin...", sessionID, message
        msgType = fix.MsgType()        
        message.getHeader().getField( msgType )
        if(msgType.getValue() == fix.MsgType_Heartbeat):
            return 
            
        self.__logger.info("fromAdmin: " + sessionID.__str__() + " " + message.__str__())
        return

    def toApp(self, message, sessionID):
        #print "toApp...", sessionID, message
        self.__logger.info("toApp: " + sessionID.__str__() + " " + message.__str__())
        return

    def fromApp(self, message, sessionID):
        self.__logger.info("fromApp: " + sessionID.__str__() + " " + message.__str__())
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
                symbol = fix.Symbol()
                exch = fix.SecurityExchange()
                message.getField(symbol)
                message.getField(exch)
                groupRead = NoUap.NoCustom()
                PosType = fix.PosType()
                LongQty = fix.LongQty()
                ShortQty = fix.ShortQty()
                
                
                NoPos = fix.NoPositions()
                message.getField(NoPos)
                self.__logger.info( "NoPos:" + NoPos.getString() + "symbol:" + symbol.getString() + "exch:" + exch.getString())                
                for i in range(NoPos.getValue()):
                    message.getGroup(i+1,groupRead)
                    groupRead.getFieldIfSet(PosType)
                    groupRead.getFieldIfSet(LongQty)
                    groupRead.getFieldIfSet(ShortQty)
                    self.__logger.info("PosType:" +  PosType.getString() + " LongQty:" + LongQty.getString())

                    
#            elif(PosReqType.getValue() == 9):
#                pass
            #else:
                #raise fix.UnsupportedMessageType()


