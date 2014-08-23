#!/usr/bin/env python
# server02.py

from __future__ import print_function
import socket
import select
#import portconfig as cfg
import Queue
from threading import Thread
from time import sleep
from random import randint
import sys
from xml.etree import ElementTree as ET
import datetime
from updReqTbl2 import addReq2Tbl

from cfg_workDir import workDir     # /home/sumit/mbsSkyward/
from cfg_serverAddr import serverAddr

host = (serverAddr['host'])
port = (serverAddr['port'])

punchoutMsgDir=workDir + 'msgPunchout/'
orderMsgDir=workDir + 'msgOrder/'
resp400MsgDir=workDir + 'msgResp400/'
templatesDir=workDir + 'templates/'
tmpDir = workDir + 'tmp/'

pOutRespMsg_b0 = {'b001': '<?xml version="1.0" ?>\n',
                  'b002': '<!DOCTYPE cXML SYSTEM "http://xml.cxml.org/schemas/cXML/1.1.007/cXML.dtd">\n',
                  'b003': '<cXML version="1.1.007" payloadID="',
                  'b004': 'payload_id',                           #format: 2004-12-10T08:30:16@@marshfieldbook.com
                  'b005': '" timestamp="',
                  'b006': 'time_stamp',                           #format: 2004-12-10T08:30:18
                  'b007': '">\n',
                  'b008': '<Response>\n',
                  'b009': '<Status code="200" text="success"></Status>\n',
                  'b010': '<PunchOutSetupResponse>\n',
                  'b011': '<StartPage><URL>',
                  'b012': 'http://orders.marshfieldbook.com/Marshfield/app',
                  'b013': '</URL></StartPage>\n',
                  'b012': '</PunchOutSetupResponse>\n',
                  'b013': '</Response>\n',
                  'b014': '</cXML>'
                 }

'''
<?xml version="1.0"?>
<!DOCTYPE cXML SYSTEM "http://xml.cxml.org/schemas/cXML/1.1.007/cXML.dtd">
<cXML payloadID="2004-12-10T08:30:16" timestamp="2004-12-10T08:30:18">
<Response>
<Status code="200" text="success"></Status>
<PunchOutSetupResponse>
<StartPage><URL>http://orders.marshfieldbook.com/Marshfield/app</URL></StartPage>
</PunchOutSetupResponse>
</Response>
</cXML>
'''


class ProcessThread(Thread):
    def __init__(self):
        super(ProcessThread, self).__init__()
        self.running = True
        self.q = Queue.Queue()

    def add(self, data):
        self.q.put(data)

    def stop(self):
        self.running = False

    def run(self):
        q = self.q
        while self.running:
            try:
                # block for 1 second only:
                value = q.get(block=True, timeout=1)
                process(value)
            except Queue.Empty:
                #sys.stdout.write('.')
                sys.stdout.flush()
        #
        if not q.empty():
            print("Elements left in the queue:")
            while not q.empty():
                print(q.get())

t = ProcessThread()
t.start()

def process(value):
    """
    Implement this. Do something useful with the received data.
    """
    print(value)
    sleep(randint(1,9))    # emulating processing time

def parseXMLreq(data):
    root = ET.fromstring(data)
    #print(root.tag)
    req_type = None
    #root[1][0] <PunchOutSetupRequest> or <OrderRequest>
    for PunchOutSetupRequest in root[1][0].iter('PunchOutSetupRequest'):
        req_type = 'PunchOutSetupRequest'
        print('PunchOutSetupRequest', PunchOutSetupRequest.attrib)

    #for BuyerCookie in root[1][0].iter('BuyerCookie'):
        #buyerCookie = BuyerCookie.text
        #print('BuyerCookie', BuyerCookie.text)

    for OrderRequestHeader in root[1][0].iter('OrderRequestHeader'):
        req_type = 'OrderRequest'
        print('OrderRequestHeader', OrderRequestHeader.attrib)

    return(req_type)

