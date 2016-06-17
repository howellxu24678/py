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


from auto.mainengine import Business
from PyQt4.QtCore import QCoreApplication


logging.config.fileConfig(os.path.join(os.getcwd(), baseconfdir, loggingconf))
logger = logging.getLogger("run")


def start():
    try:
        """主程序入口"""
        logger.info('start')
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
    try:
        logger.info('stop')
        global me
        me.stop()

        global app
        app.quit()
        app.deleteLater()
    except BaseException,e:
        logger.exception(e)

if __name__ == '__main__':
    from apscheduler.schedulers.blocking import BlockingScheduler

    sched = BlockingScheduler()
    # m = Main()
    sched.add_job(start, 'cron', id='first', day_of_week ='1-5', hour = 9, minute = 10)
    sched.add_job(stop, 'cron', id='second', day_of_week ='1-5', hour = 15, minute = 10)
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

# class Main(object):
#     def __init__(self):
#         try:
#             """主程序入口"""
#             self._app = QCoreApplication(sys.argv)
#
#             cf = ConfigParser.ConfigParser()
#             cf.read(os.path.join(os.getcwd(), baseconfdir, businessconf))
#
#             self._me = Business(cf)
#
#             #sys.exit(app.exec_())
#         except BaseException,e:
#             logger.exception(e)
#
#     def start(self):
#         try:
#             self._me.start()
#             self._app.exec_()
#         except BaseException,e:
#             logger.exception(e)
#
#     def stop(self):
#         try:
#             self._me.stop()
#             self._app.quit()
#         except BaseException,e:
#             logger.exception(e)


# import os
# import ConfigParser
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')
# cf = ConfigParser.ConfigParser()
# path = r'F:\code\git\py\tdcron\conf'
# businessconf= "business.ini"
# cf.read(os.path.join(path, businessconf))
