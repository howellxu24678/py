# -*- coding: utf-8 -*-
import logging 
import logging.config

import os
import ConfigParser
import sys
reload(sys)
sys.setdefaultencoding('utf8')

baseconfdir="conf"
loggingconf= "logging.config"
businessconf= "business.ini"


from auto.mainengine import Monitor
from auto.mainengine import Business
from PyQt4.QtCore import QCoreApplication


logging.config.fileConfig(os.path.join(os.getcwd(), baseconfdir, loggingconf))
logger = logging.getLogger("run")

class Main(object):
    def __init__(self):
        try:
            """主程序入口"""
            self._app = QCoreApplication(sys.argv)

            cf = ConfigParser.ConfigParser()
            cf.read(os.path.join(os.getcwd(), baseconfdir, businessconf))

            self._me = Business(cf)

            #sys.exit(app.exec_())
        except BaseException,e:
            logger.exception(e)

    def start(self):
        try:
            self._me.start()
            self._app.exec_()
        except BaseException,e:
            logger.exception(e)

    def stop(self):
        try:
            self._me.stop()
            self._app.quit()
        except BaseException,e:
            logger.exception(e)


def start():
    try:
        """主程序入口"""
        global app
        app = QCoreApplication(sys.argv)

        cf = ConfigParser.ConfigParser()
        cf.read(os.path.join(os.getcwd(), baseconfdir, businessconf))

        global me
        me = Business(cf)
        me.start()

        app.exec_()
    except BaseException,e:
        logger.exception(e)

def stop():
    global me
    me.stop()

    global app
    print 'app:'
    print type(app)
    app.quit()
    app.deleteLater()

if __name__ == '__main__':
    from apscheduler.schedulers.blocking import BlockingScheduler

    sched = BlockingScheduler()
    # m = Main()
    sched.add_job(start, 'cron', id='first', day_of_week ='1-5', minute = 29)
    sched.add_job(stop, 'cron', id='second', day_of_week ='1-5', minute = 32)
    sched.start()

# app = None
#
# def start():
#     try:
#         from auto.mainengine import Monitor
#         from auto.mainengine import Business
#         from PyQt4.QtCore import QCoreApplication
#         """主程序入口"""
#         global app
#         app = QCoreApplication(sys.argv)
#
#         logging.config.fileConfig(os.path.join(os.getcwd(), baseconfdir, loggingconf))
#         logger = logging.getLogger("run")
#
#         cf = ConfigParser.ConfigParser()
#         cf.read(os.path.join(os.getcwd(), baseconfdir, businessconf))
#
#         me = Business(cf)
#         me.start()
#
#         sys.exit(app.exec_())
#     except BaseException,e:
#         logger.exception(e)
#
# def stop():
#     global app
#     print 'app:'
#     print type(app)
#     app.quit()




# import os
# import ConfigParser
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')
# cf = ConfigParser.ConfigParser()
# path = r'F:\code\git\py\tdcron\conf'
# businessconf= "business.ini"
# cf.read(os.path.join(path, businessconf))
