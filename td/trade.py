# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 19:06:35 2015

@author: guosen
"""
import time
import quickfix as fix
import fix_app
import logging 


#class Student(object):
#    def 


class fix_trade(object):
    def __init__(self, initfile, logger):
        self.__initfile = initfile
        self.__logger = logger
    
    def create(self):
        try:
            self.__settings = fix.SessionSettings( self.__initfile )
            self.__application = fix_app.Application()
            self.__application.setLogger(self.__logger)
            self.__factory = fix.FileStoreFactory( self.__settings )
            self.__log = fix.FileLogFactory(self.__settings)
            self.__initiator = fix.SocketInitiator( self.__application,self.__factory, self.__settings, self.__log )
            self.__initiator.start()
            
            self.__logger.debug('fix_trade create')
            time.sleep( 4 )
        except BaseException,e:
             self.__logger.error(e)
            
            
        
    def close(self):
        self.__initiator.stop()
        
    def NewStockOrder(self):
        pass;
        
    def CancleOrder(self):
        pass;