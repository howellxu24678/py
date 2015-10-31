#-*- coding: UTF-8 -*-
from __future__ import print_function
from lxml import etree
import  os
xml_file_name = os.path.join(os.getcwd(), "test.xml")
doc = etree.parse(xml_file_name)
root = doc.getroot()

qindegree = {}
qoutdegree = {}
mqset = set()
mqlist = []
sr_adj = {}
global matrix
matrix = []

def checkServiceId():
    idset = set()
    for s in root.getiterator('services'):
        for sr in s.getiterator("service"):
            sid = s.getparent().tag + ":" + sr.get("id")
            print ("id", sid)
            if sid in idset:
                print ("error!!! services name:", sr.get("name"), "id:", sid, "is duplicated")
                return
            else:
                idset.add(sid)

def checkQueueId():
    idset = set()
    for s in root.getiterator('queues'):
        for sr in s.getiterator("mqset"):
            sid = s.getparent().tag + ":" + sr.get("id")
            print ("id", sid)
            if sid in idset:
                print ("error!!! mqset name:", sr.get("name"), "id:", sid, "is duplicated")
                return
            else:
                idset.add(sid)

def findAllMsgQueueDegree():
    cnt = 0
    for s in root.getiterator('services'):
        for sr in s.getiterator("service"):
            for sf in sr.getiterator("svcfunc"):
                inqueuelist=[]
                outqueuelist=[]
                if not (sf.get("inqueue") is None or sf.get("inqueue") == ""):
                    inqueuelist = sf.get("inqueue").split(',')
                    for iq in inqueuelist:
                        iqstr = str(int(iq))
                        iqindex = s.getparent().tag + ":" + iqstr
                        mqset.add(iqindex)

                        if iqindex in qoutdegree:
                            qoutdegree[iqindex] += 1
                        else:
                            qoutdegree[iqindex] = 1

                if not (sf.get("outqueue") is None or sf.get("outqueue") == ""):
                    outqueuelist = sf.get("outqueue").split(',')
                    for oq in outqueuelist:
                        oqstr = str(int(oq))
                        oqindex = s.getparent().tag + ":" + oqstr
                        mqset.add(oqindex)
                        if oqindex in qindegree:
                            qindegree[oqindex] += 1
                        else:
                            qindegree[oqindex] = 1
                if sf.get("inqueue") == "" or sf.get("outqueue") == "":
                     cnt += 1
                     mqset.add("*" + str(cnt))

                sr_adj_value = sr.get("id") + "_" + sf.get("id") + "_" + sf.get("clsid")
                if len(inqueuelist) > 0 and len(outqueuelist) > 0:
                    for iq in inqueuelist:
                        for oq in outqueuelist:
                            iqstr = str(int(iq))
                            iqindex = s.getparent().tag + ":" + iqstr
                            oqstr = str(int(oq))
                            oqindex = s.getparent().tag + ":" + oqstr
                            sr_adj[iqindex + "," + oqindex] = sr_adj_value

                if len(inqueuelist) > 0 and len(outqueuelist) == 0:
                    for iq in inqueuelist:
                        iqstr = str(int(iq))
                        iqindex = s.getparent().tag + ":" + iqstr
                        sr_adj[iqindex + ","] = sr_adj_value

                if len(inqueuelist) == 0 and len(outqueuelist) > 0:
                    for oq in outqueuelist:
                        oqstr = str(int(oq))
                        oqindex = s.getparent().tag + ":" + oqstr
                        sr_adj["," + oqindex] = sr_adj_value

                if not (sf.get("inqueue") is None or sf.get("inqueue") == "") or \
                        not (sf.get("outqueue") is None or sf.get("outqueue") == ""):
                    print ("parent", s.getparent().tag, "id", sr.get("id"), "inqueue:", sf.get("inqueue"), "outqueue:", sf.get("outqueue"))

def getSrvAdj():
    mat = [["" for i in range(len(mqlist))] for j in range(len(mqlist))]
    cnt = 0
    for s in root.getiterator('services'):
        for sr in s.getiterator("service"):
            for sf in sr.getiterator("svcfunc"):
                inqueuelist=[]
                outqueuelist=[]
                if not (sf.get("inqueue") is None or sf.get("inqueue") == ""):
                    inqueuelist = sf.get("inqueue").split(',')
                if not (sf.get("outqueue") is None or sf.get("outqueue") == ""):
                    outqueuelist = sf.get("outqueue").split(',')
                sr_adj_value = s.getparent().tag + " srvid:" + sr.get("id") + "_" + "funcid:" + sf.get("id") + "_" + "clsid:" + sf.get("clsid")
                if len(inqueuelist) > 0 and len(outqueuelist) > 0:
                    for iq in inqueuelist:
                        for oq in outqueuelist:
                            iqstr = str(int(iq))
                            iqindex = s.getparent().tag + ":" + iqstr
                            oqstr = str(int(oq))
                            oqindex = s.getparent().tag + ":" + oqstr
                            mat[mqlist.index(iqindex)][mqlist.index(oqindex)] = sr_adj_value

                if len(inqueuelist) > 0 and len(outqueuelist) == 0:
                    for iq in inqueuelist:
                        cnt += 1
                        iqstr = str(int(iq))
                        iqindex = s.getparent().tag + ":" + iqstr
                        mat[mqlist.index(iqindex)][mqlist.index("*" + str(cnt))] = sr_adj_value

                if len(inqueuelist) == 0 and len(outqueuelist) > 0:
                    for oq in outqueuelist:
                        cnt += 1
                        oqstr = str(int(oq))
                        oqindex = s.getparent().tag + ":" + oqstr
                        mat[mqlist.index("*" + str(cnt))][mqlist.index(oqindex)] = sr_adj_value
    return mat

def dfs(node, visit):
    print (node,end = "")
    visit[mqlist.index(node)] = True
    for i in range(len(mqlist)):
        if matrix[mqlist.index(node)][i] != "" and not visit[i]:
            print ("[" + matrix[mqlist.index(node)][i] + "]", "-> ",end = "")
            dfs(mqlist[i],visit)


def traceQueue():
    '''
    入度为0或者在sr_adj中in为空的应为起点
    :return:
    '''
    startnodes = mqset - set(qindegree)
    for s in startnodes:
        print( "begin<<", end = "")
        visit = [False for i in range(len(mqlist))]
        dfs(s, visit)
        print (">>end")




checkServiceId()
checkQueueId()
#traceQueue()
findAllMsgQueueDegree()
mqlist = list(mqset)
# print mqset
print (mqlist)
matrix = getSrvAdj()
print (matrix)
traceQueue()



# print "qindegree"
# for (k,v) in qindegree.items():
#     print "k",k,"v", v
#
# print "qoutdegree"
# for (k,v) in qoutdegree.items():
#     print "k",k,"v", v
#
# print sr_adj