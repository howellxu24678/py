# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 18:13:52 2015

@author: guosen
"""
import trade
import quote

from apscheduler.schedulers.background import BackgroundScheduler

class Stg_td(object):
    def __init__(self, quote_, trade_):
        self.__quote = quote_
        self.__trade = trade_
        
        self.__sched  = BackgroundScheduler()
    
    def start(self):
        self.__sched.add_job(self.__quote.TimerToDo, 'interval', args=(self.OnNewKLine,),  seconds=3)
        self.__sched.start()
        print "Stg_td start"
        
    def stop(self):
        self.__sched.shutdown()
        
    def OnNewKLine(self, kline):
        print "OnNewKLine"
        print kline
        