'''
#root[0][0] <From>
    for Credential in root[0][0].iter('Credential'):
        print('From Credential', Credential.attrib)
    for Identity in root[0][0].iter('Identity'):
        print('From Identity', Identity.text)

#root[0][1] <To>
    for Credential in root[0][1].iter('Credential'):
        print('To Credential', Credential.attrib)
    for Identity in root[0][1].iter('Identity'):
        print('To Identity', Identity.text)

#root[0][2] <Sender>
    for Credential in root[0][2].iter('Credential'):
        print('Sender Credential', Credential.attrib)
    for Identity in root[0][2].iter('Identity'):
        print('Sender Identity', Identity.text)
    for SharedSecret in root[0][2].iter('SharedSecret'):
        print('Sender SharedSecret', SharedSecret.text)
    for UserAgent in root[0][2].iter('UserAgent'):
        print('Sender UserAgent', UserAgent.text)
'''



def getSeqNo():
    reqSeqNoFile = 'reqSeqNo'
    reqSeqNo = open(reqSeqNoFile, 'r')
    seq_no = reqSeqNo.read()
    reqSeqNo.close()
    seq_no_int = int(seq_no)
    seq_no_int += 1
    reqSeqNo = open(reqSeqNoFile, 'w')
    #print("seq no: %8d" % seq_no_int)
    new_seq_no = ("%06d" % seq_no_int)
    #new_seq_no = "{0:0>6}".format(seq_no_int)
    reqSeqNo.write(new_seq_no)
    reqSeqNo.close()
    return new_seq_no

