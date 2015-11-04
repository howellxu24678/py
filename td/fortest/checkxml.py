#-*- coding: UTF-8 -*-
from lxml import etree
import  os
import  sys
xml_file_name = os.path.join(os.getcwd(), "test.xml")
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

# def genReplaceNullStr(s, sr, sf):
#     '''
#     当队列编号为空时，根据上下文生成一个队列编号，便于后续处理和定位
#     :param s:
#     :param sr:
#     :param sf:
#     :return:
#     '''
#     return s.getparent().tag + ":" + sr.get("id") + "_" + sf.get("id")

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
    print "checkServiceId"
    idictset = {}
    for s in root.getiterator('services'):
        for sr in s.getiterator("service"):
            if not isNeedToDeal(s):
                continue
            sid = sr.get("id")
            if idictset.has_key(s.getparent().tag):
                if sid in idictset[s.getparent().tag]:
                    print "error!!!", s.getparent().tag, "services name:",sr.get("name"), "id:", sid, "is duplicated"
                    return
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
    print "checkQueueId"
    idictset = {}
    for s in root.getiterator('queues'):
        for sr in s.getiterator("msgqueue"):
            if not isNeedToDeal(s):
                continue
            sid = sr.get("id")
            if idictset.has_key(s.getparent().tag):
                if sid in idictset[s.getparent().tag]:
                    print "error!!!", s.getparent().tag, "msgqueue name:",sr.get("name"), "id:", sid, "is duplicated"
                    return
                else:
                    idictset[s.getparent().tag].add(sid)
            else:
                idset = set()
                idset.add(sid)
                idictset[s.getparent().tag] = idset

    print "queueId:", idictset

def mqDictSetAdd(mqdictset, s, q):
    if mqdictset.has_key(s.getparent().tag):
        mqdictset[s.getparent().tag].add(StdInt2Str(q))
    else:
        mqset = set()
        mqset.add(StdInt2Str(q))
        mqdictset[s.getparent().tag] = mqset

def findAllMsgQueueInServices():
    '''
    获得所有节点的集合及其入度出度
    :return:
    '''
    mqdictset = {}

    for s in root.getiterator('services'):
        for sr in s.getiterator("service"):
            for sf in sr.getiterator("svcfunc"):
                if not isNeedToDeal(s):
                    continue
                if sf.get("inqueue") != "":
                    for q in sf.get("inqueue").split(','):
                        mqDictSetAdd(mqdictset, s, q)
                if sf.get("outqueue") != "":
                    for q in sf.get("outqueue").split(','):
                        mqDictSetAdd(mqdictset, s, q)

                if sf.get("inqueue") == "" or sf.get("outqueue") == "":
                    mqDictSetAdd(mqdictset, s, genQueueNullStr(sr, sf))

    print "findAllMsgQueueInServices mqdictset", mqdictset
    return mqdictset

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
                            dictmat[s.getparent().tag][mqlist.index(StdInt2Str(iq))][mqlist.index(StdInt2Str(oq))] = sr_adj_value
                            addDegree(dictindegree, section, StdInt2Str(oq))
                            addDegree(dictoutdegree, section, StdInt2Str(iq))

                if len(inqueuelist) > 0 and len(outqueuelist) == 0:
                    for iq in inqueuelist:
                        dictmat[s.getparent().tag][mqlist.index(StdInt2Str(iq))][mqlist.index(genQueueNullStr(sr, sf))] = sr_adj_value
                        addDegree(dictindegree, section, genQueueNullStr(sr, sf))
                        addDegree(dictoutdegree, section, StdInt2Str(iq))


                if len(inqueuelist) == 0 and len(outqueuelist) > 0:
                    for oq in outqueuelist:
                        dictmat[s.getparent().tag][mqlist.index(genQueueNullStr(sr, sf))][mqlist.index(StdInt2Str(oq))] = sr_adj_value
                        addDegree(dictindegree, section, StdInt2Str(oq))
                        addDegree(dictoutdegree, section, genQueueNullStr(sr, sf))

    return dictmat,dictindegree,dictoutdegree

def traceRouteDict(mqdictset, dictmat,dictindegree,dictoutdegree):
    for k,v in mqdictset.iteritems():
        startpoints = v - set(dictindegree[k])
        endpoints = v - set(dictoutdegree[k])
        for s in startpoints:
            for e in endpoints:
                visit = [False for i in range(len(v))]
                path = []
                schAllPath(s, e, visit, path, list(v), dictmat[k], k)


def printPath(path,k):
    print k, "begin<< brief:{",

    if len(path) % 2 == 1:
        for i in range(len(path)):
            if i % 2 == 0:
                print path[i],
                if i < len(path) - 1:
                    print "->",

    print "} detail:", path, ">>end"


def schAllPath(v, t, visit, path, mqlist, matrix, k):
    if visit[mqlist.index(v)]:
        return
    path.append(v)

    if v == t:
        printPath(path, k)

    else:
        visit[mqlist.index(v)] = True
        for i in range(len(mqlist)):
            if matrix[mqlist.index(v)][i] != "" and not visit[i]:
                path.append(matrix[mqlist.index(v)][i])
                schAllPath(mqlist[i], t, visit, path, mqlist, matrix, k)
                path.pop()
                path.pop()
        visit[mqlist.index(v)] = False



if __name__  == "__main__":

    if len(sys.argv[1:]) > 0 and sys.argv[1] != "all":
        needToDealList = sys.argv[1:]
    else:
        needToDealList = ["all",]

    checkServiceId()
    checkQueueId()
    #print findAllMsgQueueInServices()
    #mqlist = list(mqdictset)
    mqdictset = findAllMsgQueueInServices()
    dictmat,dictindegree,dictoutdegree = getSrvAdj(mqdictset)

    print dictmat
    print dictindegree
    print dictoutdegree

    traceRouteDict(mqdictset, dictmat,dictindegree,dictoutdegree)

