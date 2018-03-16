import os
import quickfix as fix
import quickfix42 as fix42
import application
import logging.config
import ConfigParser
import datetime as dt

class Test(object):
    def __init__(self, cf, cf_path):
        self._cf = cf
        self._cf_path = cf_path

        fix_cf = ConfigParser.ConfigParser()
        fix_cf.read(os.path.join(os.getcwd(), baseconfdir, cf.get("main", "fix_cfg_file")))
        self._session = fix.SessionID(fix_cf.get("SESSION", "BeginString"),
                                      fix_cf.get("SESSION", "SenderCompID"),
                                      fix_cf.get("SESSION", "TargetCompID"))

        self._order_section = 'order'
        self._market_section = 'market'
        #self._clordid_tag = '11'
        #self._clordid_value = self._cf.getint(self._order_section, self._clordid_tag)


    def marketDataRequest(self):
        self._cf.read(self._cf_path)

        msg = fix42.Message()
        for name, value in self._cf.items(self._market_section):
            if name == '35' or name == '115':
                msg.getHeader().setField(fix.StringField(int(name), value))
            elif name.isdigit():
                msg.setField(fix.StringField(int(name), value))
            elif name == 'entrytypes':
                type_group = fix42.MarketDataRequest().NoMDEntryTypes()
                for entry in value.split(';'):
                    type_group.setField(fix.MDEntryType(entry))
                    msg.addGroup(type_group)
            elif name == 'symbols':
                sym_group = fix42.MarketDataRequest().NoRelatedSym()
                for sym in value.split(';'):
                    sym_group.setField(fix.Symbol(sym))
                    msg.addGroup(sym_group)

        fix.Session.sendToTarget(msg, self._session)


    def orderRequest(self):
        self._cf.read(self._cf_path)

        msg = fix42.Message()
        for name, value in self._cf.items(self._order_section):
            if name == '35' or name == '115':
                msg.getHeader().setField(fix.StringField(int(name), value))
            else:
                msg.setField(fix.StringField(int(name), value))
        #now = dt.datetime.utcnow()
        #now.strftime("%Y%m%d-%H:%M:%S")
        #msg.setField(fix.StringField(11, str(self._clordid_value)))
        # self._clordid_value += 1
        # self._cf.set(self._order_section, self._clordid_tag, str(self._clordid_value))
        # with open(self._cf_path, 'w') as fw:
        #     self._cf.write(fw)
        msg.setField(fix.StringField(60, dt.datetime.utcnow().strftime("%Y%m%d-%H:%M:%S")))

        fix.Session.sendToTarget(msg, self._session)


baseconfdir = "config"
loggingconf = "logging.config"
globalConf = "pyfix.ini"
ch_count = 40


def tips():
    print('')
    print("{}".format("-" * ch_count))
    print("1:order")
    print("2:marketdata")
    print('q:quit')
    print("{}".format("-" * ch_count))
    print('')

#print "getcwd:" + os.getcwd()

logging.config.fileConfig(os.path.join(os.getcwd(), baseconfdir, loggingconf))
logger = logging.getLogger()
cf = ConfigParser.ConfigParser()
cf_path = os.path.join(os.getcwd(), baseconfdir, globalConf)
cf.read(cf_path)
settings = fix.SessionSettings(os.path.join(os.getcwd(), baseconfdir, cf.get("main", "fix_cfg_file")))

application = application.Application()
application.setUserIDPasswd(cf.get("main", "userID"), cf.get("main", "password"))
factory = fix.FileStoreFactory("log")
log = fix.FileLogFactory("log")
# acpt = fix.SocketAcceptorBase(application, factory, settings, log)
# acpt.start()
init = fix.SocketInitiatorBase(application, factory, settings, log)
init.start()
test = Test(cf, cf_path)



ch = 0
while 1:
    tips()
    try:
        ch = raw_input(u"your choice:\n\n")
        if ch == '1':
            test.orderRequest()
        elif ch == '2':
            test.marketDataRequest()
        elif ch == 'q':
            os._exit(0)
    except BaseException,e:
        print e

        #test.marketDataRequest()
init.stop()
