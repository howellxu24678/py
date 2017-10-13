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
        #logger.info("message:%s", message)
        msgType = fix.MsgType()
        message.getHeader().getField(msgType)
        if msgType.getValue() == fix.MsgType_Reject:
            logger.info("message:%s", message)

    def fromAdmin(self, message, sessionID):
        #logger.info("message:%s", message)
        msgType = fix.MsgType()
        message.getHeader().getField(msgType)
        if msgType.getValue() == fix.MsgType_Reject:
            logger.info("message:%s", message)

    def toApp(self, message, sessionID):
        logger.info("message:%s", message)

    def fromApp(self, message, sessionID):
        logger.info("message:%s", message)
