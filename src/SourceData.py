import requests
import json
import os.path

STATUS_OK = 200
STATUS_NOT_FOUND = 400

class SourceData:

    _name =""
    _url = ""
    _paged = False
    _pageAttribute= "page"
    _fromPage = 1
    _toPage = 0
    _itemsPerPageAttribute = "per_page"
    _itemsPerPageValue = 100
    _data = ""
    _dataAttribute = ""
    _file =""

    NO_DATA = ""

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def __init__(self, sourceJSON):
        self._name = sourceJSON["name"]
        self._url = sourceJSON["url"]
        if "paged" in sourceJSON.keys():
            self.setPagedAttribute(sourceJSON["paged"]["pageAttribute"])
            self.setPagedFrom(int(sourceJSON["paged"]["fromPage"]))
            self.setToPage(int(sourceJSON["paged"]["toPage"]))
            self.setItemsPerPageAttribute(sourceJSON["paged"]["itemsPerPageAttribute"])
            self.setItemsPerPageValue(int(sourceJSON["paged"]["itemsPerPageValue"]))
            self.setPaged(True)
        else:
            self.setPaged(False)

        if "data" in sourceJSON.keys():
            self._data = sourceJSON["data"]
            self._dataAttribute = sourceJSON["data"]["dataAttribute"]

        if "file" in sourceJSON.keys():
            self._file = sourceJSON["file"]            

    def getName(self):
        return self._name
    
    def setPaged(self, isPaged):
        self._paged = isPaged
    
    def isPaged(self):
        return self._paged
    
    def setURL(self, url):
        self._url = url

    def getURL(self):
        return self._url
    
    def getData(self):
        return self._data
    
    def getDataAttribute(self):
        return self._dataAttribute
    
    def setPagedAttribute(self, pageAttribute):
        self._pageAttribute = pageAttribute

    def getPagedAttribute(self):
        return self._pageAttribute

    def setPagedFrom(self, fromPage):
        if (fromPage==""):
            fromPage="0"
        self._fromPage = int(fromPage)

    def getPageFrom(self):
        return self._fromPage

    def setToPage(self, toPage):
        if (toPage==""):
            toPage ="0"
        self._toPage = int(toPage)

    def getToPage(self):
        return self._toPage

    def setItemsPerPageAttribute(self, itemsAtt):
        self._itemsPerPageAttribute = itemsAtt

    def getItemsPerPageAttribute(self):
        return self._itemsPerPageAttribute

    def setItemsPerPageValue(self, value):
        self._itemsPerPageValue=value

    def getItemsPerPageValue(self):
        return self._itemsPerPageValue
    
    def isOutOfPage(self, numPage):
        out = False
        if (self.isPaged()):
            if (self.getToPage()>0 and self.getToPage()<numPage):
                out = True
            
            if (self.getPageFrom()>0 and self.getPageFrom()>numPage):
                out = True

        return out
    
    def hasDataAttribute(self):
        return self._dataAttribute!=""
    
    def getDattaAttribute(self):
        return self._dataAttribute
    
    def getFinalURL(self, numPage, dataValue=""):

        finalURL = self.NO_DATA

        if dataValue!="":
            dataValue = str(dataValue)

# entra en isPaged aunque no es Paged, hay que revisar quien marca setPaged (aunque tiene valores, pare tema de objetos inicialización incorrecta)
        if (not self.isOutOfPage(numPage) or self._data!=""):               
            finalURL = self._url            
            joinCharacter="&"

            if "?" not in finalURL:
                joinCharacter = "?"

            if (self.isPaged()):
                 finalURL = finalURL + joinCharacter + self.getPagedAttribute() + "=" +str(numPage)
                 if (self.getItemsPerPageValue()>0):
                      finalURL = finalURL + "&" + self.getItemsPerPageAttribute() + "=" +str(self.getItemsPerPageValue())
            if (self._data !=""):
                if self._dataAttribute=="/":
                    finalURL = finalURL + "/" + dataValue
                else:
                    finalURL = finalURL + joinCharacter + self._dataAttribute + "=" + dataValue
        return finalURL
    
    def show(self):
        print("sourcedata")
        print("name = "+self._name)
        print("url  = "+self._url)
        print("pageAttribute = "+self.getPagedAttribute())
        print("from page = "+str(self.getPageFrom()))
        print("to page   = "+str(self.getToPage()))
        print("ItemsPerPageAttribute = "+self.getItemsPerPageAttribute())
        print("ItemsPerPageValue     = "+str(self.getItemsPerPageValue()))
    
    def loadData(self, dataBlock=1, dataValue=""):

        data = []

        if dataValue!="":
            dataValue = str(dataValue)
       
        if self._file!="":
            if os.path.isfile(self._file):
                data = self.getContent(dataValue)

        if len(data)==0:       
            url = self.getFinalURL(dataBlock, dataValue)

            if (url!=self.NO_DATA):
                response = requests.get(url)
                if (response.status_code == STATUS_OK):
                    data = response.json()
                    print("LOADING DATABLOCK = " + str(dataBlock) + " --> (" +str(len(data))+") --> "+url)   
                if self._data!="" and self._file!="":                    
                    with open(self._file, 'a', encoding='utf-8') as f:
                        f.write('<'+dataValue+'>\n')        
                        adaptedData = json.dumps(data)
                        """
                        adapteData = str(data)
                        adaptedData = adaptedData.replace("\'","\"")
                        adaptedData = adaptedData.replace("True","true")
                        adaptedData = adaptedData.replace("False","false")
                        """
                        f.write(adaptedData+'\n')
                        f.write('</'+dataValue+'>\n')



        return data
    
    def getContent(self, uri):
        with open(self._file, 'r',encoding='utf-8') as fp:
            data = ""
            headFound = False
            tailFound = False
            headLine = 0
            startTag = "<"+uri+">\n"
            endTag = "</"+uri+">\n"
            for l_no, line in enumerate(fp):
                # search string
                if (not headFound) and ( startTag in line):
                    headFound = True
                    headLine = l_no

                if (not tailFound) and ( endTag in line):
                    tailFound = True
                    break
                
                if (l_no > headLine) and headFound:                                   
                    data = data + line
        
        if data=="":
            return {}
        else:
            return json.loads(data)
        
    




