# -*- coding: utf-8 -*-
# import logging
# import logging.config
#
# import os
# import ConfigParser
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')
#
# baseconfdir="conf"
# loggingconf= "logging.config"
# businessconf= "business.ini"
#
# def main():
#     try:
#         from auto.mainengine import Monitor
#         from auto.mainengine import BatchOrder
#         from PyQt4.QtCore import QCoreApplication
#         """主程序入口"""
#         app = QCoreApplication(sys.argv)
#
#         logging.config.fileConfig(os.path.join(os.getcwd(), baseconfdir, loggingconf))
#         logger = logging.getLogger("run")
#
#         cf = ConfigParser.ConfigParser()
#         cf.read(os.path.join(os.getcwd(), baseconfdir, businessconf))
#
#         me = Monitor(cf)
#         #bo = BatchOrder(cf)
#
#         sys.exit(app.exec_())
#     except BaseException,e:
#         logger.exception(e)
#
#
# if __name__ == '__main__':
#     main()

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
from PyQt4.QtCore import QCoreApplication


logging.config.fileConfig(os.path.join(os.getcwd(), baseconfdir, loggingconf))
logger = logging.getLogger("run")

cf = ConfigParser.ConfigParser()
cf.read(os.path.join(os.getcwd(), baseconfdir, businessconf))


def start():
    try:
        """主程序入口"""
        logger.info('start')

        global me
        me.start()

    except BaseException,e:
        logger.exception(e)

def stop():
    try:
        logger.info('stop')

        global me
        me.stop()

    except BaseException,e:
        logger.exception(e)


if __name__ == '__main__':
    try:
        from apscheduler.schedulers.qt import QtScheduler
        app = QCoreApplication(sys.argv)
        global me
        me = Monitor(cf)
        sched = QtScheduler()
        # m = Main()
        # sched.add_job(start, 'cron', id='first', day_of_week ='0-4', hour = 9, minute = 11)
        # sched.add_job(stop, 'cron', id='second', day_of_week ='0-4', hour = 15, minute = 20)
    #    sched.add_job(start, 'cron', id='first',  hour = 9, minute = 16)
    #    sched.add_job(stop, 'cron', id='second',  hour = 15, minute = 10)
        sched.add_job(start, 'cron', id='first', second = 10)
        sched.add_job(stop, 'cron', id='second', second = 50)
        sched.start()
        app.exec_()
    except BaseException,e:
        logger.exception(e)