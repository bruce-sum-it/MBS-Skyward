#!/usr/bin/env python

# Create python xml structures compatible with
# http://search.cpan.org/~grantm/XML-Simple-2.18/lib/XML/Simple.pm

from __future__ import print_function
from itertools import groupby
import mysql.connector
from mysql.connector import errorcode
from xml.etree import ElementTree as ET

dbAccess = {
    'user': 'sumit',
    'password': 'f1sumit',
    'host': '192.168.51.80',
    'database': 'marshdta',
    'raise_on_warnings': True,
}

def createPOutReqTbl(cur):
    createTbl = ("CREATE TABLE if not exists pOutReq \
                 (reqNo MEDIUMINT PRIMARY KEY AUTO_INCREMENT, \
                  fromIdentity         varchar(60), \
                  toIdentity           varchar(60), \
                  senderIdentity       varchar(60), \
                  senderSharedSecret   varchar(60), \
                  userAgent            varchar(60), \
                  operation            varchar(20), \
                  buyerCookie          varchar(60) NOT NULL UNIQUE, \
                  extrinsicUserID      varchar(60), \
                  browserFormPostURL   varchar(100), \
                  supplierSetupURL     varchar(100), \
                  shiptoAddressID      varchar(40), \
                  shiptoAddressName    varchar(60), \
                  postalAddressName    varchar(60), \
                  deliverTo            varchar(60), \
                  street               varchar(60), \
                  city                 varchar(60), \
                  state                varchar(2), \
                  postalCode           varchar(10), \
                  country              varchar(40), \
                  mbsOrderNo           int(11), \
                  docPayloadID         varchar(60), \
                  docTimeStamp         varchar(20), \
                  custno               varchar(12), \
                  shiptono             varchar(6))")

    try:
        #print("Creating table pOutReq ", end='')
        cur.execute(createTbl)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            #print("already exists.")
            pass
        else:
            print(err.msg)
    #else:
        #print("OK")

