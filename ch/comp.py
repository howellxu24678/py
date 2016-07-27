# -*- coding: utf-8 -*-
__author__ = 'xujh'


class Base(object):
    def __init__(self):
        self.idx = 0

    def __str__(self):
        return str(self.__dict__) + '\n'

    def __repr__(self):
        return str(self)


class Kline(Base):
    def __init__(self, **kwargs):
        super(Kline, self).__init__()
        # shape 用于区分是顶分型还是底分型
        self.high = kwargs['high']
        self.low = kwargs['low']
        self.shape = kwargs['shape'] if 'shape' in kwargs else 'un'
        self.time = kwargs['time']


class PenPoint(Base):
    def __init__(self, **kwargs):
        super(PenPoint, self).__init__()
        # kidx在标准k线列表中所处的index，value顶点或者底点的值，shape顶分型还是底分型
        self.kidx = kwargs['kidx']
        self.value = kwargs['value']
        self.shape = kwargs['shape'] if 'shape' in kwargs else 'un'
        self.stable = 0


class LinePoint(Base):
    def __init__(self, **kwargs):
        super(LinePoint, self).__init__()
        # kidx在标准k线列表中所处的index，pidx在笔列表中所处的index,value顶点或者底点的值，shape顶分型还是底分型
        #pidx在笔列表中所处的index
        self.pidx = kwargs['pidx']



class Seq(Base):
    def __init__(self, **kwargs):
        super(Seq, self).__init__()
        self.bpidx = kwargs['bpidx']
        self.epidx = kwargs['epidx']
        self.bvalue = kwargs['bvalue']
        self.evalue = kwargs['evalue']
        self.high = kwargs['high'] if 'high' in kwargs else 'un'
        self.low = kwargs['low'] if 'low' in kwargs else 'un'
        self.shape = kwargs['shape'] if 'shape' in kwargs else 'un'


#中枢的计算生成类
class Center(Base):
    def __init__(self, **kwargs):
        super(Center, self).__init__()
        self.xy = kwargs['xy']
        self.width = kwargs['width']
        self.heigth = kwargs['heigth']


class CenterCalc(object):
    def __init__(self):
        self._lastIndex = 0
        #self.

    def calc(self, penlist):
        #形成一个中枢，需要6个端点
        if len(penlist) < 6:
            return

        for i in range(self._lastIndex, len(penlist)):
            if penlist[i].shape == 'd':
                min_ = min(penlist[i+1].value, penlist[i+3].value)
                max_ = max(penlist[i+2].value, penlist[i+4].value)
            else:
                min_ = min(penlist[i+2].value, penlist[i+4].value)
                max_ = max(penlist[i+1].value, penlist[i+3].value)

            #中枢成立
            if min_ > max_:
                pass


