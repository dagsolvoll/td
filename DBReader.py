import sys
try:
    import cx_Oracle
except ImportError as ex:
    print ("cx_Oracle finnes ikke (\"" + str(ex) + "\")")

import xml.etree.ElementTree as ET

user = "prod_user"
pwd  = "KI4YAUTQN7X7FVI"
host = "riverton"
db   = "PEMS1"
con  = None

class DBReader:
    def __init__(self, user = user, pwd = pwd, host = host, db = db):
        self.user = user
        self.pwd = pwd
        self.host = host
        self.db = db

    def readmessage(self, msgno):
        con = None
        retstr = ""
        try:
            con = cx_Oracle.connect( self.user + "/" + self.pwd + "@" + 
                    self.host + "/" + self.db)
            cur = con.cursor()
            cur.prepare("""
                SELECT payload from prod.message_log where 1=1
                and message_no = :id
                and contract_id = '01002147'
                """)
            cur.execute(None, {'id': msgno})
            payload = cur.fetchall()[0][0]
            cur.close()
            retstr = ET.fromstring(str(payload))

        except cx_Oracle.DatabaseError as exc:
            print >> sys.stderr, "Oracle-Error-Code:", error.code
            print >> sys.stderr, "Oracle-Error-Message:", error.message
        try:
            con.close()
        except:
            pass
        return retstr

class FileReader:
    def __init__(self, filename):
        self.filename = filename

    def readmessage(self):
        tree = ET.parse(self.filename)
        return tree.getroot()