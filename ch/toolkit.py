# -*- coding: utf-8 -*-
__author__ = 'xujh'

from comp import *


MIN_FLOAT = 1e-4
#顶分型（含）与底分型（含）的连接线上必须至少有5根蜡烛线才能构成一笔, i+1>=5,即i>=4
DISTANCE = 4

class Toolkit(object):
    _shapeVariableSet = ['na', 'u', 'd']
    _shapeUpDown = ['u', 'd']
    def __init__(self):
        pass

    # 是否存在包含关系
    @staticmethod
    def isContain(prekline, curkline):
        # 向左包含 n+1包含n
        if curkline.high >= prekline.high and curkline.low <= prekline.low:
            return True
        # 向右包含 n包含n+1
        elif curkline.high <= prekline.high and curkline.low >= prekline.low:
            return True
        else:
            return False


    # 判断是上升趋势还是下降趋势,True为上升趋势，False为下降趋势
    @staticmethod
    def isUp(line1, line2):
        if line2.high >= line1.high and line2.low >= line1.low:
            return True
        else:
            return False


    @staticmethod
    def getShape(line1, line2, line3):
        # 顶分型
        if line2.high > line1.high \
                and line2.high > line3.high:
            return 'u'
        # 底分型
        elif line2.low < line1.low \
                and line2.low < line3.low:
            return 'd'
        # 未知情况
        else:
            return 'na'

    @staticmethod
    def checkIfUpShape(list):
        if len(list) < 3:
            return False

        if list[-2].high >= list[-1].high and list[-2].high >= list[-3].high:
            list[-2].shape = 'u'
            return True
        return False

    @staticmethod
    def checkIfDownShape(list):
        if len(list) < 3:
            return False

        if list[-2].low <= list[-1].low and list[-2].low <= list[-3].low:
            list[-2].shape = 'd'
            return True
        return False

    @staticmethod
    # @profile
    def append(list, dict_value):
        dict_value.idx = len(list)
        list.append(dict_value)

    @staticmethod
    # @profile
    def procContain(list, isUp, newkline):
        if len(list) < 1 or not Toolkit.isContain(list[-1], newkline):
            Toolkit.append(list, newkline)
        else:
            # 高点取高值，低点也取高值，简单的说就是“上升取高高”
            if isUp:
                newkline.high = max(list[-1].high, newkline.high)
                newkline.low = max(list[-1].low, newkline.low)
            # 高点取低值，低点也取低值，简单的说就是“下降取低低”
            else:
                newkline.high = min(list[-1].high, newkline.high)
                newkline.low = min(list[-1].low, newkline.low)
            # 处理完包含关系后，将前一个删除，只保留最终处理完的结果
            list.pop()
            # 递归处理包含关系，有可能出现处理包含之后的元素和之前的元素还存在包含关系
            return Toolkit.procContain(list, isUp, newkline)

    @staticmethod
    # @profile
    def procSeqContain(list, isUp, newseq, needproc = True):
        if not needproc or len(list) < 1 or not Toolkit.isContain(list[-1], newseq):
            Toolkit.append(list, newseq)
        else:
            # 高点取高值，低点也取高值，简单的说就是“上升取高高”
            if isUp:
                if list[-1].high - newseq.high > MIN_FLOAT:
                    newseq.bvalue = newseq.high = list[-1].high
                    newseq.bpidx = list[-1].bpidx
                else:
                    newseq.evalue = newseq.low = list[-1].low
                    newseq.epidx = list[-1].epidx
                # newseq.high = max(list[-1].high, newseq.high)
                # newseq.low = max(list[-1].low, newseq.low)
            # 高点取低值，低点也取低值，简单的说就是“下降取低低”
            else:
                if list[-1].high - newseq.high > MIN_FLOAT:
                    newseq.bvalue = newseq.low = list[-1].low
                    newseq.bpidx = list[-1].bpidx
                else:
                    newseq.evalue = newseq.high = list[-1].high
                    newseq.epidx = list[-1].epidx
                # newseq.high = min(list[-1].high, newseq.high)
                # newseq.low = min(list[-1].low, newseq.low)
            # 处理完包含关系后，将前一个删除，只保留最终处理完的结果
            list.pop()
            # 递归处理包含关系，有可能出现处理包含之后的元素和之前的元素还存在包含关系
            return Toolkit.procSeqContain(list, isUp, newseq, needproc)

    @staticmethod
    def procShape(list):
        has_new_shape = False
        if len(list) < 3:
            return has_new_shape
        for i in xrange(2, len(list)):
            # 性能优化，只做一次推断，不重复推断
            if list[-i].shape in Toolkit._shapeVariableSet:
                break

            _shape = Toolkit.getShape(
                list[-i - 1],
                list[-i],
                list[-i + 1])
            list[-i].shape = _shape
            if _shape in Toolkit._shapeUpDown:
                has_new_shape = True

        return has_new_shape
    # 方向（属于向上笔还是向下笔）
    @staticmethod
    def getDirect(pen_start, pen_end):
        # 向上笔
        if pen_start['value'] < pen_end['value']:
            return 'u'
        # 向下笔
        elif pen_start['value'] > pen_end['value']:
            return 'd'
        # 位置情况
        return 'na'


    @staticmethod
    def lineBreakByPen(seqlist, lineBeginShape, newsq):
        if len(seqlist) < 1:
            return False
        for i in xrange(1, len(seqlist) + 1):
            if (lineBeginShape == 'd' and newsq.low < seqlist[-i].high) \
                or (lineBeginShape == 'u' and newsq.high > seqlist[-i].low):
                return True
        return False

    # 获取subDf中形态为顶分型的最高点
    @staticmethod
    # @profile
    def getUpHighPoint(subList):
        upSubList = filter(Toolkit.up_shape, subList)
        return max(upSubList, key=lambda x: x.high) if upSubList else None


    # 获取subDf中形态为底分型的最低点
    @staticmethod
    # @profile
    def getDownLowPoint(subList):
        downSubList = filter(Toolkit.down_shape, subList)
        return min(downSubList, key=lambda x: x.low) if downSubList else None

    @staticmethod
    def updatePen(penList, idxFrom, kline):
        value_ = kline.high if kline.shape == 'u' else kline.low
        penList[idxFrom].kidx = kline.idx
        penList[idxFrom].value = value_

    @staticmethod
    def checkBeginPoint(penlist, idxFrom):
        if penlist[idxFrom].shape == 'd' and penlist[idxFrom + 3].value > penlist[idxFrom + 1].value:
            return True
        elif penlist[idxFrom].shape == 'u' and penlist[idxFrom + 3].value < penlist[idxFrom + 1].value:
            return True
        else:
            return False

    @staticmethod
    def has_shape(x):
        return True if x.shape == 'u' or x.shape == 'd' else False

    @staticmethod
    def up_shape(x):
        return True if x.shape == 'u' else False

    @staticmethod
    def down_shape(x):
        return True if x.shape == 'd' else False

    @staticmethod
    def appendPen(penlist, kline):
        value_ = kline.high if kline.shape == 'u' else kline.low
        Toolkit.append(penlist, PenPoint(kidx=kline.idx, shape=kline.shape, value=value_))

    #首次形成第一笔，从后往前找能形成笔(距离>=4)的相异分型
    @staticmethod
    def getFirstTwoPenPoint(penlist, klist):
        hasShapeList = filter(Toolkit.has_shape, klist)
        if len(hasShapeList) < 2:
            return

        secondKlineToAdd = hasShapeList[-1]
        preOppoShapeList = filter(Toolkit.up_shape, hasShapeList) \
            if secondKlineToAdd.shape == 'd' \
            else filter(Toolkit.down_shape, hasShapeList)

        if len(preOppoShapeList) < 1:
            return

        for i in range(1, len(preOppoShapeList) + 1):
            #找到距离满足成笔条件的k线
            if secondKlineToAdd.idx - preOppoShapeList[-i].idx >= DISTANCE:
                #查看有没有地点更低或者高点更高的
                subOppoShapeList = preOppoShapeList[:len(preOppoShapeList) - i + 1]
                preKline = Toolkit.getUpHighPoint(subOppoShapeList) \
                    if secondKlineToAdd.shape == 'd' \
                    else Toolkit.getDownLowPoint(subOppoShapeList)
                firstKlineToAdd = preKline if preKline.idx < preOppoShapeList[-i].idx else preOppoShapeList[-i]
                Toolkit.appendPen(penlist, firstKlineToAdd)
                Toolkit.appendPen(penlist, secondKlineToAdd)


