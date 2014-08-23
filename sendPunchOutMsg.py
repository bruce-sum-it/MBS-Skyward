#!/usr/bin/env python


import json
import decimal
#import psycopg2
#import psycopg2.extras
import os
import subprocess
import sys
import datetime
import mysql.connector
from mysql.connector import errorcode
from xml.etree import ElementTree as ET

from cfg_dbAccess import dbAccess
from cfg_workDir import workDir     # /home/sumit/mbsSkyward/
from cfg_reqDir import reqDir       # /var/lib/tomcat7/webapps/Marshfield/mbsdata/
from cfg_opMode import opMode

reqProcessedDir=reqDir[0:-1] + '_processed'


# PunchOutOrderMessage xml lines/fields:

# xml doc block 0 Header
#pOutOrderMsg_b0 = {'b000': '<FORM=POST ACTION=',
#                   'b001': 'browser_form_post_url',  #browserFormPostURL from pOutReq fmt: &quot;URL_value&quot;
#                   'b002': '>',
#                   'b003': '<input type="hidden" name="cXML-urlencoded" value="&lt;?xml version=&quot;1.0&quot; encoding=&quot;UTF-8&quot;?&gt;&lt;!DOCTYPE cXML SYSTEM &quot;http://xml.cxml.org/schemas/cXML/1.2.019/cXML.dtd&quot;&gt;',
pOutOrderMsg_b0 = {'b001': '<?xml version="1.0" ?>',
                   'b002': '<!DOCTYPE cXML SYSTEM "http://xml.cxml.org/schemas/cXML/1.1.007/cXML.dtd">',
                   'b003': '<cXML version="1.1.007" payloadID="2004-12-10T08:30:16@@marshfieldbook.com" timestamp="2004-12-10T08:30:18">',
#                   'b004': 'payload_id',             # format: 2004-12-10T08:30:16
#                   'b005': '" timestamp="',
#                   'b006': 'time_stamp',             # format: 2004-12-10T08:30:18
#                   'b007': '">\n',
                   }

# xml doc block 1 Header
pOutOrderMsg_b1 = {'b100': '<Header>',
                   'b101': '<From>',
                   'b102': '<Credential domain="NetworkId">',
                   'b103': '<Identity>',
                   'b104': 'login_id',            #fromIdentity  (from pOutReq query)
                   'b105':'</Identity>',
                   'b106': '</Credential>',
                   'b107': '</From>',

                   'b108': '<To>',
                   'b109': '<Credential domain="DUNS">',
                   'b110': '<Identity>',
                   'b111': 'duns_number',         #toIndentity  (from pOutReq query) 023341274 Marshfield
                   'b112':'</Identity>',
                   'b113': '</Credential>',
                   'b114': '</To>',

                   'b115': '<Sender>',
                   'b116': '<Credential domain="NetworkId">',
                   'b117': '<Identity>',
                   'b118': 'login_id',            #senderIdentity  (from pOutReq query)
                   'b119': '</Identity>',
                   'b120': '<SharedSecret>',
                   'b121': 'user_password',       #senderSharedSecret  (from pOutReq query)
                   'b122': '</SharedSecret>',
                   'b123': '</Credential>',
                   'b124': '<UserAgent>PeopleSoft eProcurement</UserAgent>',
                   'b125': '</Sender>',
                   'b126': '</Header>',
                   }


# xml doc block 2 PunchOutOrderMessage
pOutOrderMsg_b2 = {'b200': '<Message deploymentMode="test">',
                   'b201': '<PunchOutOrderMessage>',
                   'b202': '<BuyerCookie>',
                   'b203': 'buyer_cookie',           #buyerCookie  (from pOutReq query)
                   'b204': '</BuyerCookie>',

                   'b205': '<PunchOutOrderMessageHeader operationAllowed="edit">',
                   'b206': '<Total>',
                   'b207': '<Money currency="USD">',
                   'b208': 'order_total',            #
                   'b209': '</Money>',
                   'b210': '</Total>',

                   'b211': '<ShipTo>',
                   'b212': '<Address>',
                   'b213': '<Name xml:lang="en">',
                   'b214': 'cust_name',              #shiptoAddressName  (from pOutReq query)
                   'b215': '</Name>',
                   'b216': '<PostalAddress name=',
                   'b217': 'cust_addr_name',         #postalAddressName
                   'b218': '>',
                   'b219': '<DeliverTo>',
                   'b220': 'cust_attn',              #deliverTo
                   'b221': '</DeliverTo>',
                   'b222': '<Street>',
                   'b223': 'cust_street_addr',       #street
                   'b224': '</Street>',
                   'b225': '<City>',
                   'b226': 'cust_city',              #city
                   'b227': '</City>',
                   'b228': '<State>',
                   'b229': 'cust_state',             #state
                   'b230': '</State>',
                   'b231': '<PostalCode>',
                   'b232': 'cust_zipcode',           #postalCode
                   'b233': '</PostalCode>',
                   'b234': '<Country isoCountryCode="US"/>',
                   'b235': '</PostalAddress>',
                   'b236': '</Address>',
                   'b237': '</ShipTo>',
                   'b238': '</PunchOutOrderMessageHeader>',
                   }


