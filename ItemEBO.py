import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree

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

        if item.getprovider():
            sup = ET.SubElement(it, "Supplier")
            supn = ET.SubElement(sup, "SupplierName")
            supn.text = item.getprovider()[1]
            sss = ET.SubElement(sup, "SupplierSite")
            gln = ET.SubElement(sss, "GlobalIdentificationNumber")
            gln.text = item.getprovider()[0]

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
            qty.text = str(item.getquantity())

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

