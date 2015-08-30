# -*- coding: utf-8 -*-

baseconfdir="./conf"
loggingconfpath= baseconfdir + "/logging.config"
quickfixconfpath= baseconfdir + "/quickfix.ini"

#import sys
#import time
#import quickfix as fix
#import fix_app
#
#
#
#settings = fix.SessionSettings( quickfixconfpath )
#application = fix_app.Application()
#factory = fix.FileStoreFactory( settings )
#log = fix.FileLogFactory(settings)
#initiator = fix.SocketInitiator( application,factory, settings ,log )
#
#sessionID = fix.SessionID( "FIX.4.2","FIXTest129" ,"SERVER")
#dic = settings.get(sessionID)
#
#initiator.start()
#time.sleep( 4 )
#
#Msg=fix.Message()
#Msg.setString("8=FIX.4.29=18235=D34=1549=FIXTest12952=20141110-00:53:51.63856=SERVER11=Mon Nov 10 2014 08:53:51 GMT+080021=138=10040=244=39.1254=155=60044660=20140616-07:35:03.69610=251",0)
#	
#
#
#print(sessionID)
#
#fix.Session.sendToTarget( Msg,sessionID)
##fix.Session.sendToTarget( Msg)
#
#while 1:
#	time.sleep( 1 )
#initiator.stop()






import logging 
import logging.config
import trade

#import quickfix as fix
#import fix_app

logging.config.fileConfig(loggingconfpath)
logger = logging.getLogger("example01")

#settings = fix.SessionSettings( quickfixconfpath )
#application = fix_app.Application()
#application.setLogger(logger)
#factory = fix.FileStoreFactory(settings )
#log = fix.FileLogFactory(settings)
#initiator = fix.SocketInitiator( application,factory, settings, log )
#initiator.start()

trader = trade.fix_trade(quickfixconfpath, logger)
trader.create()
#trader.NewStockOrder()

trader.UAN(9)