# xml doc block 3 Item
pOutOrderMsg_b3 = {'b300': '<ItemIn quantity=',
                   'b301': 'item_order_qty',
                   'b302': 'lineNumber=',
                   'b303': 'item_line_no',
                   'b304': '>',
                   'b305': '<ItemID>',
                   'b306': '<SupplierPartID>',
                   'b307': 'item_id',
                   'b308': '</SupplierPartID>',
                   #<SupplierPartAuxiliaryID>2214056|40169733</SupplierPartAuxiliaryID>
                   'b309': '</ItemID>',
                   'b310': '<ItemDetail>',
                   'b311': '<UnitPrice>',
                   'b312': '<Money currency="USD">',
                   'b313': 'item_prc',
                   'b314': '</Money>',
                   'b315': '</UnitPrice>',
                   'b316': '<Description xml:lang="en">',
                   'b317': 'item_desc',
                   'b318': '</Description>',
                   'b319': '<UnitOfMeasure>',
                   'b320': 'item_uofm',
                   'b321': '</UnitOfMeasure>',
                   #<3lassification domain="UNSPSC">6010130700</Classification>
                   #<ManufacturerPartID>1820C</ManufacturerPartID>
                   #<ManufacturerName>HYGLOSS PRODUCTS</ManufacturerName>
                   'b322': '</ItemDetail>',
                   'b323': '<Tax/>',
                   'b324': '</ItemIn>',
                   }

# xml doc block 4 end of doc
pOutOrderMsg_b4 = {'b400': '</PunchOutOrderMessage>',
                   'b401': '</Message>',
                   'b402': '</cXML>',
                   }
#                   'b403': '<INPUT TYPE=SUBMIT VALUE=&quot;Proceed&quot;>',
#                   }
#                   'b404': '</FORM>',
#                   }


def getSeqNo():
    orderSeqNoFile = 'orderSeqNo'
    orderSeqNo = open(orderSeqNoFile, 'r')
    seq_no = orderSeqNo.read()
    orderSeqNo.close()
    seq_no_int = int(seq_no)
    seq_no_int += 1
    orderSeqNo = open(orderSeqNoFile, 'w')
    #print("seq no: %8d" % seq_no_int)
    new_seq_no = ("%06d" % seq_no_int)
    #new_seq_no = "{0:0>6}".format(seq_no_int)
    orderSeqNo.write(new_seq_no)
    orderSeqNo.close()
    return new_seq_no

def move_to_processed(fname):
    subprocess.call(''.join(["mv ", reqDir, fname, ' ', reqProcessedDir]),shell=True)

def curl_req(req_file, send_to):
    curl_cmd = 'curl -s -k -H "Content-Type:text/xml"'

    #req_file_path = ''.join([' -d@/export/home/sumit/', req_file])
    req_file_path = ''.join([' -d@', workDir, req_file])

    resp_file =  os.path.splitext(req_file)[0] + '.resp'
    #resp_file_path = ''.join([' -o /export/home/sumit/', resp_file])
    resp_file_path = ''.join([' -o ./', resp_file])

    post_xml_doc_cmd = []
    #post_xml_doc_cmd = ''.join([curl_cmd, req_file, ' ', send_to, ' > ', resp_file])
    post_xml_doc_cmd = ''.join([curl_cmd, req_file_path, resp_file_path, ' ', send_to])

    #print(post_xml_doc_cmd)

    post_xml_doc = subprocess.call(post_xml_doc_cmd, shell=True)

    if post_xml_doc != 0:
        print('post xml doc response: ', post_xml_doc)
        return False
    else:
        return True



