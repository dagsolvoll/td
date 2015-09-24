import sys
try:
    import cx_Oracle
except ImportError as ex:
    print ("cx_Oracle finnes ikke (\"" + str(ex) + "\")")

import xml.etree.ElementTree as ET

g_user = "prod_user"
g_pwd  = "KI4YAUTQN7X7FVI"
g_host = "riverton"
g_db   = "PEMS1"
con  = None

class DBReader:
    def __init__(self, user = g_user, pwd = g_pwd, host = g_host, db = g_db):
        self.user = user
        self.pwd = pwd
        self.host = host
        self.db = db

    def readmessageno(self):
        con = None
        msgnos = []
        try:
            con = cx_Oracle.connect( self.user + "/" + self.pwd + "@" + 
                        self.host + "/" + self.db)
            cur = con.cursor()
            print("START")
            cur.execute("""
                    SELECT MESSAGE_NO from ML where 1=1
                    AND contract_id = '01002147'
                    --AND rownum < 1000
                """)

            for i in cur.fetchall():
                msgnos.append(i[0])
            cur.close()
        except cx_Oracle.DatabaseError as exc:
            print ("Exception: ", exc)
        try:
            con.close();
        except:
            pass
        return msgnos

    def readmessage(self, msgno):
        con = None
        retstr = ""
        try:
            con = cx_Oracle.connect( self.user + "/" + self.pwd + "@" + 
                    self.host + "/" + self.db)
            cur = con.cursor()
            print(self.user)
            cur.prepare("""
                SELECT PAYLOAD from ML where message_no = :id
 --               SELECT payload from prod.message_log where 1=1
 --               and message_no = :id
 --               and contract_id = '01002147'
                """)
            cur.execute(None, {'id': msgno})
            payload = cur.fetchall()[0][0]
            cur.close()
            retstr = ET.fromstring(str(payload))

        except cx_Oracle.DatabaseError as exc:
            print (sys.stderr, "Oracle-Error-Code:", error.code)
            print >> sys.stderr, "Oracle-Error-Message:", error.message
        try:
            con.close()
        except:
            pass
        return retstr

    def readItemNo(self, gtin):
        con = None
        itemNo = None
        try:
            con = cx_Oracle.connect( self.user + "/" + self.pwd + "@" + 
                    self.host + "/" + self.db)
            cur = con.cursor()
            print(self.user)
            cur.prepare("""
                SELECT ITEM_NO from ML_GTIN where GTIN = :gtin
                """)
            cur.execute(None, {'gtin': gtin})
            itemNo = cur.fetchall()[0][0]
            cur.close()
        except cx_Oracle.DatabaseError as exc:
            print ("Oracle-Error-Code:", error.code)
            print ("Oracle-Error-Message:", error.message)
        try:
            con.close()
        except:
            pass
        return itemNo

class FileReader:
    def __init__(self, filename):
        self.filename = filename

    def readmessage(self):
        tree = ET.parse(self.filename)
        return tree.getroot()