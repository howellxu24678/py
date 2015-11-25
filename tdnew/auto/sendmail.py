# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 13:43:01 2015

@author: guosen
"""

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
from eventengine import *

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))


class sendmail(object):
    def __init__(self, cf, eventEngine_):
        self._smtp_server = cf.get("DEFAULT", "smtp_server")
        self._from_addr = cf.get("DEFAULT", "from_addr")
        self._password = cf.get("DEFAULT", "password")
        self._eventEngine = eventEngine_
        self._eventEngine.register(EVENT_SENDMAIL, self.onSend)

        
    def onSend(self, event):
        remarks = event.dict_['remarks']
        content = event.dict_['content']
        to_addr = event.dict_['to_addr']

        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = self._from_addr
        msg['To'] = ', '.join(to_addr)
        msg['Subject'] = Header(u'%s 的提醒……' % remarks, 'utf-8').encode()
        
        server = smtplib.SMTP(self._smtp_server, 25)
        server.set_debuglevel(1)
        server.login(self._from_addr, self._password)
        server.sendmail(self._from_addr, to_addr, msg.as_string())
        server.quit()