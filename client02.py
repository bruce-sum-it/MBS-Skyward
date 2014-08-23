#!/usr/bin/env python
# client.py

#import config as cfg
import sys
import socket
import argparse

from cfg_serverAddr import serverAddr

host = (serverAddr['host'])
port = (serverAddr['port'])

''' command line args (required):
1 doc_to_send_1 
2 doc_to_send_2 
2 server_ip    
'''
parser = argparse.ArgumentParser()
parser.add_argument("Doc1")
parser.add_argument("Doc2")
parser.add_argument("IP")
#parser.add_argument("DevID")
#parser.add_argument("TrxNo", nargs = '?', default = 0)
#parser.add_argument("Amount", nargs = '?', default = 0)
args = parser.parse_args()

doc_to_send_1 = args.Doc1
doc_to_send_2 = args.Doc2
server_ip = args.IP

reqFileName1 = doc_to_send_1
reqFileName2 = doc_to_send_2
# i.e.'PunchOutSetupRequest.xml' or 'OrderRequest.xml'
try:
    reqFile1 = open(reqFileName1, 'r')
    reqDoc1 = reqFile1.read()
except Exception as msg:
    print(msg, 'XML doc not found')
reqFile1.close()

try:
    reqFile2 = open(reqFileName2, 'r')
    reqDoc2 = reqFile2.read()
except Exception as msg:
    print(msg, 'XML doc not found')
reqFile2.close()

#def main(elems):
def main():
    try:
        #for e in elems:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #host = socket.gethostname()
        #host = '192.168.51.20'
        host = server_ip
        print(host, port)
        client.connect((host, port))
        client.send(reqDoc1)
        print(reqDoc1)
        #data = client.recv(1024)
        #print data
        client.send(reqDoc2)
        print(reqDoc2)
        #data = client.recv(1024)
        #print data
        client.shutdown(socket.SHUT_RDWR)
        client.close()
    except Exception as msg:
        print msg

#########################################################

if __name__ == "__main__":
    #main(sys.argv[1:])
    main()