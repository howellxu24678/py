# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 21:38:30 2015

@author: guosen
"""

class Fruit:
      def __init__(self, color):
           self._color = color
           print "fruit's color: %s" %self._color
 
      def grow(self):
           print "grow..."
 
class Apple(Fruit):                               #继承了父类
      def __init__(self, color):                  #显示调用父类的__init__方法
           Fruit.__init__(self, color)
           print "apple's color: %s" % self._color
 
class Banana(Fruit):                              #继承了父类
      def __init__(self, color):                  #显示调用父类的__init__方法
           Fruit.__init__(self, color)
           print "banana's color:%s" % self._color
 
      def grow(self):                             #覆盖了父类的grow方法
           print "banana grow..."
           
           
apple = Apple("red")
apple.grow()
banana = Banana("yellow")
banana.grow()