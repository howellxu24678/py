# -*- coding: utf-8 -*-
__author__ = 'xujh'

import time
import pywinauto

# sleepItv = 0.5
# timeOutItv = 30
# retryItv = 1
# tdxExePath = "D:\TdxW_HuaTai\TdxW.exe"
# exportFolder = "export2"
# titleText = u'华泰证券(通达信版)V6.38'
# self._traderTitleText = u'通达信网上交易V6'

import logging
logger = logging.getLogger("run")


class TdxOp(object):
    def __init__(self, cf):
        try:
            self._cf = cf
            self._app = pywinauto.application.Application()

            self._app.start(cf.get("strategy", "tdxExePath"))
            self._mainTitleText = cf.get("strategy", "mainTitleText")
            self._traderTitleText = cf.get("strategy", "traderTitleText")

            self._sleepItv = cf.getint("strategy", "sleepItv")
            self._timeOutItv = cf.getint("strategy", "timeOutItv")
            self._retryItv = cf.getint("strategy", "retryItv")

            self._hqdatadir = cf.get("strategy", "hqdatadir")
            #导出历史行情的文件夹
            self._exportFolder = self._hqdatadir.split("\\")[-1]

        except BaseException,e:
            logger.exception(e)
            raise e

    def WaitForWindow(self, timeout = None, retry_interval = None, **kwargs):
        timeout = self._timeOutItv if timeout is None else timeout
        retry_interval = self._retryItv if retry_interval is None else retry_interval
        return self._app.window_(**kwargs).Wait('exists enabled visible ready', timeout, retry_interval)

    def LoadHistoryData(self):
        try:
            self.WaitForWindow( title=self._mainTitleText)
            hwnd_top = pywinauto.findwindows.find_window(title=self._mainTitleText)
            hwnd_AfxWnd42 = pywinauto.findwindows.find_windows(top_level_only=False, class_name='AfxWnd42', parent=hwnd_top)
            marketW = self._app.window_(handle =hwnd_AfxWnd42[-3])
            marketW.ClickInput()

            self.WaitForWindow(class_name = 'TdxW_MainFrame_Class')
            tdxHq = pywinauto.findwindows.find_window(class_name = 'TdxW_MainFrame_Class')
            td_AfxControlBar = pywinauto.findwindows.find_windows(top_level_only=False, class_name='AfxControlBar42', parent=tdxHq)
            self._mainFrame = self._app.window_(class_name = 'TdxW_MainFrame_Class')
            self._mainFrame.SetFocus()
            tdHandle = self._mainFrame.window_(handle=td_AfxControlBar[0])
            tdHandle.ClickInput(coords=(348, 40))

            self.WaitForWindow(title =u'盘后数据下载')
            phDlg = self._app.window_(title =u'盘后数据下载')
            phtab = phDlg.window_(title ='Tab2', class_name ='SysTabControl32')
            phtab.ClickInput(coords=(100, 15))
            time.sleep(self._sleepItv)
            phtab.ClickInput(coords=(18, 66))
            time.sleep(self._sleepItv)
            phtab.ClickInput(coords=(18, 130))
            self.WaitForWindow(class_name = '#32770', title = 'TdxW')
            tdxW = self._app.window_(class_name = '#32770', title = 'TdxW')
            tdxW.SetFocus()
            tdxW[u'确定'].Click()
            time.sleep(self._sleepItv)
            phtab.ClickInput(coords=(323, 231))

            self.WaitForWindow(title = u'选择品种', class_name = '#32770')
            xzDlg = self._app.window_(title = u'选择品种', class_name = '#32770')
            xzDlg.SetFocus()
            xzDlg.ClickInput(coords=(459, 15))
            time.sleep(self._sleepItv)
            bk = xzDlg.window_(title = 'CFQS', class_name = 'SysListView32')
            #选择自定义板块的td
            bk.ClickInput(coords=(12, 43))
            time.sleep(self._sleepItv)
            xzDlg[u'全选'].Click()
            time.sleep(self._sleepItv)
            xzDlg[u'确定'].Click()
            time.sleep(self._sleepItv)

            phDlg[u'开始下载'].Click()
            pywinauto.timings.WaitUntil(self._timeOutItv, self._retryItv, phDlg.Static2.WindowText, u'下载完毕.')
            phDlg[u'关闭'].Click()

            self._mainFrame.SetFocus()
            self._mainFrame.TypeKeys('34{ENTER}', pause=0.5)
            time.sleep(self._sleepItv)

            self.WaitForWindow(title = u'数据导出', class_name = '#32770')
            sjdcDlg = self._app.window_(title = u'数据导出', class_name = '#32770')
            sjdcDlg[u'高级导出'].Click()
            time.sleep(self._sleepItv)

            self.WaitForWindow(title = u'高级导出', class_name = '#32770')
            gjdcDlg = self._app.window_(title = u'高级导出', class_name = '#32770')
            gjdcDlg[u'5分钟线'].Click()
            time.sleep(self._sleepItv)
            gjdcDlg.Edit1.SetEditText(self._hqdatadir)
            time.sleep(self._sleepItv)
            gjdcDlg[u'添加品种'].Click()
            time.sleep(self._sleepItv)
            xzDlg.ClickInput(coords = (459, 15))
            time.sleep(self._sleepItv)
            #选择自定义板块的td
            bk.ClickInput(coords = (12, 43))
            time.sleep(self._sleepItv)
            xzDlg[u'全选'].Click()
            time.sleep(self._sleepItv)
            xzDlg[u'确定'].Click()
            time.sleep(self._sleepItv)
            gjdcDlg[u'开始导出'].Click()
            self.WaitForWindow(class_name = '#32770', title = 'TdxW')
            tdxW[u'确定'].Click()
            time.sleep(self._sleepItv)
            gjdcDlg[u'关闭'].Click()
            time.sleep(self._sleepItv)

            ef = pywinauto.application.WindowSpecification({'title': self._exportFolder, 'class_name': 'CabinetWClass'})
            ef.SetFocus()
            ef.Close()
        except BaseException,e:
            logger.exception(e)
            raise e

    def EnterTraderDlg(self):
        try:
            hwndTdxM = pywinauto.findwindows.find_window(class_name = 'TdxW_MainFrame_Class')
            hwndTrader = pywinauto.findwindows.find_windows(top_level_only=False, class_name='AfxWnd42', parent=hwndTdxM, found_index=10)
            traderLoginW = self._app.window_(handle = hwndTrader[0])
            traderLoginW.ClickInput()

            #最长等待半个小时
            self.WaitForWindow(timeout = 1800, title=self._traderTitleText, class_name = '#32770', top_level_only=False)
            traderW = self._app.window_(title=self._traderTitleText, class_name = '#32770', top_level_only=False)
            traderW.ClickInput(coords=(48, 76))
        except BaseException,e:
            logger.exception(e)
            raise e

    def Close(self):
        try:
            if self._mainFrame.Exists():
                self._mainFrame.SetFocus()
                self._mainFrame.Close()
        except BaseException,e:
            logger.exception(e)
            raise e
