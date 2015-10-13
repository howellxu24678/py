# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 17:11:30 2015

@author: guosen
"""
#import os
#import ConfigParser
#
#baseconfdir="conf"
#businessconf= "business.ini"
#
#
#buconf = os.path.join(os.getcwd(), baseconfdir, businessconf)
#cf = ConfigParser.ConfigParser()
#cf.read(buconf)
#
#class Animal(object):
#    def run(self):
#        print 'Animal is running...'
#        
#class Dog(Animal):
#    def run(self):
#        print 'Dog is running...'
#
#class Cat(Animal):
#    def run(self):
#        print 'Cat is running..'
#        
#def run_twice(animal):
#    animal.run()
    
import trade

trader = trade.gui_trade()
