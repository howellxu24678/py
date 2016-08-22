# -*- coding: utf-8 -*-
__author__ = 'xujh'


from toolkit import *
from comp import *


class Chan(object):
    def __init__(self, isUp):
        self._isUp = isUp

        #处理包含关系后的标准k线list
        self._KlineList = []

        #笔的端点list
        self._PenPointList = []

        #第一特征序列
        self._FirstSeqList = []

        #第二特征序列
        self._SecondSeqList = []

        self._bCheckSecondSeqListFlag = False

        # 线段
        self._LinePointList = []

        #self._shapeVariableSet = ['na', 'u', 'd']
        self._shapeUpDown = ['u','d']

        self._print = False

    # @profile
    def procKlineContain(self, list, newkline):
        if len(list) < 2:
            Toolkit.procContain(list, self._isUp, newkline)
        else:
            Toolkit.procContain(list, Toolkit.isUp(list[-2], list[-1]), newkline)

    #@profile
    def onNewKline(self, newkline_):
        newkline = Kline(high = newkline_.high, low = newkline_.low, time=newkline_.name)
        self.procKlineContain(self._KlineList, newkline)
        if Toolkit.procShape(self._KlineList):
            if self.procPen():
                self.procLine()

    def getUp(self):
        if len(self._LinePointList) > 0:
            return True if self._PenPointList[self._LinePointList[-1].pidx].shape == 'd' else False
        return True

    #判断第一特征序列的第一和第二元素是否存在缺口
    def hasGap(self):
        if self._FirstSeqList[-2].shape == 'u'and self._FirstSeqList[-2].low > self._FirstSeqList[-3].high:
            return True
        elif self._FirstSeqList[-2].shape == 'd' and self._FirstSeqList[-2].high < self._FirstSeqList[-3].low:
            return True
        else:
            return False

    #添加新的线段端点
    def addNewLinePoint(self):
        Toolkit.append(self._LinePointList, LinePoint(pidx=self._FirstSeqList[-2].bpidx))
        self._curFirstSeqBeginPenPoint = self._FirstSeqList[-2].bpidx
        self._FirstSeqList = []

        if len(self._LinePointList) > 1:
            print '_LinePointList', self._LinePointList
        print '--------------------------'

    def addFirstSeq(self):
        check_fun = Toolkit.checkIfDownShape if self._PenPointList[self._LinePointList[-1].pidx].shape == 'u' else Toolkit.checkIfUpShape
        while (self._curFirstSeqBeginPenPoint <= len(self._PenPointList) - 5):
            newsq = Seq(bpidx=self._PenPointList[self._curFirstSeqBeginPenPoint + 1].idx,
                        bvalue=self._PenPointList[self._curFirstSeqBeginPenPoint + 1].value,
                        epidx=self._PenPointList[self._curFirstSeqBeginPenPoint + 2].idx,
                        evalue=self._PenPointList[self._curFirstSeqBeginPenPoint + 2].value,
                        high=max(self._PenPointList[self._curFirstSeqBeginPenPoint + 1].value,
                                 self._PenPointList[self._curFirstSeqBeginPenPoint + 2].value),
                        low=min(self._PenPointList[self._curFirstSeqBeginPenPoint + 1].value,
                                self._PenPointList[self._curFirstSeqBeginPenPoint + 2].value))

            # todo：目前线段的生成中，遇到笔破坏线段的情况时
            # 原著中的条件是“一笔破坏了线段并这一笔后面延伸出成为线段的走势（也即形成新的线段）”
            # 目前的判断逻辑只判断是否有笔对线段的破坏，并没有进行是否有新的线段生成的判断，从7月20~25 1分钟k线生成的结果来看不准确，需要进行更改
            Toolkit.procSeqContain(self._FirstSeqList,
                                   self.getUp(), newsq,
                                   not Toolkit.lineBreakByPen(self._FirstSeqList,
                                                          self._PenPointList[self._LinePointList[-1].pidx].shape,
                                                          newsq))

            self._curFirstSeqBeginPenPoint += 2
            if check_fun(self._FirstSeqList):
                if len(self._FirstSeqList) > 1:
                    print '_FirstSeqList', self._FirstSeqList

                # 第一种情况（第一第二元素没有缺口）
                if not self.hasGap():
                    self.addNewLinePoint()
                    break
                # 第二种情况（第一第二元素有缺口）,判断第二特征序列是否存在分型
                else:
                    self._bCheckSecondSeqListFlag = True
                    self._curSecondSeqBeginPenPoint = self._FirstSeqList[-2].bpidx

    def addSecondSeq(self):
        check_fun = Toolkit.checkIfUpShape if self._PenPointList[self._LinePointList[-1].pidx].shape == 'u' else Toolkit.checkIfDownShape
        while (self._curSecondSeqBeginPenPoint <= len(self._PenPointList) - 5):
            newsq = Seq(bpidx=self._PenPointList[self._curSecondSeqBeginPenPoint + 1].idx,
                        bvalue=self._PenPointList[self._curSecondSeqBeginPenPoint + 1].value,
                        epidx=self._PenPointList[self._curSecondSeqBeginPenPoint + 2].idx,
                        evalue=self._PenPointList[self._curSecondSeqBeginPenPoint + 2].value,
                        high=max(self._PenPointList[self._curSecondSeqBeginPenPoint + 1].value,
                                 self._PenPointList[self._curSecondSeqBeginPenPoint + 2].value),
                        low=min(self._PenPointList[self._curSecondSeqBeginPenPoint + 1].value,
                                self._PenPointList[self._curSecondSeqBeginPenPoint + 2].value))
            Toolkit.procSeqContain(self._SecondSeqList, not self.getUp(), newsq)

            self._curSecondSeqBeginPenPoint += 2
            if check_fun(self._SecondSeqList):
                if len(self._SecondSeqList) > 1:
                    print '_SecondSeqList', self._SecondSeqList
                self.addNewLinePoint()
                self._bCheckSecondSeqListFlag = False
                self._SecondSeqList = []
                break
            #todo：else的情况如果第二种情况不成立，要去找顶底分型却一直没有找到的情况，应该如何应对？原著中没有对此情况进行阐述
            # 目前我想到的合理的解决方案应该是从后续端点去判断新线段的形成。从而形成对原线段的破坏，通过这个因素来确定退出条件


    def procLine(self):
        # 生成笔的最后的两点是会变的，所以只关注笔的最后两点之前的
        # 笔的方向可以通过终点的类型来判断，如果是'u'则是向上笔，如果是'd'则是向下笔
        # 首次开始
        # 笔的数量小于3时，即笔的端点小于4时，算上最后两点是不确定的，所以这里应该是5，不可能形成线段
        if len(self._PenPointList) < 5:
            return

        if len(self._LinePointList) < 1:
            self._curFirstSeqBeginPenPoint = 0 if Toolkit.checkBeginPoint(self._PenPointList, 0) else 1
            Toolkit.append(self._LinePointList, LinePoint(pidx=self._curFirstSeqBeginPenPoint))

        if not self._bCheckSecondSeqListFlag:
            self.addFirstSeq()
        else:
            self.addSecondSeq()


    #获取笔所在端点的值，用于判断是否与之前设定的值一致，否则进行修改
    def getPenPoint(self, penIdxFrom):
        fun = Toolkit.getUpHighPoint if self._PenPointList[penIdxFrom].shape == 'u' else Toolkit.getDownLowPoint
        return fun(self._KlineList[self._PenPointList[penIdxFrom].kidx:])

    #获取笔所在端点的下一个值，主要用于笔新端点的添加
    def getPenPointNext(self, penIdxFrom):
        fun = Toolkit.getUpHighPoint if self._PenPointList[penIdxFrom].shape == 'd' else Toolkit.getDownLowPoint
        return fun(self._KlineList[self._PenPointList[penIdxFrom].kidx:])

    #获取笔所在端点的下一个值，主要用于笔新端点的添加
    def getPenPointNextDistance(self, penIdxFrom):
        if self._PenPointList[penIdxFrom].kidx + DISTANCE > len(self._KlineList) - 1:
            return

        fun = Toolkit.getUpHighPoint if self._PenPointList[penIdxFrom].shape == 'd' else Toolkit.getDownLowPoint
        return fun(self._KlineList[self._PenPointList[penIdxFrom].kidx + DISTANCE:])

    def procPen(self):
        #首次开始，从后往前-4的位置找相异的分型,找到之后还要往前找看有没有更高或者更低的
        if len(self._PenPointList) < 2:
            Toolkit.getFirstTwoPenPoint(self._PenPointList, self._KlineList)
        else:
            #先看当前高点或者地点是否有更新
            kline = self.getPenPoint(-1)
            if kline.idx > self._PenPointList[-1].kidx:
                Toolkit.updatePen(self._PenPointList, -1, kline)
                return True

            kline = self.getPenPointNext(-1)
            if kline is None:
                return False
            #如果下一个高点或者低点与倒数第一个点构不成笔，但是比倒数第二个点更高或者更低，则删除倒数第一个点，更新倒数第二个点
            elif kline.idx - self._PenPointList[-1].kidx < 4:
                if (self._PenPointList[-2].shape == 'u' and kline.high > self._PenPointList[-2].value) or \
                    (self._PenPointList[-2].shape == 'd' and kline.low < self._PenPointList[-2].value):
                    self._PenPointList.pop()
                    Toolkit.updatePen(self._PenPointList, -1, kline)
                    return True
            else:
                Toolkit.appendPen(self._PenPointList, kline)
                return True

            #解决下一个最高点或者最低点距离小于4，但是其实大于4的距离有合适的点存在的情况，这个时候存在笔（之前遗漏了）
            kline = self.getPenPointNextDistance(-1)
            if kline is None:
                return False
            else:
                Toolkit.appendPen(self._PenPointList, kline)
                return True