import quickfix as fix
import logging

logger = logging.getLogger()

class Application(fix.Application):
    def setUserIDPasswd(self, userID, passwd):
        self._userID = userID
        self._passwd = passwd

    def onCreate(self, sessionID):
        logger.info("%s", sessionID)

    def onLogon(self, sessionID):
        logger.info("%s", sessionID)

    def onLogout(self, sessionID):
        logger.info("%s", sessionID)

    def toAdmin(self, message, sessionID):
        msgType = fix.MsgType()
        message.getHeader().getField(msgType)
        if msgType.getValue() == fix.MsgType_Reject:
            logger.info("message:%s", message)
        elif msgType.getValue() == fix.MsgType_Logon:
            message.getHeader().setField(fix.SenderSubID(self._userID))
            message.setField(fix.RawData(self._passwd))
        logger.info("message:%s", message)

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
