#-*- coding: UTF-8 -*-
from lxml import etree
import  os
import  sys
xml_file_name = os.path.join(os.getcwd(), "maServer.xml")
doc = etree.parse(xml_file_name)
root = doc.getroot()

qindegree = {}
qoutdegree = {}
mqset = set()
mqlist = []
matrix = []
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

def genReplaceNullStr(s, sr, sf):
    '''
    当队列编号为空时，根据上下文生成一个队列编号，便于后续处理和定位
    :param s:
    :param sr:
    :param sf:
    :return:
    '''
    return s.getparent().tag + ":" + sr.get("id") + "_" + sf.get("id")

def genAdjValue(s, sr, sf):
    return s.getparent().tag + " srvid:" + \
           sr.get("id") + "_" + "funcid:" + \
           sf.get("id") + "_" + "clsid:" + \
           sf.get("clsid")

def addIndegree(node):
    '''
    给节点添加入度
    :param node:
    :return:
    '''
    if node in qindegree:
        qindegree[node] += 1
    else:
        qindegree[node] = 1

def addOutdegree(node):
    '''
    给节点添加出度
    :param node:
    :return:
    '''
    if node in qoutdegree:
        qoutdegree[node] += 1
    else:
        qoutdegree[node] = 1

def isNeedToDeal(s):
    if "all" in needToDealList:
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
    idset = set()
    for s in root.getiterator('services'):
        for sr in s.getiterator("service"):
            if not isNeedToDeal(s):
                continue
            sid = s.getparent().tag + ":" + sr.get("id")
            print "id", sid
            if sid in idset:
                print ("error!!! services name:", sr.get("name"), "id:", sid, "is duplicated")
                return
            else:
                idset.add(sid)

def checkQueueId():
    '''
    校验QueueId 是否有重复，允许不同的parent下的QueueId重复
    :return:
    '''
    print "checkQueueId"
    idset = set()
    for s in root.getiterator('queues'):
        for sr in s.getiterator("mqset"):
            if not isNeedToDeal(s):
                continue
            sid = s.getparent().tag + ":" + sr.get("id")
            print ("id", sid)
            if sid in idset:
                print ("error!!! mqset name:", sr.get("name"), "id:", sid, "is duplicated")
                return
            else:
                idset.add(sid)

def findAllMsgQueueSetAndDegree():
    '''
    获得所有节点的集合及其入度出度
    :return:
    '''
    for s in root.getiterator('services'):
        for sr in s.getiterator("service"):
            for sf in sr.getiterator("svcfunc"):
                if not isNeedToDeal(s):
                    continue
                if sf.get("inqueue") != "":
                    for q in sf.get("inqueue").split(','):
                        mqset.add(s.getparent().tag + ":" + StdInt2Str(q))
                if sf.get("outqueue") != "":
                    for q in sf.get("outqueue").split(','):
                        mqset.add(s.getparent().tag + ":" + StdInt2Str(q))

                if sf.get("inqueue") == "" or sf.get("outqueue") == "":
                    mqset.add(genReplaceNullStr(s, sr, sf))



def getSrvAdj():
    '''
    生成邻接表
    :return:
    '''
    mat = [["" for i in range(len(mqlist))] for j in range(len(mqlist))]
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
                if len(inqueuelist) > 0 and len(outqueuelist) > 0:
                    for iq in inqueuelist:
                        for oq in outqueuelist:
                            iqindex = s.getparent().tag + ":" + StdInt2Str(iq)
                            oqindex = s.getparent().tag + ":" + StdInt2Str(oq)
                            mat[mqlist.index(iqindex)][mqlist.index(oqindex)] = sr_adj_value
                            addIndegree(oqindex)
                            addOutdegree(iqindex)

                if len(inqueuelist) > 0 and len(outqueuelist) == 0:
                    for iq in inqueuelist:
                        iqindex = s.getparent().tag + ":" + StdInt2Str(iq)
                        mat[mqlist.index(iqindex)][mqlist.index(genReplaceNullStr(s, sr, sf))] = sr_adj_value
                        addIndegree(genReplaceNullStr(s, sr, sf))
                        addOutdegree(iqindex)

                if len(inqueuelist) == 0 and len(outqueuelist) > 0:
                    for oq in outqueuelist:
                        oqindex = s.getparent().tag + ":" + StdInt2Str(oq)
                        mat[mqlist.index(genReplaceNullStr(s, sr, sf))][mqlist.index(oqindex)] = sr_adj_value
                        addIndegree(oqindex)
                        addOutdegree(genReplaceNullStr(s, sr, sf))
    return mat

def isEnd(node, visit):
    for i in range(len(mqlist)):
        if matrix[mqlist.index(node)][i] != "" and not visit[i]:
            return False
    return  True


def traceRoute():
    print "traceRoute"
    startpoints = mqset - set(qindegree)
    endpoints = mqset - set(qoutdegree)

    print "startpoints:", startpoints
    print "endpoints", endpoints
    for s in startpoints:
        for e in endpoints:
            visit = [False for i in range(len(mqlist))]
            path = []
            schAllPath(s, e, visit, path)

def schAllPath(v, t, visit, path):
    if visit[mqlist.index(v)]:
        return
    path.append(v)

    if v == t:
        print "begin<<", path, ">>end"
    else:
        visit[mqlist.index(v)] = True
        for i in range(len(mqlist)):
            if matrix[mqlist.index(v)][i] != "" and not visit[i]:
                path.append(matrix[mqlist.index(v)][i])
                schAllPath(mqlist[i], t, visit, path)
        visit[mqlist.index(v)] = False


if __name__  == "__main__":

    if len(sys.argv[1:]) > 0 and sys.argv[1] != "all":
        needToDealList = sys.argv[1:]
    else:
        needToDealList = ["all",]

    checkServiceId()
    checkQueueId()
    #traceRoute()
    findAllMsgQueueSetAndDegree()
    mqlist = list(mqset)
    #print mqset
    #print mqlist
    matrix = getSrvAdj()
    #print matrix
    traceRoute()

