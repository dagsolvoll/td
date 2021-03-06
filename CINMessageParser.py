import xml.etree.ElementTree as ET
from datetime import date

from BuyingBuilder import BuyingBuilder
from ItemDef import Item
from ItemDef import Pallet
from ItemDef import TradeUnit
from ItemDef import BaseUnit
import ItemDef
from DBReader import FileReader
from DBReader import DBReader
from ItemEBO import ItemEBO


ns = {
    "sh" : "http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader" ,
    "eanucc": "urn:ean.ucc:2" ,
    "gdsn": "urn:ean.ucc:gdsn:2",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance", 
    "schemaLocation": "http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader http://www.gs1globalregistry.net/2.7/schemas/sbdh/StandardBusinessDocumentHeader.xsd  urn:ean.ucc:2 http://www.gs1globalregistry.net/2.7/schemas/CatalogueItemNotificationProxy.xsd"
}
rootItem = None
deposits = {}
itemDict = {}

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

def findSingleElem(root, name):
    retval = None
    elm = root.findall(name, ns)
    if elm:
        retval = elm[0].text
    return retval

def findAttribute(root, name, attribname):
    retval = None
    elm = root.findall(name, ns)
    if elm and elm[0].attrib[attribname]:
        retval = elm[0].attrib[attribname]
    return retval

def parseTUInfomation(tradeItemElm, item):
    gln = findSingleElem(tradeItemElm, "tradeItemInformation/informationProviderOfTradeItem/informationProvider/gln")
    name = findSingleElem(tradeItemElm, "tradeItemInformation/informationProviderOfTradeItem/nameOfInformationProvider")
    brandName = findSingleElem(tradeItemElm, "tradeItemInformation/tradeItemDescriptionInformation/brandName")
    descr = findSingleElem(tradeItemElm, "tradeItemInformation/tradeItemDescriptionInformation/functionalName/description/shortText")
    depth = findSingleElem(tradeItemElm, "tradeItemInformation/tradingPartnerNeutralTradeItemInformation/tradeItemMeasurements/depth/measurementValue/value")
    depthUoM = findAttribute(tradeItemElm, "tradeItemInformation/tradingPartnerNeutralTradeItemInformation/tradeItemMeasurements/depth/measurementValue", "unitOfMeasure")
    height = findSingleElem(tradeItemElm, "tradeItemInformation/tradingPartnerNeutralTradeItemInformation/tradeItemMeasurements/height/measurementValue/value")
    heightUoM = findAttribute(tradeItemElm, "tradeItemInformation/tradingPartnerNeutralTradeItemInformation/tradeItemMeasurements/height/measurementValue", "unitOfMeasure")
    width          = findSingleElem(tradeItemElm, "tradeItemInformation/tradingPartnerNeutralTradeItemInformation/tradeItemMeasurements/width/measurementValue/value")
    widthUoM       = findAttribute(tradeItemElm,  "tradeItemInformation/tradingPartnerNeutralTradeItemInformation/tradeItemMeasurements/width/measurementValue", "unitOfMeasure")
    grossWeight    = findSingleElem(tradeItemElm, "tradeItemInformation/tradingPartnerNeutralTradeItemInformation/tradeItemMeasurements/grossWeight/measurementValue/value")
    grossWeightUoM = findAttribute(tradeItemElm,  "tradeItemInformation/tradingPartnerNeutralTradeItemInformation/tradeItemMeasurements/grossWeight/measurementValue", "unitOfMeasure")
    netContent     = findSingleElem(tradeItemElm, "tradeItemInformation/tradingPartnerNeutralTradeItemInformation/tradeItemMeasurements/netContent/measurementValue/value")
    netContentUoM  = findAttribute(tradeItemElm,  "tradeItemInformation/tradingPartnerNeutralTradeItemInformation/tradeItemMeasurements/netContent/measurementValue", "unitOfMeasure")
    compcontent    = findSingleElem(tradeItemElm, "tradeItemInformation/tradingPartnerNeutralTradeItemInformation/tradeItemMeasurements/priceComparisonMeasurement/measurementValue/value")
    compcontentUoM = findAttribute(tradeItemElm,  "tradeItemInformation/tradingPartnerNeutralTradeItemInformation/tradeItemMeasurements/priceComparisonMeasurement/measurementValue", "unitOfMeasure")

    print (netContent)
    item.setattributes(ItemDef.SUPPLIER, [gln,name])
    item.setattributes(ItemDef.BRAND, brandName)
    item.setattributes(ItemDef.DESCRIPTION, descr)
    item.setattributes(ItemDef.DEPTH, [depth, depthUoM])
    item.setattributes(ItemDef.GROSS_WEIGHT, [grossWeight, grossWeightUoM])
    item.setattributes(ItemDef.WIDTH, [width, widthUoM])
    item.setattributes(ItemDef.HEIGHT, [height, heightUoM])
    if netContent:
        item.setattributes(ItemDef.NET_CONTENT, [netContent, netContentUoM])
    if compcontent:
        item.setattributes(ItemDef.COMP_CONTENT, [compcontent, compcontentUoM])

