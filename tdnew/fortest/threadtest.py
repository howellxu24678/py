# -*- coding: utf-8 -*-
__author__ = 'xujh'


import threading
import time


def target():
    print 'the current threading %s is running' % threading.current_thread().name
    time.sleep(1)
    print 'the current threading %s is ended' % threading.current_thread().name


print 'the current threading %s is running' % threading.current_thread().name
t = threading.Thread(target=target)

t.start()
t.join()

print 'the current threading %s is ended' % threading.currentThread().name