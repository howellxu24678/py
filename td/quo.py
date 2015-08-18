# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 17:11:33 2015

@author: guosen
"""

import tushare as ts


class TsQuo(object):    
    
    def GetHistKlineFq(self, ):
        ts.get_hist_data('600783',ktype='60',start='2015-07-06',end='2015-08-14')
    

#无复权60分钟线
dfnfq60m = ts.get_hist_data('600783',ktype='60',start='2015-07-06',end='2015-08-14')

#复权日线
dffq1d = ts.get_h_data('600783',start='2015-07-06',end='2015-08-14')

#无复权日线
dfnfq1d = ts.get_h_data('600783',autype=None,start='2015-07-06',end='2015-08-14')

#复权/无复权比率
rate = (dffq1d['close'] / dfnfq1d['close'])