__author__ = 'xujhao'

import json


ts = '{"207":"0","38":"500","40":"121","44":"0.00000000","448":"0099607054","48":"000001","625":"00","66":"77","8810":"410000012978","8811":"1","8812":"0005056c00008","8813":"F","8814":"13910000000075e7b6b21601241601242359590000000001TbCo1359MbQ=AopBS/pw6WwjeV4QMvOI8ixz6iseeuSgv2Ff1gLIFn8=","8815":"10388101","8816":"20160124154035000","8821":"4100","8825":"410000012978","8826":"0","8834":"20160124","8842":"100","8902":"410000012978","8920":"410000012978","8970":"0","8975":"0.00000000","9080":"1","9100":"TIM=07:41:22;","9101":"1010","9102":"O181263879xxbcfe7884","916":"154122"}'

my = '{"38":"100","40":"121","448":"0099607054","48":"000001","625":"00","8810":"410000012978","8811":"1","8812":"1:192.168.30.65","8813":"F","8814":"13910000000075e7b6b21601241601242359590000000001TbCo1359MbQ=AhacaW7eNMD/nxlwIvChSNeT7sIZoF6XJs4IFbGZlKQ=","8815":"10388101","8816":"20160124154605827000","8821":"4100","8842":"100","8902":"410000012978","8920":"410000012978","8975":"10.43000000","9101":"1010","916":"153430"}'

jts = json.loads(ts)

jmy = json.loads(my)

ts_set = set(jts.keys())

my_set = set(jmy.keys())


notinmyset = ts_set.difference(my_set)
if len(notinmyset) > 1:
    print "### not in my set:"
    for i in notinmyset:
        print i,jts.get(i)


notintset = my_set.difference(ts_set)
if len(notintset) > 1:
    print "### not in my set:"
    for i in notintset:
        print i,my_set.get(i)
print '\n'
print "diff myset with ts"
for k,v in jmy.iteritems():
    if jts.has_key(k) and v != jts.get(k):
        print "key:", k, "jts:",jts.get(k), "jmy:",v



