# -*- coding: utf-8 -*-
__author__ = 'xujh'


import time
import pywinauto


sleepItv = 1
tdxExePath = "D:\TdxW_HuaTai\TdxW.exe"
exportFolder = "export2"

app = pywinauto.application.Application()
app.start(tdxExePath)
#time.sleep(sleepItv)

app.window_(title=u'华泰证券(通达信版)V6.38').Wait('exists', timeout=30, retry_interval=1)
#app.window_(title=u'华泰证券(通达信版)V6.38').SetFocus()
hwnd_top = pywinauto.findwindows.find_window(title=u'华泰证券(通达信版)V6.38')
hwnd_AfxWnd42 = pywinauto.findwindows.find_windows(top_level_only=False, class_name='AfxWnd42', parent=hwnd_top)
market = app.window_(handle=hwnd_AfxWnd42[-3])
market.ClickInput()
time.sleep(10)


tdxHq = pywinauto.findwindows.find_window(class_name = 'TdxW_MainFrame_Class')
td_AfxControlBar = pywinauto.findwindows.find_windows(top_level_only=False, class_name='AfxControlBar42', parent=tdxHq)
mainFrame = app.window_(class_name = 'TdxW_MainFrame_Class')
mainFrame.SetFocus()
tdHandle = mainFrame.window_(handle=td_AfxControlBar[0])
tdHandle.ClickInput(coords=(348, 40))

time.sleep(sleepItv)
phDlg = app.window_(title = u'盘后数据下载')
#phRect = phDlg.Rectangle()
phtab = phDlg.window_(title='Tab2', class_name='SysTabControl32')
phtab.ClickInput(coords=(100, 15))
time.sleep(sleepItv)
phtab.ClickInput(coords=(18, 66))
time.sleep(sleepItv)
phtab.ClickInput(coords=(18, 130))
tdxW = app.window_(class_name='#32770', title = 'TdxW')
tdxW.SetFocus()
tdxW[u'确定'].Click()
time.sleep(sleepItv)
phtab.ClickInput(coords=(323, 231))

xzDlg = app.window_(title = u'选择品种', class_name='#32770')
xzDlg.SetFocus()
xzDlg.ClickInput(coords=(459, 15))
time.sleep(sleepItv)
bk = xzDlg.window_(title = 'CFQS', class_name='SysListView32')
#选择自定义板块的td
bk.ClickInput(coords=(12, 43))
time.sleep(sleepItv)
xzDlg[u'全选'].Click()
time.sleep(sleepItv)
xzDlg[u'确定'].Click()
time.sleep(sleepItv)

phDlg[u'开始下载'].Click()
time.sleep(20)
phDlg[u'关闭'].Click()

mainFrame.SetFocus()
mainFrame.TypeKeys('34{ENTER}', pause=1)
time.sleep(sleepItv)

sjdcDlg = app.window_(title = u'数据导出', class_name='#32770')
sjdcDlg[u'高级导出'].Click()
time.sleep(sleepItv)

gjdcDlg = app.window_(title = u'高级导出', class_name='#32770')
gjdcDlg[u'5分钟线'].Click()
time.sleep(sleepItv)
gjdcDlg[u'添加品种'].Click()
time.sleep(sleepItv)
xzDlg.ClickInput(coords=(459, 15))
time.sleep(sleepItv)
#选择自定义板块的td
bk.ClickInput(coords=(12, 43))
time.sleep(sleepItv)
xzDlg[u'全选'].Click()
time.sleep(sleepItv)
xzDlg[u'确定'].Click()
time.sleep(sleepItv)
gjdcDlg[u'开始导出'].Click()
time.sleep(10)
tdxW[u'确定'].Click()
time.sleep(sleepItv)
gjdcDlg[u'关闭'].Click()
time.sleep(3)

mainFrame.SetFocus()
mainFrame.CloseAltF4()
time.sleep(sleepItv)

mainFrame.SetFocus()
mainFrame.CloseAltF4()
time.sleep(sleepItv)

while(True):
    try:
        popup_hwnd = mainFrame.PopupWindow()
        if popup_hwnd:
            popup_window = app.window_(handle=popup_hwnd)
            popup_window.SetFocus()
            ctrlsValues = popup_window._ctrl_identifiers()
            for it in ctrlsValues.itervalues():
                if it.count(u'退出') > 0:
                    popup_window[u'退出'].Click()
                    time.sleep(sleepItv)
                    break
                elif it.count(u'取消') > 0:
                    popup_window[u'取消'].Click()
                    time.sleep(sleepItv)
                    break
        else:
            break
        time.sleep(3)
    except BaseException,e:
        print(e)
        break

# if popup_hwnd:
#     popup_window = app.window_(handle=popup_hwnd)
#     popup_window.SetFocus()
#     if popup_window[u'退出'] is not None:
#         popup_window[u'退出'].Click()
#     elif popup_window
#     popup_window.CloseAltF4()
    #popup_window.Button.Click()


# mainFrame.SetFocus()
# mainFrame.CloseAltF4()
# time.sleep(3)
#
# mainFrame.SetFocus()
# mainFrame.CloseAltF4()
# time.sleep(3)
#
# tcqrDlg = app.window_(title = u'退出确认', class_name='#32770')
# tcqrDlg[u'退出'].Click()
# time.sleep(sleepItv)
#
# tsDlg = app.window_(title = u'提示', class_name='#32770')
# tsDlg[u'取消'].Click()
# time.sleep(sleepItv)

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
#
# import re
# phanzi=re.compile(u'华泰证券(通达信版)V6.38 - [[\w\s\u4e00-\u9fa5]]')
# phanzi=re.compile(u'通达信版\[\w\s\u4e00-\u9fa5\]')
# t = u'华泰证券(通达信版)V6.38 - [行情表-tdxHq]'
# phanzi=re.compile(u'通达信版\[[\u4e00-\u9fa5]*\]')
# phanzi=re.compile(u'华泰证券(通达信版)V6.38 - \[[\u4e00-\u9fa5]+\-[\u4e00-\u9fa5]*\w*\]')
# t = u'通达信版[行情表-行情td]'
#
# # phanzi=re.compile(u'通达信版\[[\u4e00-\u9fa5]+\]')
# # t = u'通达信版[行情表]'
# result = phanzi.findall(t)
# for r in result:
#     print r.encode('utf8')