def parseTradeItem(pre, tradeItem):
    global itemDict, rootItem, deposits
    gtin = tradeItem.findall("tradeItemIdentification/gtin", ns)
    item = None
    if gtin[0].text in itemDict:
        item = itemDict[gtin[0].text]
    else:
        item = Item()
        itemDict[gtin[0].text] = item
        item.setgtin(gtin[0].text)
    if rootItem is None:
        rootItem = item

    deposit = tradeItem.findall("tradeItemInformation/tradingPartnerNeutralTradeItemInformation/packagingMaterial/returnablePackageDepositCode", ns)
    if (len(deposit)):
        item.setattributes(ItemDef.DEPOSIT, deposit[0].text)
        deposits[deposit[0].text] = deposit[0].text
    tradeItemUnitDescriptor = tradeItem.findall("tradeItemUnitDescriptor", ns)
    gln = tradeItem.findall("tradeItemIdentification/gtin", ns)
    baseunit  = tradeItem.findall("tradeItemInformation/tradingPartnerNeutralTradeItemInformation/tradeItemUnitIndicator/isTradeItemABaseUnit", ns)
    tradeunit = tradeItem.findall("tradeItemInformation/tradingPartnerNeutralTradeItemInformation/tradeItemUnitIndicator/isTradeItemAnOrderableUnit", ns)

    if tradeItemUnitDescriptor[0].text == "PALLET" or tradeItemUnitDescriptor[0].text == "MIXED_MODE":
        item.setpallet(Pallet())

    if baseunit and str2bool(baseunit[0].text):
        item.setbaseunit(BaseUnit())

    if tradeunit and str2bool(tradeunit[0].text):
        item.settradeunit(TradeUnit())

    childQty = tradeItem.findall("nextLowerLevelTradeItemInformation/quantityOfChildren", ns)
    children = tradeItem.findall("nextLowerLevelTradeItemInformation/childTradeItem", ns)
    ChildTotalQty = tradeItem.findall("nextLowerLevelTradeItemInformation/totalQuantityOfNextLowerLevelTradeItem", ns)
    for ch in children:        
        gt = ch.findall("tradeItemIdentification/gtin", ns)
        if gt:
            nit = None
            if gt[0].text in itemDict:
                nit = itemDict[gt[0].text]
            else:  
                nit = Item()
                itemDict[gt[0].text] = nit
                nit.setgtin(gt[0].text)

            nl = ch.findall("quantityofNextLowerLevelTradeItem", ns)
            if nl:
                nit.setattributes(ItemDef.QUANTITY_IN_PREV_LEVEL, nl[0].text)
            item.addChild(nit)
            nit.addParent(item)
    parseTUInfomation(tradeItem, item)

def parseCatalogItem(pre, ci):
    dataRep = ci.findall("dataRecipient", ns)
    sourceDataPool = ci.findall("sourceDataPool", ns)
    tradeItem = ci.findall("tradeItem", ns)
    if dataRep:
        pass #print(pre + dataRep[0].text)
    if sourceDataPool:
        pass #print (pre + sourceDataPool[0].text)
    for ti in tradeItem:
        parseTradeItem(pre, ti)
    #print (pre + "next" + str(ci))
    for child in ci.findall("catalogueItemChildItemLink", ns):
        #print(pre + "child : " + str(child))
        for c in child.findall("catalogueItem", ns):
            parseCatalogItem(pre + "    ", c)

def parseMsg(root):
    global ns, rootItem, deposits
    message = root.getchildren()[0].getchildren()[1]
    notif = message.findall("eanucc:transaction/command/eanucc:documentCommand/documentCommandOperand/gdsn:catalogueItemNotification", ns)    
    for c in notif[0].findall("catalogueItem", ns):
        parseCatalogItem("", c)
    rootItem.setattributes(ItemDef.DEPOSITS, deposits)

def parseCINMessage(filename):
    fr = FileReader(filename)
    parseMsg(fr.readmessage())
    num = rootItem.setitemnumber(None,1)
    ebo = ItemEBO(rootItem, 1)
    ebo.build()
    return ebo

def parseCINMessageFromDB(msgno, dbreader):
    parseMsg(dbreader.readmessage(msgno))
    num = rootItem.setitemnumber(dbreader,1)
    ebo = ItemEBO(rootItem, 1)
    ebo.build()
    return ebo
    



