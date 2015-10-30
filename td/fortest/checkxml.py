
from lxml import etree
xml_file_name = 'F:\\code\\git\\py\\td\\fortest\\maServer.xml'
doc = etree.parse(xml_file_name)
root = doc.getroot()

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
        for sr in s.getiterator("msgqueue"):
            sid = s.getparent().tag + ":" + sr.get("id")
            print "id", sid
            if sid in idset:
                print "error!!! msgqueue name:", sr.get("name"), "id:", sid, "is duplicated"
                return
            else:
                idset.add(sid)

def tracequeue():
    queueindegree = {}
    queueoutdegree = {}
    for s in root.getiterator('services'):
        for sr in s.getiterator("service"):
            for sf in sr.getiterator("svcfunc"):
                if not (sf.get("inqueue") is None or sf.get("inqueue") == ""):
                    for inq in sf.get("inqueue").split(','):
                        qindex = s.getparent().tag + inq
                        if qindex in queueoutdegree:
                            queueoutdegree[qindex] += 1
                        else:
                            queueoutdegree[qindex] = 1
                if not (sf.get("outqueue") is None or sf.get("outqueue") == ""):
                    for outq in sf.get("outqueue").split(','):
                        qindex = s.getparent().tag + outq
                        if qindex in queueindegree:
                            queueindegree[qindex] += 1
                        else:
                            queueindegree[qindex] = 1
                if not (sf.get("inqueue") is None or sf.get("inqueue") == "") or not (sf.get("outqueue") is None or sf.get("outqueue") == ""):
                    print "parent", s.getparent().tag, "id", sr.get("id"), "inqueue:", sf.get("inqueue"), "outqueue:", sf.get("outqueue")

    print "queueindegree"
    for (k,v) in queueindegree.items():
        print "k",k,"v", v

    print "queueoutdegree"
    for (k,v) in queueoutdegree.items():
        print "k",k,"v", v


checkServiceId()
checkQueueId()
tracequeue()


# for s in root.getiterator('services'):
#     for sr in s.iterchildren():
#         print "parent:", s.getparent().tag, "service name", sr.get("name"), "id", sr.get("id")

# for article in root:
#     for field in article:
#         if field.tag == 'gtu':
#             for gtc in field:
#                 if gtc.tag == 'queues':
#                     for mq in gtc:
#                         if mq.tag == 'msgqueue':
#                             print "mq name", mq.get("name"), "id", mq.get("id")