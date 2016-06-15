# -*- coding: utf-8 -*-
__author__ = 'xujh'

def first():
    print("first")

def second():
    print("second")

from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()
sched.add_job(first, 'cron', id='first', day_of_week ='0-4', hour = 21, minute = 44)
sched.add_job(second, 'cron', id='second', day_of_week ='0-4', hour = 21, minute = 45)
sched.start()