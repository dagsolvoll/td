import cx_Oracle
import xml.etree.ElementTree as ET
from datetime import date


class BuyingBuilder:
    """ A class where a Buying Product Scructure can be Build"""
    def __init__(self, palletGtin, dbConn):
        """ 
            palletGtin is the GTIN of the topmost structure of the product
            sbConn: is the database connection to an assortment schema
        """
        self.palletGtin = palletGtin
        self.dbConn = dbConn


    def createTop(self):
        self.root = ET.Element('BuyingProduct')

    def getBuyingRecord(self, gtin):
        cursor = self.dbConn.cursor()
        cursor.prepare("""
            select * from emsa.buying_item where 1=1
            and gtin = :id
            and (GTIN_PERIOD_TO is null or GTIN_PERIOD_TO > trunc(sysdate))
            """)
        cursor.execute(None, {'id': str(gtin)})
        res = cursor.fetchall()
        cursor.close()
        return res

    def createPalletItem(self):
        self.createTop()
        elm = self.root
        item = ET.SubElement(elm, 'Item')
        elm = ET.SubElement(item, 'GlobalTradeItemNumber')
        elm.text = self.palletGtin
        itemArray = self.getBuyingRecord(self.palletGtin)
        elm = ET.SubElement(item, 'Depth')
        elm.text = str(itemArray[0][13])

    def dump(self):
        ET.dump(self.root)


