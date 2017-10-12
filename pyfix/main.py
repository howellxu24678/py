import os
import time
import quickfix as fix
import application
import logging.config

baseconfdir = "config"
loggingconf = "logging.config"
fixConf = "Fix.cfg"

print "getcwd:" + os.getcwd()

logging.config.fileConfig(os.path.join(os.getcwd(), baseconfdir, loggingconf))
logger = logging.getLogger("run")


settings = fix.SessionSettings(os.path.join(os.getcwd(), baseconfdir, fixConf))
application = application.Application()
factory = fix.FileStoreFactory("log")
log = fix.FileLogFactory("log")
acpt = fix.SocketAcceptorBase(application, factory, settings, log)

acpt.start()
time.sleep(4)

#Msg = fix.Message()
#Msg.setString(
#    "8=FIX.4.29=18235=D34=1549=FIXTest12952=20141110-00:53:51.63856=SERVER11=Mon Nov 10 2014 08:53:51 GMT+080021=138=10040=244=39.1254=155=60044660=20140616-07:35:03.69610=251",
#    0)

#sessionID = fix.SessionID("FIX.4.2", "FIXTest129", "SERVER")

# print(sessionID)

#fix.Session.sendToTarget(Msg, sessionID)
# fix.Session.sendToTarget( Msg)

logger.info("hello fix")

while 1:
    time.sleep(1)
acpt.stop()
