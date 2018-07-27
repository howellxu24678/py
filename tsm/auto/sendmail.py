# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 13:43:01 2015

@author: guosen
"""

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

from eventengine import *
import logging
logger = logging.getLogger()
import smtplib

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))

class SendMail(object):
    def __init__(self, cf, eventEngine_):
        try:
            self._smtp_server = cf.get("main", "smtp_server")
            self._from_addr = cf.get("main", "from_addr")
            self._from_name = cf.get("main", "from_name")
            self._password = cf.get("main", "password")
            self._eventEngine = eventEngine_
            self._eventEngine.register(EVENT_SENDMAIL, self.onSend)
        except BaseException,e:
            logger.exception(e)
            raise e

    #修改为ssl模式
    def onSend(self, event):
        try:
            remarks = event.dict_['remarks']
            content = event.dict_['content']
            to_addr = event.dict_['to_addr']
            logger.info('sendmail %s:%s, to_addr:%s', remarks, content, to_addr)

            msg = MIMEText(content, 'plain', 'utf-8')
            msg['From'] = _format_addr(u'%s <%s>' % (self._from_name, self._from_addr))
            msg['To'] = ', '.join(to_addr)
            msg['Subject'] = Header(u'%s' % remarks, 'utf-8').encode()

            server = smtplib.SMTP(self._smtp_server, 587)
            server.starttls()
            server.set_debuglevel(1)
            server.login(self._from_addr, self._password)
            server.sendmail(self._from_addr, to_addr, msg.as_string())
            server.quit()
        except BaseException,e:
            logger.exception(e)

if __name__ == '__main__':
    smtp_server = 'smtp.qq.com'
    from_addr = '3043334314@qq.com'
    password = 'bxpanqsjkglrdecd'
    to_addr = '727513059@qq.com'

    msg = MIMEText('test', 'plain', 'utf-8')
    msg['From'] = _format_addr(u'cos监控 <%s> ' % from_addr)
    msg['To'] = to_addr
    msg['Subject'] = Header(u'%s 的提醒……' % 'ddd', 'utf-8').encode()


    server = smtplib.SMTP(smtp_server, 587)
    server.starttls()
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()