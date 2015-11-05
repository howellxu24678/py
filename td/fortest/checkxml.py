#-*- coding: UTF-8 -*-
from lxml import etree
import  os
import  sys
xml_file_name = os.path.join(os.getcwd(), "maServer.xml")
doc = etree.parse(xml_file_name)
root = doc.getroot()

needToDealList = []

def StdInt2Str(sid):
    '''
    将sid的转为int再转string，目的是去掉前面的0，使其统一
    :param sid: string
    :return:
    '''
    try:
        return str(int(sid))
    except:
        return str(sid)

def genQueueNullStr(sr, sf):
    return sr.get("id") + "_" + sf.get("id")

def genAdjValue(s, sr, sf):
    return "srvid:" + \
           sr.get("id") + "_" + "funcid:" + \
           sf.get("id") + "_" + "clsid:" + \
           sf.get("clsid")


def addDegree(dictdegree, section, node):
    if dictdegree.has_key(section):
        if node in dictdegree[section]:
            dictdegree[section][node] += 1
        else:
            dictdegree[section][node] = 1
    else:
        d = {node: 1}
        dictdegree[section] = d

def isNeedToDeal(s):
    if s.getparent().tag == "kernel":
        return False
    elif "all" in needToDealList:
        return True
    elif s.getparent().tag in needToDealList:
        return  True
    else:
        return  False


def checkServiceId():
    '''
    校验ServiceId 是否有重复，允许不同的parent下的ServiceId重复
    :return:
    '''
    print "####----- %-20s ------####" % "checkServiceId"
    idictset = {}
    for s in root.getiterator('services'):
        for sr in s.getiterator("service"):
            if not isNeedToDeal(s):
                continue
            sid = sr.get("id")
            if idictset.has_key(s.getparent().tag):
                if sid in idictset[s.getparent().tag]:
                    print "error!!!", s.getparent().tag, "services name:",sr.get("name"), "id:", sid, "is duplicated"
                    raise RuntimeError, 'checkServiceId failed'
                else:
                    idictset[s.getparent().tag].add(sid)
            else:
                idset = set()
                idset.add(sid)
                idictset[s.getparent().tag] = idset

    print "serviceId:", idictset

def checkQueueId():
    '''
    校验QueueId 是否有重复，允许不同的parent下的QueueId重复
    :return:
    '''
    print "####----- %-20s ------####" % "checkQueueId"
    idictset = {}
    for queuses in root.getiterator('queues'):
        for msgqueue in queuses.getiterator("msgqueue"):
            if not isNeedToDeal(queuses):
                continue
            sid = StdInt2Str(msgqueue.get("id"))
            if idictset.has_key(queuses.getparent().tag):
                if sid in idictset[queuses.getparent().tag]:
                    print "error!!!", queuses.getparent().tag, "msgqueue name:",msgqueue.get("name"), "id:", sid, "is duplicated"
                    raise RuntimeError, 'checkQueueId failed'
                else:
                    idictset[queuses.getparent().tag].add(sid)
            else:
                idset = set()
                idset.add(sid)
                idictset[queuses.getparent().tag] = idset

    print "queueId:", idictset
    return idictset

def mqDictSetAdd(mqdictset, s, q):
    if mqdictset.has_key(s.getparent().tag):
        mqdictset[s.getparent().tag].add(q)
    else:
        mqset = set()
        mqset.add(q)
        mqdictset[s.getparent().tag] = mqset

def parseQueue(q):
    if q.find(':') > -1:
        return StdInt2Str(q.split(':')[1].strip())
    else:
        return  StdInt2Str(q.strip())

def findAllMsgQueueInServices():
    '''
    获得所有节点的集合及其入度出度
    :return:
    '''
    print "####----- %-20s ------####" % "findAllMsgQueueInServices"
    mqdictset = {}

    for s in root.getiterator('services'):
        for sr in s.getiterator("service"):
            for sf in sr.getiterator("svcfunc"):
                if not isNeedToDeal(s):
                    continue
                if sf.get("inqueue") != "":
                    for q in sf.get("inqueue").split(','):
                        mqDictSetAdd(mqdictset, s, parseQueue(q))
                if sf.get("outqueue") != "":
                    for q in sf.get("outqueue").split(','):
                        mqDictSetAdd(mqdictset, s, parseQueue(q))

                if sf.get("inqueue") == "" or sf.get("outqueue") == "":
                    mqDictSetAdd(mqdictset, s, genQueueNullStr(sr, sf))

    print "mqdictset", mqdictset
    return mqdictset

def parseXa():
    '''
    解析xa模块
    :return:
    '''
    xadict = {}
    for xas in root.getiterator('xas'):
        for xa in xas.getiterator("xa"):
            if not isNeedToDeal(xas):
                continue
            xaopen = xa.get("xaopen")
            queidindex = xaopen.find("queid")
            if queidindex > -1:
                queid = xaopen[queidindex: xaopen.find(";", queidindex)].split("=")[1]
                if xadict.has_key(xas.getparent().tag):
                    xadict[xas.getparent().tag][queid] = xa.get("name") + "_" + xa.get("id")
                else:
                    dxa = {queid: xa.get("name") + "_" + xa.get("id")}
                    xadict[xas.getparent().tag] = dxa
    return xadict


