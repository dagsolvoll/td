
class Pallet:
    def __init__(self):
        pass

class TradeUnit:
    def __init__(self):
        pass

class BaseUnit:
    def __init__(self):
        pass

SUPPLIER = 'supplier'
BRAND = 'brand'
DESCRIPTION = 'description'
GROSS_WEIGTH = 'grossweight'
DEPTH = 'depth'
HEIGHT = 'height'
WIDTH = 'width'
QUANTITY_IN_PREV_LEVEL = 'quantity'

class Item:

    def __init__(self, gtin=None):
        self.gtin = gtin
        self.children = []
        self.parents = []
        self.pallet = None
        self.tradeunit = None
        self.baseunit = None
        self.attributes = {}

        self.quantity = None
        self.brandname = None
        self.description = None
        self.depth = None
        self.grossweight = None
        self.height = None
        self.width = None
        self.itemnumber = 99999999

    def __str__(self):
        typ = ""
        if self.ispallet() and self.istradeunit() and self.isbaseunit():
            typ = "PTUBU"
        elif self.ispallet() and self.istradeunit():
            typ = "PTU"
        elif self.ispallet() and self.isbaseunit():
            typ = "PBU"
        elif self.isbaseunit() and self.istradeunit():
            typ = "TUBU" + str(self.tradeunit)
        elif self.ispallet():
            typ = "P"
        elif self.istradeunit():
            typ = "TU"
        elif self.isbaseunit():
            typ = "BU"
        retstr = "Item: [gtin=" + self.gtin + ", " + \
            "Type: "  + typ + ", Qty: " + str(self.quantity)

        for key in self.attributes:
            retstr += str(key) + ": " + str(self.attributes[key])

        retstr += "]"
        return retstr

    def setgtin(self, gtin):
        self.gtin = gtin

    def getgtin(self):
        return self.gtin

    def setbaseunit(self, bu):
        self.baseunit = bu

    def getbaseunit(self):
        return self.baseunit

    def isbaseunit(self):
        return self.baseunit != None

    def settradeunit(self, bu):
        self.tradeunit = bu

    def gettradeunit(self):
        return self.tradeunit

    def istradeunit(self):
        return self.tradeunit != None

    def setpallet(self, p):
        self.pallet = p

    def getpallet(self):
        return self.pallet

    def ispallet(self):
        return self.pallet != None

    def setattributes(self, name, value):
        self.attributes[name] = value

    def getattributes(self, name):
        if name in self.attributes:
            return self.attributes[name]
        else:
            return None


    def addChild(self, child):
        self.children.append(child)
        return self

    def getchildren(self):
        return self.children

    def addParent(self, parent):
        self.parents.append(parent)
        return self

    def setitemnumber(self, startnumber):
        self.itemnumber = startnumber
        for c in self.children:
            startnumber = c.setitemnumber(startnumber + 1)
        return startnumber

    def getitemnumber(self):
        return self.itemnumber


    def dump(self, pre):
        print(pre + str(self))
        for i in self.children:
            i.dump(pre + "    ")