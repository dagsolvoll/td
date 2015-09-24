import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree
import ItemDef

class ItemEBO:
    
    def __init__(self, robj, itemseq):
        self.rootObj = robj
        self.rootElement = None

    def buildItem(self, packstruct, item):
        it = ET.SubElement(packstruct, "Item")
        itn = ET.SubElement(it, "ItemNumber")
        itn.text = str(item.getitemnumber())

        gtin = ET.SubElement(it, "Gtin")
        gtin.text = item.getgtin()
        pt = ET.SubElement(it, "PackType")
        if item.ispallet():
            pt.text = "Pallet"
        elif item.istradeunit():
            pt.text = "Case"
        elif item.isbaseunit():
            pt.text = "Each"


        if item.getattributes(ItemDef.SUPPLIER):
            sup = ET.SubElement(it, "Supplier")
            supn = ET.SubElement(sup, "SupplierName")
            supn.text = item.getattributes(ItemDef.SUPPLIER)[1]
            sss = ET.SubElement(sup, "SupplierSite")
            gln = ET.SubElement(sss, "GlobalIdentificationNumber")
            gln.text = item.getattributes(ItemDef.SUPPLIER)[0]
            ssr = ET.SubElement(sss, "SupplierSiteRole")
            cv = ET.SubElement(ssr, "CodeValue")
            cv.text = "TP"
            cv = ET.SubElement(ssr, "CodeName")
            cv.text = "Trading partner"
            ssr = ET.SubElement(sss, "PrimarySupplierSite")
            ssr.text = "true"

        for c in item.getchildren():
            pr = ET.SubElement(it, "PackRelation")
            num = ET.SubElement(pr, "RelationPackNumber")
            num.text = str(c.getitemnumber())
            rpt = ET.SubElement(pr, "RelationPackType")
            if c.ispallet():
                rpt.text = "Pallet"
            elif c.istradeunit():
                rpt.text = "Case"
            else:
                rpt.text = "Each"
            qty = ET.SubElement(pr, "Qty")
            if c.getattributes(ItemDef.QUANTITY_IN_PREV_LEVEL):
                qty.text = str(c.getattributes(ItemDef.QUANTITY_IN_PREV_LEVEL))
            else:
                qty.text = "0"

        if item.getattributes(ItemDef.DEPOSIT):
            de = ET.SubElement(it, "DepositItemRef")
            dec = ET.SubElement(de, "DepositItemNumber")
            dec.text = item.getattributes(ItemDef.DEPOSIT)

        la = ET.SubElement(it, "LocalAttributes")
        de = ET.SubElement(la, "ItemDescription")
        de.text = item.getattributes(ItemDef.DESCRIPTION)

        ga = ET.SubElement(it, "GlobalAttributes")
        


        if item.getattributes(ItemDef.COMP_CONTENT):
            tid = ET.SubElement(ga, "SalesInformationModule")
            tw  = ET.SubElement(tid, "PriceComparisonContentTypeCode")
            tw.text = item.getattributes(ItemDef.COMP_CONTENT)[1]
            tw = ET.SubElement(tid, "PriceComparisonMeasurement")
            tw.text = item.getattributes(ItemDef.COMP_CONTENT)[0]

        ti = ET.SubElement(ga, "TradeItem")
        if item.getattributes(ItemDef.QUANTITY_IN_PREV_LEVEL): 
            tib = ET.SubElement(ti, "QuantityOfNextLowerLevelTradeItem")
            tib.text = item.getattributes(ItemDef.QUANTITY_IN_PREV_LEVEL)


        tib = ET.SubElement(ti, "IsTradeItemABaseUnit")
        if item.isbaseunit():
            tib.text = "true"
        else:
            tib.text = "false"

        tib = ET.SubElement(ti, "IsTradeItemAnOrderableUnit")
        if item.istradeunit():
            tib.text = "true"
        else:
            tib.text = "false"

        tid = ET.SubElement(ga, "TradeItemDimensions")
        tw = ET.SubElement(tid, "Width")
        tw.text = item.getattributes(ItemDef.WIDTH)[0]
        tw = ET.SubElement(tid, "Height")
        tw.text = item.getattributes(ItemDef.HEIGHT)[0]
        tw = ET.SubElement(tid, "DimensionTypeCode")
        tw.text = item.getattributes(ItemDef.WIDTH)[1]
        tw = ET.SubElement(tid, "Depth")
        tw.text = item.getattributes(ItemDef.DEPTH)[0]

        tid = ET.SubElement(ga, "TradeItemMeasurementsModule")
        if item.getattributes(ItemDef.NET_CONTENT):
            tw = ET.SubElement(tid, "NetContent")
            tw.text = item.getattributes(ItemDef.NET_CONTENT)[0]
        tw = ET.SubElement(tid, "GrossWeight")
        tw.text = item.getattributes(ItemDef.GROSS_WEIGHT)[0]

        

        for c in item.getchildren():
            self.buildItem(packstruct, c)

    def build(self):
        self.rootElement = ET.Element("ItemEBO")
        ps = ET.SubElement(self.rootElement, "PackStructure")
        self.buildItem(ps, self.rootObj)
        if self.rootObj.getattributes(ItemDef.DEPOSITS):
            for key in self.rootObj.getattributes(ItemDef.DEPOSITS).keys():
                di = ET.SubElement(self.rootElement, "DepositItem")
                div = ET.SubElement(di, "ItemNumber")
                div.text = key
                div = ET.SubElement(di, "DepositGTIN")
                div.text = key
                div = ET.SubElement(di, "Description")
                div.text = 'asdasd'


    def dump(self, file = "XXX"):
        if file == "XXX":
            ET.dump(self.rootElement) 
        else:
            tree = ElementTree()
            tree._setroot(self.rootElement)
            tree.write(file, "UTF-8")

    def getrootelement(self):
        return self.rootElement
