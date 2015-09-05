import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree
import ItemDef

class ItemEBO:
    
    def __init__(self, robj, itemseq):
        self.rootObj = robj

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
            qty.text = str(item.getattributes(ItemDef.QUANTITY_IN_PREV_LEVEL))

        ga = ET.SubElement(it, "GlobalAttributes")
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


        for c in item.getchildren():
            self.buildItem(packstruct, c)

    def build(self):
        root = ET.Element("ItemEBO")
        ps = ET.SubElement(root, "PackStructure")
        self.buildItem(ps, self.rootObj)

        tree = ElementTree()
        tree._setroot(root)
        tree.write('ebo.xml')
        ET.dump(root) 