def main():
    s = socket.socket()         # Create a socket object

    #host = socket.gethostname() # Get local machine name
    #host = '192.168.51.231'

    #print("Host ", host)
    #port = cfg.PORT                # Reserve a port for your service.
    #port = 42009
    try:
        s.bind((host, port))        # Bind to the port
        #print "Listening on port {p}...".format(p=port)
        print("Listening on Host: %s  port: %s" % (host, port))

    except Exception as err_msg:
        print(err_msg)

        #s.shutdown(socket.SHUT_RDWR)
        #s.close()

        cleanup()
        sys.exit(9)


    curl_hdr = "POST / HTTP/1.1 \
           User-Agent: curl/7.34.0 \
           Host: orders.marshfieldbook.com:42009 \
           Accept: */* \
           Content-Type: text/xml \
           Content-Length: 1280 \
           Expect: "

    s.listen(5)                 # Now wait for client connection.
    while True:
        try:
            client, addr = s.accept()
            now = datetime.datetime.now()
            print("Got a connection from %s" % str(addr), now.strftime("%Y-%m-%d %H:%M"))

            ready = select.select([client,],[], [],2)
            if ready[0]:
                data = client.recv(2048)
                print('received a Request p1')
                #print(data)
                recvReqFile = tmpDir + 'requestDoc_p1' + '.xml'
                recvReq = open(recvReqFile, 'w')
                recvReq.write(data)
                recvReq.close()
                #client.send('HTTP 1.1 100 CONTINUE')

                data = client.recv(4096)
                print('received a Request p2')
                #print(data)
                recvReqFile = tmpDir + 'requestDoc_p2' + '.xml'
                recvReq = open(recvReqFile, 'w')
                recvReq.write(data)
                recvReq.close()
                #client.send('HTTP 1.1 200 OK')


                try:
                    req_type = parseXMLreq(data)
                except Exception as err_msg:
                    print(err_msg)
                    cleanup()
                    sys.exit(9)


                resp_payloadID = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S@marshfieldbook.com")
                resp_timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                if req_type == 'PunchOutSetupRequest':

                    print('process PunchOutSetupRequest')
                    file_seq_no = getSeqNo()
                    pOutReqFile = punchoutMsgDir + 'PunchOutSetupRequest' + file_seq_no + '.xml'
                    pOutReq = open(pOutReqFile, 'w')
                    #pOutReq.write(t.add(data))
                    pOutReq.write(data)
                    pOutReq.close()

                    buyerCookie = addReq2Tbl(data)
                    startPageURL = 'http://orders.marshfieldbook.com/Marshfield/app' + '?bc=' + buyerCookie

                    #resp_tree = ET.parse(templatesDir + 'PunchOutSetupResponse.xml')
                    #resp_root = resp_tree.getroot()
                    #for cXML in resp_root.iter('cXML'):
                    #    cXML.set('payloadID', resp_payloadID)
                    #    cXML.set('timestamp', resp_timestamp)
                    #for URL in resp_root.iter(tag = 'URL'):
                    #    #print(URL.text)
                    #    URL.text = startPageURL
                    #resp_tree.write(punchoutMsgDir + 'PunchOutSetupResponse' + file_seq_no + '.xml')

                    pOutRespFile = punchoutMsgDir + 'PunchOutSetupResponse' + file_seq_no + '.xml'
                    pOutRespMsg = open(pOutRespFile, 'w')

                    pOutRespMsg_b0['b004'] = resp_payloadID;
                    pOutRespMsg_b0['b006'] = resp_timestamp;
                    pOutRespMsg_b0['b012'] = startPageURL;

                    for key in sorted(pOutRespMsg_b0.iterkeys()):
                        #print("%s" % (pOutRespMsg_b0[key]))
                        pOutRespMsg.write(pOutRespMsg_b0[key])

                    pOutRespMsg.close()

                    pOutRespMsg = open(pOutRespFile, 'r')
                    pOutRespDoc = pOutRespMsg.read()
                    pOutRespMsg.close()

                    #client.send('HTTP 1.1 200 OK')
                    client.send(pOutRespDoc)
                    client.close()

                elif req_type == 'OrderRequest':

                    print('process OrderRequest')
                    file_seq_no = getSeqNo()
                    orderReqFile = orderMsgDir + 'OrderRequest' + file_seq_no + '.xml'
                    orderReq = open(orderReqFile, 'w')
                    #pOutReq.write(t.add(data))
                    orderReq.write(data)
                    orderReq.close()

                    resp_tree = ET.parse(templatesDir + 'OrderResponse.xml')
                    resp_root = resp_tree.getroot()
                    for cXML in resp_root.iter('cXML'):
                        cXML.set('payloadID', resp_payloadID)
                        cXML.set('timestamp', resp_timestamp)
                        resp_tree.write(orderMsgDir + 'OrderResponse' + file_seq_no + '.xml')

                    orderRespFile = orderMsgDir + 'OrderResponse' + file_seq_no + '.xml'
                    orderResp = open(orderRespFile, 'r')
                    orderRespDoc = orderResp.read()
                    client.send(orderRespDoc)
                    client.close()

                else:
                    print('Invalid req type value: ', req_type)
                    file_seq_no = getSeqNo()
                    resp_tree = ET.parse(templatesDir +  'ReqResponse400.xml')
                    resp_root = resp_tree.getroot()
                    for cXML in resp_root.iter('cXML'):
                        cXML.set('payloadID', resp_payloadID)
                        cXML.set('timestamp', resp_timestamp)
                        resp_tree.write(resp400MsgDir + 'ReqResponse400' + file_seq_no + '.xml')

                    reqRespFile = resp400MsgDir + 'ReqResponse400' + file_seq_no + '.xml'
                    reqResp = open(reqRespFile, 'r')
                    reqRespDoc = reqResp.read()
                    client.send(reqRespDoc)
                    client.close()


        except KeyboardInterrupt:
            print
            print("Stop.")
            break
        except socket.error, msg:
            print("Socket error! %s" % msg)
            break
    #
    cleanup()

def cleanup():
    print('Cleaning up')
    t.stop()
    t.join()


if __name__ == "__main__":
    main()
