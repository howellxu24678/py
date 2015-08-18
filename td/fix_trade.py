# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 19:06:35 2015

@author: guosen
"""
import time
import quickfix as fix
import fix_app


class fix_trade:
    def __int__(self, initfile):
        self.__initfile = initfile
    
    def create(self):
        settings = fix.SessionSettings( self.__initfile )
        application = fix_app.Application()
        factory = fix.FileStoreFactory( "store" )
        log = fix.FileLogFactory("log")
        self.__initiator = fix.SocketInitiator( application,factory, settings ,log )
        self.__initiator.start()
        time.sleep( 4 )
        
    def close(self):
        self.__initiator.stop()
        
    def NewStockOrder(self):
        pass;
        
    def CancleOrder(self):
        pass;