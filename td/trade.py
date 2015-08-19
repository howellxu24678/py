# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 19:06:35 2015

@author: guosen
"""
import time
import datetime

import quickfix as fix
import fix_app
#import logging
import ConfigParser 



#class Student(object):
#    def 


class fix_trade(object):
    def __init__(self, initfile, logger):
        self.__initfile = initfile
        self.__logger = logger
        

    def GetConfig(self):
        cf = ConfigParser.ConfigParser()
        cf.read(self.__initfile)
        self.__clordid_prefix = cf.get("DEFAULT", "clordid_prefix")
        self.__UserName = cf.get("SESSION", "UserName")
        self.__PassWord = cf.get("SESSION", "Password")
        self.__SenderCompID = cf.get("SESSION", "SenderCompID")
        self.__TargetCompID = cf.get("SESSION", "TargetCompID")
        self.__AccountType = cf.get("SESSION", "AccountType")
        self.__RawData = self.__AccountType + ":" + self.__UserName + ":" + self.__PassWord
        
        self.__logger.info('__UserName:' + self.__UserName + \
            " __SenderCompID:" + self.__SenderCompID + \
            " __TargetCompID:" + self.__TargetCompID + \
            "__clordid_prefix:" + self.__clordid_prefix + \
            "__AccountType:" + self.__AccountType)
            
    def create(self):
        try:
            self.GetConfig()
            
            self.__settings = fix.SessionSettings( self.__initfile )
            self.__application = fix_app.Application()
            self.__application.setParm(self.__logger,  self.__RawData)
            self.__factory = fix.FileStoreFactory( self.__settings )
            self.__log = fix.FileLogFactory(self.__settings)
            self.__initiator = fix.SocketInitiator( self.__application,self.__factory, self.__settings, self.__log )
            self.__initiator.start()
#            self.__settings = fix.SessionSettings( self.__initfile )
#            self.__application = fix_app.apptest(self.__logger)
#            self.__factory = fix.FileStoreFactory( self.__settings )
#            self.__log = fix.FileLogFactory(self.__settings)
#            self.__initiator = fix.SocketInitiator( self.__application,self.__factory, self.__settings, self.__log )
#            self.__initiator.start()
            
            self.__logger.debug('fix_trade create')
            time.sleep( 4 )
        except BaseException,e:
             self.__logger.error(e)
            
    def genOrderID(self):
        return self.__clordid_prefix + time.strftime("%H%M%S",time.localtime()) + str(datetime.datetime.now().microsecond/1000)    
        
    def close(self):
        self.__initiator.stop()
        
    def NewStockOrder(self):
        msg = fix.Message()
        msg.getHeader().setField(fix.MsgType(fix.MsgType_NewOrderSingle))
        #msg.setField(fix.m)
        
    def CancleOrder(self):
        pass