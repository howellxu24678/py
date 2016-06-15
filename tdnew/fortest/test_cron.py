# -*- coding: utf-8 -*-
__author__ = 'xujh'

def some_decorated_task():
    print("I am printed at")

from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()
sched.add_job(some_decorated_task, 'cron', id='my_job_id', day_of_week ='0-4', hour = 17, minute = 31)
sched.start()