# -*- coding: utf-8 -*-
__author__ = 'xujh'

# import telnetlib
#
# '''Telnet远程登录：Windows客户端连接Linux服务器'''
#
# # 配置选项
# Host = '172.24.181.71'  # Telnet服务器IP
# username = 'cos'  # 登录用户名
# password = 'coscos'  # 登录密码
# finish = ':~$ '  # 命令提示符（标识着上一条命令已执行完毕）
#
# # 连接Telnet服务器
# tn = telnetlib.Telnet(Host)
#
# # 输入登录用户名
# tn.read_until('login: ')
# tn.write(username + '\n')
#
# # 输入登录密码
# tn.read_until('Password: ')
# tn.write(password + '\n')
#
# # 登录完毕后，执行ls命令
# tn.read_until(finish)
# tn.write('ls\n')
#
# # ls命令执行完毕后，终止Telnet连接（或输入exit退出）
# tn.read_until(finish)
# tn.close()  # tn.write('exit\n')

import os, sys, re
import subprocess

hostlist = ['172.24.181.71','172.24.182.102']
def runCheck():

    for host in hostlist:
        p = subprocess.Popen(["ping -n 1 " + host],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=True)
        out = p.stdout.read()
        regex = re.compile("time=\d*", re.IGNORECASE | re.MULTILINE)
        if len(regex.findall(out)) > 0:
            print host + ': Host Up!'
        else:
            print host + ': Host Down!'


def Usage():
    print """ ---Need to enter an absolute path---
---(The current directory except)---"""

import time
while True:

    runCheck()
    time.sleep(1)
    # Usage()
    # source = raw_input('Please input your check_host_list_file:')
    # if os.path.exists(source):
    #     runCheck(source)
    #     exit()
    #
    # elif source == 'ls':
    #     print '--------List current directory--------'
    #     os.system('ls')
    #
    # else:
    #     print "Sorry your check_host_list_file not exist!"