# -*- coding: utf-8 -*-
__author__ = 'xujh'

# import multiprocessing
#
# def process(num):
#     print 'process', num
#
# if __name__ == '__main__':
#     for i in range(5):
#         p = multiprocessing.Process(target=process, args=(i,))
#         p.start()
#
#     print 'cpu number', str(multiprocessing.cpu_count())
#
#     for p in multiprocessing.active_children():
#         print 'child process name:' + p.name + 'id:' + str(p.pid)
#
#     print 'process ended'

from multiprocessing import Process
import time

class MyProcess(Process):
    def __init__(self, loop):
        Process.__init__(self)
        self.loop = loop

    def run(self):
        for count in range(self.loop):
            time.sleep(1)
            print 'Pid:' + str(self.pid) + ' LoopCount:' + str(count)

if __name__ == '__main__':
    for i in range(3,5):
        p = MyProcess(i)
        p.daemon = True
        p.start()
        p.join()

    print 'Main process ended!'