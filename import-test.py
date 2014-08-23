import mysql.connector
from mysql.connector import errorcode
from cfg_dbAccess import dbAccess
from cfg_reqDir import reqDir
from cfg_serverAddr import serverAddr


db_user = (dbAccess['user'])
host = (serverAddr['host'])
port = (serverAddr['port'])
print(host, port)
print db_user
print reqDir[0:-1] + '_processed'

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

cur.close()
cnx.close()