def main():

    eof = "N"
    i = 0
    k = 0
    b = 0
    j_count = 0

    try:
        #print(dbAccess)
        cnx = mysql.connector.connect(**dbAccess)
        #print(cnx)

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exists")
        else:
            print(err)
    try:
        cur = cnx.cursor()
    except Exception as msg:
        print('cur assign err', msg)
    #item_cursor = cnx.cursor()
    #pOutReq_cursor = cnx.cursor()


    for mbs_order in os.listdir(reqDir):
        #print(mbs_order)
        #if os.path.splitext(mbs_order)[1] == '.email':
        #print(mbs_order[0:3])
        if mbs_order[0:3] == 'MBS':
            if os.path.getsize(reqDir + '/' + mbs_order) <= 0:
                move_to_processed(mbs_order)
            else:
                print(mbs_order)

                order_no = mbs_order[3: ]

                get_pOutReq = ("select fromIdentity, toIdentity, \
                               senderIdentity, senderSharedSecret, userAgent, \
                               buyerCookie, shiptoAddressName, postalAddressName, \
                               deliverTo, street, city, state, postalCode, country, browserFormPostURL from pOutReq "
                               "where mbsOrderNo = %s")

                #pOutReq_cursor.execute(get_pOutReq, (order_no,))
                cur.execute(get_pOutReq, (order_no,))

                for (fromIdentity, toIdentity, senderIdentity, senderSharedSecret, userAgent, \
                     buyerCookie, shiptoAddressName, postalAddressName, \
                     deliverTo, street, city, state, postalCode, country, browserFormPostURL) in cur:
                    #print("{}, {}, {}, {}, {}, {}, {}".format(fromIdentity, toIdentity, senderIdentity, senderSharedSecret,
                    #                                      userAgent, buyerCookie, shiptoAddressName))

                    #pOutOrderMsg_b0['b001'] = '"' + browserFormPostURL + '"';
                    shiptoAddressName = shiptoAddressName.replace('&', '&amp;')
                    postalAddressName = postalAddressName.replace('&', '&amp;')
                    deliverTo = deliverTo.replace('&', '&amp;')
                    #pOutOrderMsg_b0['b004'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S@marshfieldbook.com")
                    #pOutOrderMsg_b0['b006'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                get_order = ("select orderno, loginid, custno, status, orderdate, shiptono, \
                              billname, billaddress, billcity, billstate, billcountry, billphone, billemail, \
                              shipname, shipline1, shipline2, shipline3, shipline4, shipcountry, shipphone, shipemail, \
                              callflag, pono, attention, taxcode, ordertotal, totaltax, freightamt, discountamt, \
                              discountpct, comment, lastchangedate, lastchangeby from orderhdr "
                             "where orderno = %s")

                #hdr_cursor.execute(get_order, (order_no,))
                cur.execute(get_order, (order_no,))

                for (orderno, loginid, custno, status, orderdate, shiptono, \
                     billname, billaddress, billcity, billstate, billcountry, billphone, billemail, \
                     shipname, shipline1, shipline2, shipline3, shipline4, shipcountry, shipphone, shipemail, \
                     callflag, pono, attention, taxcode, ordertotal, totaltax, freightamt, discountamt, \
                     discountpct, comment, lastchangedate, lastchangeby) in cur:
                    #print("{}, {}, {}, {}, {}, {}".format(orderno, loginid, custno, status, orderdate, shiptono))

                    order_seq_no = getSeqNo()
                    pOutOrderMsgFile = workDir + 'PunchOutOrderMessage' + order_seq_no + '.xml'
                    pOutOrderMsg = open(pOutOrderMsgFile, 'w')

                    for key in sorted(pOutOrderMsg_b0.iterkeys()):
                        #print("%s" % (pOutOrderMsg_b0key]))
                        pOutOrderMsg.write(pOutOrderMsg_b0[key] + '\n')

                    pOutOrderMsg_b1['b104'] = fromIdentity;
                    pOutOrderMsg_b1['b111'] = toIdentity;
                    pOutOrderMsg_b1['b118'] = senderIdentity;
                    pOutOrderMsg_b1['b121'] = senderSharedSecret;

                    for key in sorted(pOutOrderMsg_b1.iterkeys()):
                        #print("%s" % (pOutOrderMsg_b1[key]))
                        pOutOrderMsg.write(pOutOrderMsg_b1[key] + '\n')

                    order_total = ("%0.2f" % ordertotal)

                    pOutOrderMsg_b2['b203'] = buyerCookie;
                    pOutOrderMsg_b2['b208'] = order_total;
                    pOutOrderMsg_b2['b214'] = shiptoAddressName;
                    pOutOrderMsg_b2['b217'] = '"' + postalAddressName + '"';
                    pOutOrderMsg_b2['b220'] = deliverTo;
                    pOutOrderMsg_b2['b223'] = street;
                    pOutOrderMsg_b2['b226'] = city;
                    pOutOrderMsg_b2['b229'] = state;
                    pOutOrderMsg_b2['b232'] = postalCode;

                    for key in sorted(pOutOrderMsg_b2.iterkeys()):
                        #print("%s" % (pOutOrderMsg_b2[key]))
                        pOutOrderMsg.write(pOutOrderMsg_b2[key] + '\n')



                    get_items = ("select orderno, lineno, itemno, description1, description2, \
                          description3, description4, quantity, price, taxable, priceuom, discount, \
                          sortsequence, itemtype, \
                          lastchangedate, lastchangeby from orderdtl "
                                 "where orderno = %s")

                    #item_cursor.execute(get_items, (order_no,))
                    cur.execute(get_items, (order_no,))

                    for (orderno, lineno, itemno, description1, description2, \
                         description3, description4, quantity, price, taxable, priceuom, discount, \
                         sortsequence, itemtype, \
                         lastchangedate, lastchangeby) in cur:
                        #print("{}, {}, {}, {}, {}, {} {}".format(orderno, lineno, itemno, description1, quantity, price, taxable))

                        item_order_qty = ("%0.0f" % quantity)
                        item_line_no = ("%0.0f" % lineno)
                        item_prc = ("%0.3f" % price)

                        pOutOrderMsg_b3['b301'] = '"' + item_order_qty + '"';   #quantity.orderdtl  formatted
                        pOutOrderMsg_b3['b303'] = '"' + item_line_no + '"';     #lineno.orderdtl  formatted
                        pOutOrderMsg_b3['b307'] = itemno;
                        pOutOrderMsg_b3['b313'] = item_prc;                     #price.orderdtl  formatted
                        pOutOrderMsg_b3['b317'] = description1;
                        pOutOrderMsg_b3['b320'] = priceuom;

                        for key in sorted(pOutOrderMsg_b3.iterkeys()):
                            #print("%s" % (pOutOrderMsg_b3[key]))
                            pOutOrderMsg.write(pOutOrderMsg_b3[key] + '\n')

                    for key in sorted(pOutOrderMsg_b4.iterkeys()):
                        #print("%s" % (pOutOrderMsg_b4[key]))
                        pOutOrderMsg.write(pOutOrderMsg_b4[key] + '\n')

                j_count += 1
                pOutOrderMsg.close()

                order_msg_payloadID = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S@marshfieldbook.com")
                order_msg_timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                #pOutOrderMsgFile = 'PunchOutOrderMessage' + order_seq_no + '.xml'
                order_msg_tree = ET.parse(pOutOrderMsgFile)
                order_msg_root = order_msg_tree.getroot()
                for cXML in order_msg_root.iter('cXML'):
                    cXML.set('payloadID', order_msg_payloadID)
                    cXML.set('timestamp', order_msg_timestamp)
                    order_msg_tree.write(pOutOrderMsgFile)

                # post message doc via cURL

                    #doc_to_send = pOutOrderMsgFile
                    #resp_file = 'PunchOutOrderMessage' + order_seq_no + '.resp'

                if opMode == 'test':
                    doc_post_url = '192.168.51.80:42009'
                else:
                    doc_post_url = browserFormPostURL

                    '''
                    This didn't work ... tried to encapsulate cXML doc in FORM wrapper

                    pOutOrderFormFile = 'PunchOutOrderMessage' + order_seq_no + '.form'
                    pOutOrderForm = open(pOutOrderFormFile, 'w')
                    pOutOrderForm.write('<FORM METHOD=POST ACTION="' + browserFormPostURL + '">' + '\n')
                    pOutOrderForm.write('<INPUT TYPE=HIDDEN NAME="cxml-urlencoded" VALUE=' + '\n')

                    pOutOrderMsg = open(pOutOrderMsgFile, 'r')
                    pOutOrderForm.write('"' + pOutOrderMsg.read() + '"' + '\n')
                    pOutOrderMsg.close()

                    pOutOrderForm.write('<INPUT TYPE=SUBMIT value=BUY>' + '\n')
                    pOutOrderForm.write('</FORM>')
                    pOutOrderForm.close()

                    curl_req(pOutOrderFormFile, doc_post_url)
                    '''
                #curl_req(pOutOrderMsgFile, doc_post_url)
                print('curl cmd commented out, doc not sent to %s' % (doc_post_url) )
                move_to_processed(mbs_order)
                print('approve request sent: %s' % pOutOrderMsgFile)



    #pOutReq_cursor.close()
    #hdr_cursor.close()
    #item_cursor.close()
    cur.close()
    cnx.close()

    print('approve requests processed: %s' % j_count)

if __name__=="__main__":
    main()