def addReq2Tbl(reqDoc):


    root = ET.fromstring(reqDoc)

    #print(root.attrib['payloadID'])
    docPayloadID = root.attrib['payloadID']

    #print(root.attrib['timestamp'])
    docTimeStamp = root.attrib['timestamp']

    #root[0][0] <From>
    for Credential in root.findall('./Header/From/Credential'):
        #print('From Credential:', Credential.attrib)
        #print(Credential.attrib['domain'])
        fromCredential = Credential.attrib['domain']

    for Identity in root.findall('./Header/From/Credential/Identity'):
        #print('From Identity:', Identity.text)
        fromIdentity = Identity.text

    #root[0][1] <To>
    for Credential in root.findall('./Header/To/Credential'):
        #print('To Credential:', Credential.attrib)
        #print(Credential.attrib['domain'])
        toCredential = Credential.attrib['domain']

    for Identity in root.findall('./Header/To/Credential/Identity'):
        #print('To Identity:', Identity.text)
        toIdentity = Identity.text

    #root[0][2] <Sender>
    for Credential in root.findall('./Header/Sender/Credential'):
        #print('Sender Credential:', Credential.attrib)
        #print(Credential.attrib['domain'])
        senderCredential = Credential.attrib['domain']

    for Identity in root.findall('./Header/Sender/Credential/Identity'):
        #print('Sender Identity:', Identity.text)
        senderIdentity = Identity.text

    for SharedSecret in root.findall('./Header/Sender/Credential/SharedSecret'):
        #print('Sender SharedSecret:', SharedSecret.text)
        senderSharedSecret = SharedSecret.text

    for UserAgent in root.findall('./Header/Sender/UserAgent'):
        #print('Sender UserAgent:', UserAgent.text)
        userAgent = UserAgent.text

    '''
    alternate way to find elements:
    for Credential in root[0][2].iter('Credential'):
        print('Sender Credential', Credential.attrib)
    for Identity in root[0][2].iter('Identity'):
        print('Sender Identity', Identity.text)
    for SharedSecret in root[0][2].iter('SharedSecret'):
        print('Sender SharedSecret', SharedSecret.text)
    for UserAgent in root[0][2].iter('UserAgent'):
        print('Sender UserAgent', UserAgent.text)
    '''

    #root[1][0] <PunchOutSetupRequest> or <OrderRequest>
    for PunchOutSetupRequest in root.findall('./Request/PunchOutSetupRequest'):
        #print('PunchOutSetupRequest:', PunchOutSetupRequest.attrib)
        #print(PunchOutSetupRequest.attrib['operation'])
        operation = PunchOutSetupRequest.attrib['operation']

    for BuyerCookie in root.findall('./Request/PunchOutSetupRequest/BuyerCookie'):
        #print('BuyerCookie:', BuyerCookie.text)
        buyerCookie = BuyerCookie.text

    for Extrinsic in root.findall('./Request/PunchOutSetupRequest/Extrinsic'):
        #print('Extrinsic attrib:',Extrinsic.attrib['name'])
        #print('Extrinsic:', Extrinsic.text)
        extrinsicUserID = Extrinsic.text

    for BrowserFormPostURL in root.findall('./Request/PunchOutSetupRequest/BrowserFormPost/URL'):
        #print('BrowserFormPostURL:', BrowserFormPostURL.text)
        browserFormPostURL = BrowserFormPostURL.text

    for SupplierSetupURL in root.findall('./Request/PunchOutSetupRequest/SupplierSetup/URL'):
        #print('SupplierSetupURL:', SupplierSetupURL.text)
        supplierSetupURL = SupplierSetupURL.text

    for ShipToAddressID in root.findall('./Request/PunchOutSetupRequest/ShipTo/Address'):
        #print('ShipToAddressID:', ShipToAddressID.attrib)
        #print(ShipToAddressID.attrib['addressID'])
        shiptoAddressID = ShipToAddressID.attrib['addressID']
        custno, shiptono = shiptoAddressID.split("-")

    for ShipToName in root.findall('./Request/PunchOutSetupRequest/ShipTo/Address/Name'):
        #print('ShipToName attrib:', ShipToName.attrib)
        #print('ShipToName:', ShipToName.text)
        shiptoAddressName = ShipToName.text

    for PostalAddressName in root.findall('./Request/PunchOutSetupRequest/ShipTo/Address/Name'):
        #print('PostalAddressName:', PostalAddressName.text)
        postalAddressName = PostalAddressName.text

    for DeliverTo in root.findall('./Request/PunchOutSetupRequest/ShipTo/Address/PostalAddress/DeliverTo'):
        #print('DeliverTo:', DeliverTo.text)
        deliverTo = DeliverTo.text

    for Street in root.findall('./Request/PunchOutSetupRequest/ShipTo/Address/PostalAddress/Street'):
        #print('Street:', Street.text)
        street = Street.text

    for City in root.findall('./Request/PunchOutSetupRequest/ShipTo/Address/PostalAddress/City'):
        #print('City:', City.text)
        city = City.text

    for State in root.findall('./Request/PunchOutSetupRequest/ShipTo/Address/PostalAddress/State'):
        #print('State:', State.text)
        state = State.text

    for PostalCode in root.findall('./Request/PunchOutSetupRequest/ShipTo/Address/PostalAddress/PostalCode'):
        #print('PostalCode:', PostalCode.text)
        postalCode = PostalCode.text

    for Country in root.findall('./Request/PunchOutSetupRequest/ShipTo/Address/PostalAddress/Country'):
        #print('Country attrib:', Country.attrib)
        #print('Country:', Country.attrib['isoCountryCode'])
        country = Country.attrib['isoCountryCode']


    try:
        cnx = mysql.connector.connect(**dbAccess)

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exists")
        else:
            print(err)

    cur = cnx.cursor()

    reqNoValue = cur.lastrowid

    pOutReqData = {
        'reqNo': reqNoValue,
        'fromIdentity': fromIdentity,
        'toIdentity': toIdentity,
        'senderIdentity': senderIdentity,
        'senderSharedSecret': senderSharedSecret,
        'userAgent': userAgent,
        'operation': operation,
        'buyerCookie': buyerCookie,
        'extrinsicUserID': extrinsicUserID,
        'browserFormPostURL': browserFormPostURL,
        'supplierSetupURL': supplierSetupURL,
        'shiptoAddressID': shiptoAddressID,
        'shiptoAddressName': shiptoAddressName,
        'postalAddressName': postalAddressName,
        'deliverTo': deliverTo,
        'street': street,
        'city': city,
        'state': state,
        'postalCode': postalCode,
        'country': country,
        'docPayloadID': docPayloadID,
        'docTimeStamp': docTimeStamp,
        'custno': custno,
        'shiptono': shiptono
        }

    '''
    not included yet:
    'mbsOrderNo':
    'addressName':
    '''

    #Z = etree.tostring (d2xml(Y) )
    #print Z
    #assert X == Z


    #with cnx:
    createPOutReqTbl(cur)

    addPOutReq = ("INSERT INTO pOutReq "
                  "(reqNo, fromIdentity, toIdentity, senderIdentity, senderSharedSecret, \
                  userAgent, operation, buyerCookie, extrinsicUserID, browserFormPostURL, \
                  supplierSetupURL, shiptoAddressID, shiptoAddressName, \
                  postalAddressName, deliverTo, street, city, state, postalCode, country, \
                  docPayloadID, docTimeStamp, custno, shiptono)"
                  "VALUES \
                  (%(reqNo)s, %(fromIdentity)s, %(toIdentity)s, %(senderIdentity)s, %(senderSharedSecret)s, \
                  %(userAgent)s, %(operation)s, %(buyerCookie)s, %(extrinsicUserID)s, %(browserFormPostURL)s, \
                  %(supplierSetupURL)s, %(shiptoAddressID)s, %(shiptoAddressName)s, \
                  %(postalAddressName)s, %(deliverTo)s, %(street)s, %(city)s, %(state)s, %(postalCode)s, %(country)s, \
                  %(docPayloadID)s, %(docTimeStamp)s, %(custno)s, %(shiptono)s)")
    try:
        cur.execute(addPOutReq, pOutReqData)
    except Exception as msg:
        print(msg, 'Error updating db row')

    if cnx:
        cnx.commit()
        cur.close()
        cnx.close()

    return(buyerCookie)

def main():
    '''
        PunchOutSetupRequest structure dict/subdicts
        payloadID
        timestamp
        version
        Header
            From
                Credential
                    Identity
            To
                Credential
                    Identity
            Sender
                Credential
                    Identity
                    SharedSecret
                UserAgent
        Request
            PunchOutSetupRequest
                BuyerCookie
                ExtrinsicUserID
                BrowserFormPost
                    URL
                SupplierSetup
                    URL
                Shipto
                    Address
                        addressID
                        Name
                        PostalAddress
                            DeliverTo
                            Street
                            City
                            State
                            PostalCode
                            Country
        '''

    reqFileName = 'PunchOutSetupRequest000182.xml'
    # i.e.'PunchOutSetupRequest.xml' or 'OrderRequest.xml'
    try:
        reqFile = open(reqFileName, 'r')
        reqDoc = reqFile.read()
    except Exception as msg:
        print(msg, 'XML doc not found')

    #X = """<T uri="boo"><a n="1"/><a n="2"/><b n="3"><c x="y"/></b></T>"""
    #print(reqDoc)
    addReq2Tbl(reqDoc)

if __name__=="__main__":
    main()

