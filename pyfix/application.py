import quickfix as fix
import logging

logger = logging.getLogger("run")

class Application(fix.Application):
    def onCreate(self, sessionID):
        logger.info("%s", sessionID)

    def onLogon(self, sessionID):
        logger.info("%s", sessionID)

    def onLogout(self, sessionID):
        logger.info("%s", sessionID)

    def toAdmin(self, message, sessionID):
        logger.info("message:%s", message)
        msgType = fix.MsgType()
        message.getHeader().getField(msgType)
        if msgType.getValue() == fix.MsgType_Reject:
            logger.info("message:%s", message)
        elif msgType.getValue() == fix.MsgType_Logon:
            logger.info("logon msg will add rawdata")
            message.setField(fix.RawData("testrawdata"))

    def fromAdmin(self, message, sessionID):
        logger.info("message:%s", message)
        # msgType = fix.MsgType()
        # message.getHeader().getField(msgType)
        # if msgType.getValue() == fix.MsgType_Reject:
        #     logger.info("message:%s", message)

    def toApp(self, message, sessionID):
        logger.info("message:%s", message)

    def fromApp(self, message, sessionID):
        logger.info("message:%s", message)
