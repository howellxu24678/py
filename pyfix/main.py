import os
import quickfix as fix
import quickfix42 as fix42
import application
import logging.config
import ConfigParser

baseconfdir = "config"
loggingconf = "logging.config"
fixConf = "Fix.cfg"

print "getcwd:" + os.getcwd()

logging.config.fileConfig(os.path.join(os.getcwd(), baseconfdir, loggingconf))
logger = logging.getLogger("run")
cf = ConfigParser.ConfigParser()
cf.read(os.path.join(os.getcwd(), baseconfdir, fixConf))

class Test(object):
    def __init__(self, cf):
        self._session = fix.SessionID(cf.get("SESSION", "BeginString"),
                                      cf.get("SESSION", "SenderCompID"),
                                      cf.get("SESSION", "TargetCompID"))

    def marketDataRequest(self):
        msg = fix42.MarketDataRequest()
        msg.setField(fix.MDReqID("1234"))
        msg.setField(fix.SubscriptionRequestType(fix.SubscriptionRequestType_SNAPSHOT_PLUS_UPDATES))
        msg.setField(fix.MarketDepth(0))

        group1 = fix42.MarketDataRequest().NoMDEntryTypes()
        group1.setField(fix.MDEntryType(fix.MDEntryType_BID))
        msg.addGroup(group1)

        group2 = fix42.MarketDataRequest().NoRelatedSym()
        group2.setField(fix.Symbol('au1711'))
        msg.addGroup(group2)
        group2.setField(fix.Symbol('au1712'))
        msg.addGroup(group2)

        msg.getHeader().setField(fix.OnBehalfOfCompID("BLP1"))
        msg.setField(fix.Account("FUT_ACCT"))
        fix.Session.sendToTarget(msg, self._session)


settings = fix.SessionSettings(os.path.join(os.getcwd(), baseconfdir, fixConf))
application = application.Application()
factory = fix.FileStoreFactory("log")
log = fix.FileLogFactory("log")
acpt = fix.SocketAcceptorBase(application, factory, settings, log)

acpt.start()
test = Test(cf)
#time.sleep(4)

#Msg = fix.Message()
#Msg.setString(
#    "8=FIX.4.29=18235=D34=1549=FIXTest12952=20141110-00:53:51.63856=SERVER11=Mon Nov 10 2014 08:53:51 GMT+080021=138=10040=244=39.1254=155=60044660=20140616-07:35:03.69610=251",
#    0)

#sessionID = fix.SessionID("FIX.4.2", "FIXTest129", "SERVER")

# print(sessionID)

#fix.Session.sendToTarget(Msg, sessionID)
# fix.Session.sendToTarget( Msg)

ch = 0
while 1:
    ch = input("your choice:")
    if ch == 1:
        test.marketDataRequest()
acpt.stop()
