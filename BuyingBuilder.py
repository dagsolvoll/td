import xml.etree.ElementTree as ET
from datetime import date
import ItemDef

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

def gtinType(gtin):
    if len(gtin) == 8:
        return "EAN-8"
    elif len(gtin) == 12:
        return "EAN-12"
    elif len(gtin) == 14:
        return "EAN-14"
    elif len(gtin) == 13:
        if gtin[0] == "2":
            return "SE"
        else:
            return "EAN-13"
    else:
        return "UNDEF"

class BuyingBuilder:
    """ A class where a Buying Product Scructure can be Build"""
    def __init__(self, itemEbo):
        """ 
            palletGtin is the GTIN of the topmost structure of the product
            sbConn: is the database connection to an assortment schema
        """
        self.itemElement = itemEbo

    def producecontract(self):
        dict = {}
        rootItem = None
        for elm in self.itemElement.findall("PackStructure/Item"):
            print (elm.find("ItemNumber").text)
            item = None           
            if elm.find("ItemNumber").text in dict:
                item = dict[elm.find("ItemNumber").text]
                item.setgtin(elm.find("Gtin").text)
            else:
                item = ItemDef.Item(elm.find("Gtin").text)
                dict[elm.find("ItemNumber").text] = item

            if elm.find("PackType").text == "Pallet":
                rootItem = item
                item.setpallet(ItemDef.Pallet())

            for rel in elm.findall("PackRelation"):
                child = None
                if rel.find("RelationPackNumber").text in dict:
                    child = dict[rel.find("RelationPackNumber").text]
                else:
                    child = ItemDef.Item(rel.find("RelationPackNumber").text)
                    dict[rel.find("RelationPackNumber").text] = child
                item.addChild(child)
                child.addParent(item)

            if str2bool(elm.find("GlobalAttributes/TradeItem/IsTradeItemABaseUnit").text):
                item.setbaseunit(ItemDef.BaseUnit())
            if str2bool(elm.find("GlobalAttributes/TradeItem/IsTradeItemAnOrderableUnit").text):
                item.settradeunit(ItemDef.TradeUnit())

            print (elm.find("GlobalAttributes/TradeItem/IsTradeItemABaseUnit").text)
        rootItem.dump("")

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

    def createPayload(self):
        payload = ET.Element('Payload')
        root = ET.SubElement(payload, 'BuyingProduct')
        self.createItems(root, self.rootItem)
        return payload

    def createItems(self, root, item):
        itemElm = ET.SubElement(root, 'Item')
        elm = ET.SubElement(itemElm, 'GlobalTradeItemNumber')
        elm.text = self.palletGtin
        itemArray = self.getBuyingRecord(self.palletGtin)
        elm = ET.SubElement(itemElm, 'Depth')
        elm.text = str(itemArray[0][13])

    def dump(self):
        ET.dump(self.createPayload())


