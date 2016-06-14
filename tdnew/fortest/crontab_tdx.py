# -*- coding: utf-8 -*-
__author__ = 'xujh'


import time
import pywinauto


sleepItv = 0.5
timeOutItv = 30
retryItv = 1
tdxExePath = "D:\TdxW_HuaTai\TdxW.exe"
exportFolder = "export2"


def WaitForWindow(app_, **kwargs):
    return app_.window_(**kwargs).Wait('exists enabled visible ready', timeout=timeOutItv, retry_interval=retryItv)

app = pywinauto.application.Application()
app.start(tdxExePath)

WaitForWindow(app, title=u'华泰证券(通达信版)V6.38')
hwnd_top = pywinauto.findwindows.find_window(title=u'华泰证券(通达信版)V6.38')
hwnd_AfxWnd42 = pywinauto.findwindows.find_windows(top_level_only=False, class_name='AfxWnd42', parent=hwnd_top)
market = app.window_(handle =hwnd_AfxWnd42[-3])
market.ClickInput()


WaitForWindow(app, class_name = 'TdxW_MainFrame_Class')
tdxHq = pywinauto.findwindows.find_window(class_name = 'TdxW_MainFrame_Class')
td_AfxControlBar = pywinauto.findwindows.find_windows(top_level_only=False, class_name='AfxControlBar42', parent=tdxHq)
mainFrame = app.window_(class_name = 'TdxW_MainFrame_Class')
mainFrame.SetFocus()
tdHandle = mainFrame.window_(handle=td_AfxControlBar[0])
tdHandle.ClickInput(coords=(348, 40))

WaitForWindow(app, title =u'盘后数据下载')
phDlg = app.window_(title =u'盘后数据下载')
phtab = phDlg.window_(title ='Tab2', class_name ='SysTabControl32')
phtab.ClickInput(coords=(100, 15))
time.sleep(sleepItv)
phtab.ClickInput(coords=(18, 66))
time.sleep(sleepItv)
phtab.ClickInput(coords=(18, 130))
WaitForWindow(app, class_name = '#32770', title = 'TdxW')
tdxW = app.window_(class_name = '#32770', title = 'TdxW')
tdxW.SetFocus()
tdxW[u'确定'].Click()
time.sleep(sleepItv)
phtab.ClickInput(coords=(323, 231))

WaitForWindow(app, title = u'选择品种', class_name = '#32770')
xzDlg = app.window_(title = u'选择品种', class_name = '#32770')
xzDlg.SetFocus()
xzDlg.ClickInput(coords=(459, 15))
time.sleep(sleepItv)
bk = xzDlg.window_(title = 'CFQS', class_name = 'SysListView32')
#选择自定义板块的td
bk.ClickInput(coords=(12, 43))
time.sleep(sleepItv)
xzDlg[u'全选'].Click()
time.sleep(sleepItv)
xzDlg[u'确定'].Click()
time.sleep(sleepItv)

phDlg[u'开始下载'].Click()
pywinauto.timings.WaitUntil(timeOutItv, retryItv, phDlg.Static2.WindowText, u'下载完毕.')
phDlg[u'关闭'].Click()

mainFrame.SetFocus()
mainFrame.TypeKeys('34{ENTER}', pause=0.5)
time.sleep(sleepItv)

WaitForWindow(app, title = u'数据导出', class_name = '#32770')
sjdcDlg = app.window_(title = u'数据导出', class_name = '#32770')
sjdcDlg[u'高级导出'].Click()
time.sleep(sleepItv)

WaitForWindow(app, title = u'高级导出', class_name = '#32770')
gjdcDlg = app.window_(title = u'高级导出', class_name = '#32770')
gjdcDlg[u'5分钟线'].Click()
time.sleep(sleepItv)
gjdcDlg[u'添加品种'].Click()
time.sleep(sleepItv)
xzDlg.ClickInput(coords = (459, 15))
time.sleep(sleepItv)
#选择自定义板块的td
bk.ClickInput(coords = (12, 43))
time.sleep(sleepItv)
xzDlg[u'全选'].Click()
time.sleep(sleepItv)
xzDlg[u'确定'].Click()
time.sleep(sleepItv)
gjdcDlg[u'开始导出'].Click()
WaitForWindow(app, class_name = '#32770', title = 'TdxW')
tdxW[u'确定'].Click()
time.sleep(sleepItv)
gjdcDlg[u'关闭'].Click()
time.sleep(sleepItv)

ef = pywinauto.application.WindowSpecification({'title': exportFolder, 'class_name': 'CabinetWClass'})
ef.SetFocus()
ef.Close()

mainFrame.SetFocus()
mainFrame.Close()
