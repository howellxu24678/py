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

app = None

def start():
    try:
        from auto.mainengine import Monitor
        from auto.mainengine import Business
        from PyQt4.QtCore import QCoreApplication
        """主程序入口"""
        global app
        app = QCoreApplication(sys.argv)

        logging.config.fileConfig(os.path.join(os.getcwd(), baseconfdir, loggingconf))
        logger = logging.getLogger("run")

        cf = ConfigParser.ConfigParser()
        cf.read(os.path.join(os.getcwd(), baseconfdir, businessconf))

        me = Business(cf)
        me.start()

        sys.exit(app.exec_())
    except BaseException,e:
        logger.exception(e)

def stop():
    global app
    print 'app:'
    print type(app)
    app.quit()



if __name__ == '__main__':
    from apscheduler.schedulers.blocking import BlockingScheduler

    sched = BlockingScheduler()
    sched.add_job(start, 'cron', id='first', day_of_week ='0-4', hour = 13, minute = 51)
    sched.add_job(stop, 'cron', id='second', day_of_week ='0-4', hour = 13, minute = 52)
    sched.start()

