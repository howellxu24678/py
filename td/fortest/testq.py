__author__ = 'xujhao'

from qpython import *

with qconnection.QConnection(host = 'localhost', port = 5000) as q:
    print(q)
    print(q('{`int$ til x}', 10))