def getSrvAdj(mqdictset):
    '''
    生成邻接表
    :return:
    '''

    dictmat = {}
    dictindegree = {}
    dictoutdegree = {}
    for k,v in mqdictset.iteritems():
        dictmat[k] =  [["" for i in range(len(v))] for j in range(len(v))]

    for s in root.getiterator('services'):
        for sr in s.getiterator("service"):
            for sf in sr.getiterator("svcfunc"):
                if not isNeedToDeal(s):
                    continue

                inqueuelist=[]
                outqueuelist=[]
                if not (sf.get("inqueue") is None or sf.get("inqueue") == ""):
                    inqueuelist = sf.get("inqueue").split(',')
                if not (sf.get("outqueue") is None or sf.get("outqueue") == ""):
                    outqueuelist = sf.get("outqueue").split(',')
                sr_adj_value = genAdjValue(s,sr,sf)
                section = s.getparent().tag
                mqlist = list(mqdictset[section])
                if len(inqueuelist) > 0 and len(outqueuelist) > 0:
                    for iq in inqueuelist:
                        for oq in outqueuelist:
                            dictmat[s.getparent().tag][mqlist.index(parseQueue(iq))][mqlist.index(parseQueue(oq))] = sr_adj_value
                            addDegree(dictindegree, section, parseQueue(oq))
                            addDegree(dictoutdegree, section, parseQueue(iq))

                if len(inqueuelist) > 0 and len(outqueuelist) == 0:
                    for iq in inqueuelist:
                        dictmat[s.getparent().tag][mqlist.index(parseQueue(iq))][mqlist.index(genQueueNullStr(sr, sf))] = sr_adj_value
                        addDegree(dictindegree, section, genQueueNullStr(sr, sf))
                        addDegree(dictoutdegree, section, parseQueue(iq))


                if len(inqueuelist) == 0 and len(outqueuelist) > 0:
                    for oq in outqueuelist:
                        dictmat[s.getparent().tag][mqlist.index(genQueueNullStr(sr, sf))][mqlist.index(parseQueue(oq))] = sr_adj_value
                        addDegree(dictindegree, section, parseQueue(oq))
                        addDegree(dictoutdegree, section, genQueueNullStr(sr, sf))

    return dictmat,dictindegree,dictoutdegree

def traceRouteDict(mqdictset, dictmat, dictindegree, dictoutdegree, xadict):
    print "####----- %-20s ------####" % "traceRoute"
    for k,v in mqdictset.iteritems():
        startpoints = v - set(dictindegree[k])
        endpoints = v - set(dictoutdegree[k])
        for s in startpoints:
            for e in endpoints:
                visit = [False for i in range(len(v))]
                path = []
                schAllPath(s, e, visit, path, list(v), dictmat[k], k, xadict)


def printPath(path,k,xadict):
    xahead = ""
    if k in xadict and path[0] in xadict[k]:
        xahead = xadict[k][path[0]]

    print k, "begin<< brief:{",
    if xahead != "":
        print xahead, "->",
    if len(path) % 2 == 1:
        for i in range(len(path)):
            if i % 2 == 0:
                print path[i],
                if i < len(path) - 1:
                    print "->",

    print "} detail:",
    if xahead != "":
        print xahead, "->",
    print path, ">>end"


def schAllPath(v, t, visit, path, mqlist, matrix, k, xadict):
    if visit[mqlist.index(v)]:
        return
    path.append(v)

    if v == t:
        printPath(path, k, xadict)

    else:
        visit[mqlist.index(v)] = True
        for i in range(len(mqlist)):
            if matrix[mqlist.index(v)][i] != "" and not visit[i]:
                path.append(matrix[mqlist.index(v)][i])
                schAllPath(mqlist[i], t, visit, path, mqlist, matrix, k, xadict)
                path.pop()
                path.pop()
        visit[mqlist.index(v)] = False

def checkNoBeUsedQueue(mqsetdef, mqsetuse):
    print "####----- %-20s ------####" % "checkNoBeUsedQueue"
    for k,v in mqsetdef.iteritems():
        ret = mqsetdef[k] - mqsetuse[k]
        if len(ret) > 0:
            print k, "queue defined but no be used:", ret

if __name__  == "__main__":
    try:
        if len(sys.argv[1:]) > 0 and sys.argv[1] != "all":
            needToDealList = sys.argv[1:]
        else:
            needToDealList = ["all",]

        checkServiceId()
        #定义的queue队列
        mqdefset = checkQueueId()

        #在service中使用到的queue队列
        mqdictset = findAllMsgQueueInServices()
        
        checkNoBeUsedQueue(mqdefset, mqdictset)
        dictmat,dictindegree,dictoutdegree = getSrvAdj(mqdictset)

        xadict = parseXa()
        print xadict
#        print dictmat
#        print dictindegree
#        print dictoutdegree

        traceRouteDict(mqdictset, dictmat,dictindegree,dictoutdegree, xadict)
    except BaseException,e:
        print e

