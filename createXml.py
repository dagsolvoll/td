import cx_Oracle
import xml.etree.ElementTree as ET
from datetime import date
from BuyingBuilder import BuyingBuilder

user = "extdsl_adm"
pwd  = "August2015"
host = "riverton"
db   = "PEMS2"
con  = None

def openDB():
    global con, user, pwd, host, db
    con = cx_Oracle.connect( user + "/" + pwd + "@" + 
        host + "/" + db)
    print (con.version)

def closeDB():
    global con
    con.close()

def getBuyingItem(id):
    global con
    cur = con.cursor()
    root 
    try: 
        cur.prepare(""" 
                select * from emsa.buying_item where id = :id
            """)
        cur.execute(None, {'id': str(id)})
        for res in cur:            
            root = ET.Element('Payload')
            ET.SubElement(root, 'BuyingProduct')
            ET.SubElement(root, 'BuyingProduct')
            print(res)

    except: 
        pass
    cur.close()

def createXml(biId):
    global con
    cur = con.cursor()
    cur.prepare("""
        SELECT parent_buying_item_id, buying_item_id 
        FROM EMSA.BUYING_ITEM_MEMBER mem 
        start WITH MEM.PARENT_BUYING_ITEM_ID = :id
        connect BY PRIOR MEM.BUYING_ITEM_ID = MEM.PARENT_BUYING_ITEM_ID
        """)
    cur.execute(None, {'id': str(biId)})
    tid = None
    arr = []
    for result in cur:
        arr.append(result[0])
        tid =  result[1]
    arr.append(tid)
    print (arr)
    getBuyingItem(arr[0])
    cur.close()


def mainFunc():
    global con
    openDB()
    bb = BuyingBuilder('27311710000561', con)
    bb.createPalletItem()
    bb.dump()
    #createXml(368566)
    closeDB()

if __name__ == "__main__":
    mainFunc()