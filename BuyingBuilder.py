import xml.etree.ElementTree as ET
from datetime import date
import ItemDef
from DBReader import FileReader

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

def gtinType(gtin):
    if gtin[0] == "0":
        gtin = gtin[1:]
    if len(gtin) == 8:
        return "E08"
    elif len(gtin) == 12:
        return "E12"
    elif len(gtin) == 14:
        return "E14"
    elif len(gtin) == 13:
        if gtin[0] == "2":
            return "2SE"
        else:
            return "E13"
    else:
        return "UNDEF"

class BuyingBuilder:
    """ A class where a Buying Product Scructure can be Build"""
    def __init__(self, itemEbo, inputfile):
        """ 
            palletGtin is the GTIN of the topmost structure of the product
            sbConn: is the database connection to an assortment schema
        """
        self.itemElement = itemEbo
        if inputfile:
            self.itemElement = FileReader(inputfile).readmessage()
        self.rootItem = None

    def producecontract(self):
        dict = {}
        self.rootItem = None
        for elm in self.itemElement.findall("PackStructure/Item"):
            #print (elm.find("ItemNumber").text)
            item = None           
            if elm.find("ItemNumber").text in dict:
                item = dict[elm.find("ItemNumber").text]
                item.setgtin(elm.find("Gtin").text)
            else:
                item = ItemDef.Item(elm.find("Gtin").text)
                dict[elm.find("ItemNumber").text] = item

            if elm.find("PackType").text == "Pallet":
                self.rootItem = item
                item.setpallet(ItemDef.Pallet())

            for rel in elm.findall("PackRelation"):
                child = None
                if rel.find("RelationPackNumber").text in dict:
                    child = dict[rel.find("RelationPackNumber").text]
                else:
                    child = ItemDef.Item(rel.find("RelationPackNumber").text)
                    dict[rel.find("RelationPackNumber").text] = child

                child.setattributes(ItemDef.QUANTITY_IN_PREV_LEVEL, rel.find("Qty").text)
                item.addChild(child)
                child.addParent(item)

            if str2bool(elm.find("GlobalAttributes/TradeItem/IsTradeItemABaseUnit").text):
                item.setbaseunit(ItemDef.BaseUnit())
            if str2bool(elm.find("GlobalAttributes/TradeItem/IsTradeItemAnOrderableUnit").text):
                item.settradeunit(ItemDef.TradeUnit())

            dtp = elm.find("GlobalAttributes/TradeItemDimensions/DimensionTypeCode").text
            gw = None
            if elm.find("GlobalAttributes/TradeItemMeasurementsModule/GrossWeight") is not None:
                gw = [elm.find("GlobalAttributes/TradeItemMeasurementsModule/GrossWeight").text, dtp]
            item.setattributes(ItemDef.DEPTH, [elm.find("GlobalAttributes/TradeItemDimensions/Depth").text, dtp])
            item.setattributes(ItemDef.WIDTH, [elm.find("GlobalAttributes/TradeItemDimensions/Width").text, dtp])
            item.setattributes(ItemDef.HEIGHT, [elm.find("GlobalAttributes/TradeItemDimensions/Height").text, dtp])
            item.setattributes(ItemDef.GROSS_WEIGHT, gw)



        self.rootItem.dump("")

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
        elm.text = item.getgtin()
        elm = ET.SubElement(itemElm, 'GtinTypeCode')
        elm.text = gtinType(item.getgtin())
        elm = ET.SubElement(itemElm, 'FirstDateGtinValid')
        elm.text = "2015-01-01"
        elm = ET.SubElement(itemElm, 'EffectiveDate')
        elm.text = "2015-01-01"
        elm = ET.SubElement(itemElm, 'StartAvailabilityDate')
        elm.text = "2015-01-01"
        elm = ET.SubElement(itemElm, 'PackagingRecyclableFlag')
        elm.text = "false"
        elm = ET.SubElement(itemElm, 'Depth')
        elm.text = item.getattributes(ItemDef.DEPTH)[0]
        elm = ET.SubElement(itemElm, 'Height')
        elm.text = item.getattributes(ItemDef.HEIGHT)[0]
        elm = ET.SubElement(itemElm, 'Width')
        elm.text = item.getattributes(ItemDef.WIDTH)[0]
        if item.getattributes(ItemDef.GROSS_WEIGHT):
            elm = ET.SubElement(itemElm, 'GrossWeight')
            elm.text = item.getattributes(ItemDef.GROSS_WEIGHT)[0]

        elm = ET.SubElement(itemElm, 'UnitOfMeasureDimensions');
        elm.text = item.getattributes(ItemDef.WIDTH)[1].lower()
        elm = ET.SubElement(itemElm, 'UnitOfMeasureWeights');
        elm.text = item.getattributes(ItemDef.GROSS_WEIGHT)[1].lower()
        elm = ET.SubElement(itemElm, 'ReadOnlyFlag');
        elm.text = "true"
        elm = ET.SubElement(itemElm, 'NumberOfItemsContainedInPreviousLevel');
        if item.getattributes(ItemDef.QUANTITY_IN_PREV_LEVEL):
            elm.text = item.getattributes(ItemDef.QUANTITY_IN_PREV_LEVEL)
        else:
            elm.text = "0"

        if item.ispallet():
            elm = ET.SubElement(itemElm, 'Pallet')

        if item.istradeunit():
            elm = ET.SubElement(itemElm, 'TradeUnit')

        if item.isbaseunit():
            elm = ET.SubElement(itemElm, 'BaseUnit')

        for chl in item.getchildren():
            self.createItems(itemElm, chl)

    def dump(self, filename):
        from xml.etree.ElementTree import ElementTree
        pl = self.createPayload()
        #ET.dump(pl)
        tree = ElementTree()
        tree._setroot(pl)
        tree.write(filename, "UTF-8")
