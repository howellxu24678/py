# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 14:31:06 2015

@author: guosen
"""

import time
import datetime
import ConfigParser 

import logging
logger = logging.getLogger("run")

class trade(object):
    def __init__(self, cf):
        self._cf = cf;
    
    def buy(self, stock_code, stock_price, stock_number):
        pass
        
    def sell(self, stock_code, stock_price, stock_number):
        pass