# -*- coding: utf-8 -*-
import logging
import logging.config


import os
import ConfigParser
import sys
from auto.util import *
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



def monitor():
    try:
        from apscheduler.schedulers.qt import QtScheduler
        from apscheduler.triggers.cron import CronTrigger
        app = QCoreApplication(sys.argv)
        global me
        me = Monitor(cf)
        sched = QtScheduler()

        schedtime = [y.split(':') for x in cf.get('monitor', 'schedtime').strip().split('|') for y in x.split(',')]
        trigger_start = CronTrigger(day_of_week=schedtime[0][0], hour=int(schedtime[1][0]), minute=int(schedtime[1][1]))
        logger.info('schedulers:start dayofweek:%s startime:%s ', schedtime[0][0], schedtime[1])
        trigger_stop = CronTrigger(day_of_week=schedtime[2][0], hour=int(schedtime[3][0]), minute=int(schedtime[3][1]))
        logger.info('schedulers:stop dayofweek:%s stoptime:%s', schedtime[2][0], schedtime[3])
        sched.add_job(start, trigger_start)
        sched.add_job(stop, trigger_stop)
        sched.start()

        working_time_range = parse_work_time(cf.get("monitor", "workingtime"))
        #上面的任务调度只有在未来时间才会触发
        #这里加上判断当前时间如果在工作时间(时间段和交易日都要符合)，则要开启
        if is_trade_day(cf) and is_working_time(working_time_range):
            start()

        app.exec_()
    except BaseException,e:
        logger.exception(e)


def test():
    try:
        from apscheduler.schedulers.qt import QtScheduler
        app = QCoreApplication(sys.argv)
        global me
        me = Monitor(cf)
        sched = QtScheduler()
        # m = Main()
        # sched.add_job(start, 'cron', id='first', day_of_week ='0-4', hour = 9, minute = 11)
        # sched.add_job(stop, 'cron', id='second', day_of_week ='0-4', hour = 15, minute = 20)
        sched.add_job(start, 'cron', id='first',  hour = 17, minute = 21,second = 0)
        sched.add_job(stop, 'cron', id='second',  hour = 21, minute = 10)
        sched.start()
        app.exec_()
    except BaseException,e:
        logger.exception(e)


def runow():
    try:
        app = QCoreApplication(sys.argv)
        me = Monitor(cf)
        me.start()
        sys.exit(app.exec_())
    except BaseException, e:
        logger.exception(e)

if __name__ == '__main__':
    monitor()
