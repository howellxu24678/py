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
        #如有显式配置调度时间，则根据调度时间来设置调度计划
        #如果没有配置，则分别取工作时间的最前和最后时间作为任务计划的开始和结束时间
        if cf.has_option('monitor','schedtime'):
            schedtime = cf.get('monitor', 'schedtime').strip().split('~')
            startime = schedtime[0].split(':')
            stoptime = schedtime[1].split(':')

        else:
            workingtimelist = [y for x in cf.get('monitor', 'workingtime').strip().split(',')
                               for y in x.strip().split('~')]
            startime = workingtimelist[0].split(':')
            stoptime = workingtimelist[-1].split(':')

        dayofweek = cf.get('monitor', 'dayofweek').strip()
        trigger_start = CronTrigger(day_of_week=dayofweek, hour=int(startime[0]), minute=int(startime[1]))
        trigger_stop = CronTrigger(day_of_week=dayofweek, hour=int(stoptime[0]), minute=int(stoptime[1]))
        #sched.add_job(start, 'cron', id='first', day_of_week='0-4', hour=int(startime[0]), minute=int(startime[1]))
        #sched.add_job(stop, 'cron', id='second', day_of_week='0-4', hour=int(stoptime[0]), minute=int(stoptime[1]))
        logger.info('schedulers dayofweek:%s startime:%s stoptime:%s', dayofweek, startime, stoptime)
        sched.add_job(start, trigger_start)
        sched.add_job(stop, trigger_stop)
        sched.start()

        #上面的任务调度只有在未来时间才会触发
        #这里加上判断当前时间如果在工作时间(时间段和交易日都要符合)，则要开启
        worktimerange = [x.split('~') for x in cf.get("monitor", "workingtime").split(',')]

        time_now = datetime.datetime.now().strftime("%H:%M")
        for x in worktimerange:
            if time_now > x[0] and time_now < x[1]:
                logger.info('now:%s is in the worktimerange:%s,will start the job immediately', time_now, x)
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
