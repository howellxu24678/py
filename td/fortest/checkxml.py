
from lxml import etree
import  os
xml_file_name = os.path.join(os.getcwd(), "maServer.xml")
doc = etree.parse(xml_file_name)
root = doc.getroot()

queueindegree = {}
queueoutdegree = {}
msgqueueset = set()
sr_adj = {}

def checkServiceId():
    idset = set()
    for s in root.getiterator('services'):
        for sr in s.getiterator("service"):
            sid = s.getparent().tag + ":" + sr.get("id")
            print "id", sid
            if sid in idset:
                print "error!!! services name:", sr.get("name"), "id:", sid, "is duplicated"
                return
            else:
                idset.add(sid)

def checkQueueId():
    idset = set()
    for s in root.getiterator('queues'):
        for sr in s.getiterator("msgqueueset"):
            sid = s.getparent().tag + ":" + sr.get("id")
            print "id", sid
            if sid in idset:
                print "error!!! msgqueueset name:", sr.get("name"), "id:", sid, "is duplicated"
                return
            else:
                idset.add(sid)

# def traceQueue():
#
#     for s in root.getiterator('services'):
#         for sr in s.getiterator("service"):
#             for sf in sr.getiterator("svcfunc"):
#                 if not (sf.get("inqueue") is None or sf.get("inqueue") == ""):
#                     for inq in sf.get("inqueue").split(','):
#                         qindex = s.getparent().tag + ":" +  str(int(inq))
#                         if qindex in queueoutdegree:
#                             queueoutdegree[qindex] += 1
#                         else:
#                             queueoutdegree[qindex] = 1
#                 if not (sf.get("outqueue") is None or sf.get("outqueue") == ""):
#                     for outq in sf.get("outqueue").split(','):
#                         qindex = s.getparent().tag + ":" + str(int(outq))
#                         if qindex in queueindegree:
#                             queueindegree[qindex] += 1
#                         else:
#                             queueindegree[qindex] = 1
#                 if not (sf.get("inqueue") is None or sf.get("inqueue") == "") or \
#                         not (sf.get("outqueue") is None or sf.get("outqueue") == ""):
#                     print "parent", s.getparent().tag, "id", sr.get("id"), "inqueue:", sf.get("inqueue"), "outqueue:", sf.get("outqueue")


def findAllMsgQueue():
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
                        msgqueueset.add(iqindex)

                        if iqindex in queueoutdegree:
                            queueoutdegree[iqindex] += 1
                        else:
                            queueoutdegree[iqindex] = 1

                if not (sf.get("outqueue") is None or sf.get("outqueue") == ""):
                    outqueuelist = sf.get("outqueue").split(',')
                    for oq in outqueuelist:
                        oqstr = str(int(oq))
                        oqindex = s.getparent().tag + ":" + oqstr
                        msgqueueset.add(oqindex)
                        if oqindex in queueindegree:
                            queueindegree[oqindex] += 1
                        else:
                            queueindegree[oqindex] = 1

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
                    print "parent", s.getparent().tag, "id", sr.get("id"), "inqueue:", sf.get("inqueue"), "outqueue:", sf.get("outqueue")


def traceQueue():
    #入度为0或者在sr_adj中in为空的应为起点
    startpoint = msgqueueset - set(queueindegree)
    for s in startpoint:
        pass

checkServiceId()
checkQueueId()
#traceQueue()
findAllMsgQueue()
print msgqueueset

print "queueindegree"
for (k,v) in queueindegree.items():
    print "k",k,"v", v

print "queueoutdegree"
for (k,v) in queueoutdegree.items():
    print "k",k,"v", v

print sr_adj


# for s in root.getiterator('services'):
#     for sr in s.iterchildren():
#         print "parent:", s.getparent().tag, "service name", sr.get("name"), "id", sr.get("id")

# for article in root:
#     for field in article:
#         if field.tag == 'gtu':
#             for gtc in field:
#                 if gtc.tag == 'queues':
#                     for mq in gtc:
#                         if mq.tag == 'msgqueueset':
#                             print "mq name", mq.get("name"), "id", mq.get("id")