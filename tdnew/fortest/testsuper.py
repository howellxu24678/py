# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 21:38:30 2015

@author: guosen
"""

class Fruit(object):
    def __init__(self, color):
        self._color = color
        print "fruit's color: %s" % self._color
 
    def grow(self):
        print "grow..."
#继承了父类
#显示调用父类的__init__方法
class Apple(Fruit):
    def __init__(self, color):
        super(Apple, self).__init__(color)
        #Fruit.__init__(self, color)
        print "apple's color: %s" % self._color
 
class Banana(Fruit):
    def __init__(self, color):
        super(Banana, self).__init__(color)
        #Fruit.__init__(self, color)
        print "banana's color:%s" % self._color

    #覆盖了父类的grow方法
    def grow(self):
        #super(Banana, self).grow()
        print "banana grow..."
           
           
# apple = Apple("red")
# apple.grow()
b = Banana("yellow")
b.grow()

