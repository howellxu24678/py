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
        pass

    def fromAdmin(self, message, sessionID):
        pass

    def toApp(self, message, sessionID):
        logger.info("message:%s", message)

    def fromApp(self, message, sessionID):
        logger.info("message:%s", message)
