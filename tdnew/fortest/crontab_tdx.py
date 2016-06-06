# -*- coding: utf-8 -*-
__author__ = 'xujh'


import time
import pywinauto


tdxExePath = "C:\TdxW_HuaTai\TdxW.exe"
app = pywinauto.application.Application()
app.start(tdxExePath)
time.sleep(3)

app.window_(title=u'华泰证券(通达信版)V6.38').SetFocus()
hwnd_top = pywinauto.findwindows.find_window(title=u'华泰证券(通达信版)V6.38')
hwnd_AfxWnd42 = pywinauto.findwindows.find_windows(top_level_only=False, class_name='AfxWnd42', parent=hwnd_top)
market = app.window_(handle=hwnd_AfxWnd42[-3])
market.ClickInput()

td = pywinauto.findwindows.find_window(title = u'华泰证券(通达信版)V6.38 - [行情表-td]')
td_AfxControlBar = pywinauto.findwindows.find_windows(top_level_only=False, class_name='AfxControlBar42', parent=td)
app.window_(title = u'华泰证券(通达信版)V6.38 - [行情表-td]').SetFocus()
tdHandle = app.window_(title = u'华泰证券(通达信版)V6.38 - [行情表-td]').window_(handle=td_AfxControlBar[0])
tdRect = tdHandle.Rectangle()
tdHandle.ClickInput(coords=(tdRect.left + 348, (tdRect.top + tdRect.bottom) / 2), absolute = True)

time.sleep(2)
ph = app.window_(title = u'盘后数据下载')
phRect = ph.Rectangle()
phtab = ph.window_(title='Tab2', class_name='SysTabControl32')
phtab.ClickInput(coords=(phRect.left + 110, phRect.top + 42), absolute = True)



#app.window_(title=u'华泰证券(通达信版)V6.38').window_()
# app.connect(class_name='TdxW_MainFrame_Class')
# app.connect(wantedText=u'华泰证券(通达信版)V6.38')
#app.connect(path=tdxExePath)
# time.sleep(1)
# hwnd_top = pywinauto.findwindows.find_window(title=u'华泰证券(通达信版)V6.38')
# hwnd_AfxWnd42 = pywinauto.findwindows.find_windows(top_level_only=False, class_name='AfxWnd42', parent=hwnd_top)
# market = app.window_(handle=hwnd_AfxWnd42[-3])

# wanted_hwnd = pywinauto.findwindows.find_windows(top_level_only=False, parent=hwnd_AfxWnd42)
# hwnd_AfxWnd42[-3]

#from subprocess import Popen
# p = Popen(tdxExePath)
# time.sleep(3)
# time.sleep(10)
# p.terminate()

# app = pywinauto.application.Application()
# app.start('notepad.exe')
# #top = app.window_(title="")
# app.Notepad.MenuSelect(u'帮助->关于记事本')
# time.sleep(3)
# app.window_(title_re = u'关于“记事本”').SetFocus()
# app.window_(title_re = u'关于“记事本”').window_(title_re = u'确定').Click()