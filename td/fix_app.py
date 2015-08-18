# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 21:35:47 2015

@author: xujhao
"""

import quickfix as fix
import logging
#import curses


class Application(fix.Application):
    orderIDs = {}
     
    def setLogger(self, logger):
        self.__logger = logger
         
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
        self.__logger.info(" onLogon: " + sessionID.__str__())
        return

    def onLogout(self, sessionID):
        self.__logger.info(" onLogout: " + sessionID.__str__())        
        #print "onLogout...", sessionID
        #print "*****************************************************************"
        #curses.beep()
        return

    def toAdmin(self, message, sessionID):
        self.__logger.info("toAdmin: " + sessionID.__str__() + " " + message.__str__())
        msgType = fix.MsgType()
        RawData = fix.RawData()
        message.getHeader().getField( msgType )
        if( msgType.getValue() == fix.MsgType_Logon ):
            #RawData="Z:110000000572:135790:"
            message.setField( fix.RawData("Z:110000000572:135790:") )
            #print "toAdmin...", sessionID, message
            
            return

    def fromAdmin(self, message, sessionID):
        #print "fromAdmin...", sessionID, message
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

            else:
                raise fix.UnsupportedMessageType()


