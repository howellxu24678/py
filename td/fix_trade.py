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
        try:
            self.__settings = fix.SessionSettings( self.__initfile )
            self.__application = fix_app.Application()
            self.__factory = fix.FileStoreFactory( self.__settings )
            self.__log = fix.FileLogFactory(self.__settings)
            self.__initiator = fix.SocketInitiator( self.__application,self.__factory, self.__settings ,self.__log )
            self.__initiator.start()
            time.sleep( 4 )
        except e:
            self.__log.
            
        
    def close(self):
        self.__initiator.stop()
        
    def NewStockOrder(self):
        pass;
        
    def CancleOrder(self):
        pass;