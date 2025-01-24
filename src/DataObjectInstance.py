import hashlib
import re
from ThesaurusInstance import ThesaurusInstance
from SourceData import SourceData


class DataObjectInstance:

    _props = {}

    _instanceOf = None

    _built = False

    _uriGenerateFrom = []

    _activeRelation = True

    _deactivatedPropertyRelation=[]

    #trampa extendedSearch
    _extendedSearch =""

    def getExtendedSearch(self):
        return self._extendedSearch
    
    def addExtendedSearch(self, value):
        self._extendedSearch = self._extendedSearch + value+","
        
    #fin trampaExtendedSearch


    def __init__(self, props, fromObject):
        #trampaExtendedSearch
        if (fromObject.getName()=='Product'):
            self.addExtendedSearch(props['nombre'])
            self.addExtendedSearch(props['n_registro'])
        #fin trampaExtendedSearch
        self._props = props
        self._instanceOf = fromObject        
        self._built = False
        self._deactivatedPropertyRelation.clear()

    def addProp(self, propName):
        if propName not in self._props.keys():
            self._props[propName]=None
    

    def getPropNames(self):
        return self._props.keys()
    
    def hasActiveRelation(self):
        return self._activeRelation
    
    def hasActivePropertyRelation(self, propName):
        return propName not in self._deactivatedPropertyRelation
    
    def _deActivateRelation(self):
        self._activeRelation = False

    def _deActivatePropertyRelation(self, propName):
        self._deactivatedPropertyRelation.append(propName)

    def removeProperty(self, nameProp):
        if nameProp in self._props.keys():
            self._props.pop(nameProp)

    def addDataFromInstance(self, instance):
       
        for prop in instance.getPropNames():
            if prop!="id" and (prop in self._props.keys()):

                thisValue = self.getValueOf(prop)
                fromValue = instance.getValueOf(prop)

                if fromValue!=None:

                    if (thisValue == None):
                        self.setValueOf(prop, fromValue)
                    else:

                        if not isinstance(thisValue, list):
                            auxVal = self._props[prop]
                            self._props[prop]=[]
                            self._props[prop].append(auxVal)    
                            thisValue = self.getValueOf(prop)                    

                        if not isinstance(fromValue, list):
                            if fromValue not in thisValue:
                                self._props[prop].append(fromValue)
                        else:
                            for fromDataVal in fromValue:
                                if not isinstance(fromDataVal,list):
                                    if fromDataVal not in thisValue:
                                        self._props[prop].append(fromDataVal)
        
    def addValueToProp(self, prop, value):

        #self.setValueOf(prop, value)

        thisValue = self.getValueOf(prop)
        if isinstance(thisValue, list):
            thisValue.append(value)
            self.setValueOf(prop, thisValue)
        else:
            newValue = []
            newValue.append(thisValue)
            newValue.append(value)
            self.setValueOf(prop, newValue)


    def getExpressionFromPropValue(self, propName, expression):    
        result = ""

        patron = re.compile(expression)        
        match = patron.search(self.getValueOf(propName))
        if match!=None:
            result = self.getValueOf(propName)[match.start():match.end()]
        
        return result
    
    def updateWith(self, source):
        findData = True
        
        sourceWithDataInfo = self._instanceOf.getSourceWithDataInfo(source.getName())
        if sourceWithDataInfo!=None:
            
            propName = sourceWithDataInfo["dataValue"]

            propValue = self.getValueOf(propName)

            if "regexp" in sourceWithDataInfo.keys():
                regExp = sourceWithDataInfo["regexp"]
                patron = re.compile(regExp)   
                match = patron.search(propValue)
                if match!=None:
                    propValue = propValue[match.start():match.end()]
                else:
                    findData = False

            if findData:
                data = source.loadData(0,propValue)

                for propName in self._props.keys():
                    if propName!="URI":
                        prop = self._instanceOf.getPropertyByName(propName)
                        if prop.getSource() == source.getName():
                            defValue = data[prop.getValue()]
                            if isinstance(data[prop.getValue()], list):
                                if (len(data[prop.getValue()])>0):
                                    if isinstance(data[prop.getValue()][0], dict):                                   
                                        finalValue=[]
                                        for auxValue in data[prop.getValue()]:
                                            if 'lang' in auxValue.keys() and auxValue['lang']!="":    
                                                finalValue.append(auxValue['name']+"|@"+auxValue['lang']+"|")
                                        defValue = finalValue
                            
                            self.setValueOf(propName, defValue)


                    #if prop.getSource()==source.getName():


        
    def setURI(self, uri):
        self._props["URI"]=uri
        ##if ("c8f64250a5c8e9d0aa7463bb0ed90473" in uri):
          ##      print("hello2")

    def setURIFrom(self, propNames):
        self._uriGenerateFrom = propNames

    def getURI(self):
        return self._props["URI"]

    def getValueOf(self, propName):
        value = None
        if propName in self._props.keys():                      
            value = self._props[propName]

        return value
        
    def setValueOf(self, propName, value):

        #if self.getValueOf('P126 employed')!=None:
        #    if isinstance(self.getValueOf('P126 employed'), list) and propName=='P126 employed':
        #        print("hi")

        isThesaurusInstance = False

        if propName in self._props.keys():
            if (isinstance(value, ThesaurusInstance)):
                isThesaurusInstance = True

            if (isinstance(value, list)):
                if len(value)>0:
                    if isinstance(value[0], ThesaurusInstance):
                        isThesaurusInstance = True

            if isThesaurusInstance:
                if (self._instanceOf.getPropertyByName(propName).getRelatedTo()!=""):
                    self._deActivatePropertyRelation(propName)
                    #self._deActivateRelation() 

            self._props[propName] = value

            #if isinstance(self._props[propName],list):
            #    if isinstance(value,list):
            #        for dataVal in value:
            #            if not isinstance(dataVal, list):
            #                if dataVal not in self._props[propName]:
            #                    self._props[propName].append(dataVal)
            #    else:
            #        self._props[propName].append(value)
            #else:
            #   if isinstance(value,list):
            #        self._props[propName]=[]
            #       for dataVal in value:
            #            if not isinstance(dataVal, list):
            #                self._props[propName].append(dataVal)            
            #    else:
            #        self._props[propName] = value
    
    def getObject(self):
        return self._instanceOf
        
    def show(self):
        return self._props
    
        
    def showNTriples(self, type, references, file):

        #file.write("<------------ instance type : ("+self._instanceOf.getName()+") -----------> \n")

        selfURI = ''

        if isinstance(self.getURI(),list):
            selfURI = self.getURI()[0]
        else:
            selfURI = self.getURI()


        for typeAux in type:
            file.write("<"+selfURI +">\t<"+ references["type"] +">\t<"+typeAux+"> .\n")

        for propAux in self._props.keys():            
            s = "<"+selfURI+">"
            propObject = self._instanceOf.getPropertyByName(propAux)
            p=""
            lang=""
            if propObject!=None:
                p = propObject.getPredicate()
                lang = propObject.getLang()
        
            v = self.getValueOf(propAux)

            

            if (isinstance(v, ThesaurusInstance)):
                v = v.getURI()

            if (isinstance(v,list)):
                for value in v:
                    if (isinstance(value, list)):
                        break
                    if (isinstance(value, ThesaurusInstance)):
                        value = value.getURI()
                    value=str(value)
                    if value[0:4]=="http":
                        value = "<"+value.strip()+">"
                        value = value.replace("\"", "")        
                        if "@link" in value:
                            value = value.replace("|@link|", "")
                            value = "\""+ value + "\"@link"                         
                    else:
                        value = value.replace("\r","")
                        value = value.replace("\n","")
                        value = value.replace("\"", "")
                        value = value.replace("|@", "\"@")
                        # wikipedia
                        value = value.replace("|@link|","/link")
                        if value.strip()[-1:]=="|":
                            value = "\""+value.strip()[:-1]
                        else:
                            value = "\""+value.strip()+"\""

                    if lang!="":
                        value = value +"@"+lang

                    if (p.strip()!="" and value!="\"\""):
                        file.write(s+ "\t<"+ p +">\t"+ value+" .\n")
            else:   
                v = str(v)             
                if v[0:4]=="http":
                    v = "<"+v.strip()+">"
                    v = v.replace("\"", "")   
                    if "@link" in v:
                       v = v.replace("|@link|", "")
                       v = "\""+ v + "\"@link"                               
                else:
                    v = v.replace("\r","")
                    v = v.replace("\n","")
                    v = v.replace("\"", "")
                    v = v.replace("|@", "\"@")
                    if v.strip()[-1:]=="|":
                        v = "\""+v.strip()[:-1]
                    else:
                        v = "\""+v.strip()+"\""

                if lang!="":
                        v = v +"@"+lang
                    
                if (p.strip()!="" and v!="\"\""):
                    file.write(s+ "\t<"+ p +">\t")
                    #probar decodificar a ascii (ver API y probar en test.py no aqui)
                    file.write(v)
                    file.write(" .\n")

        #trampa extendedSearch
        if (self._extendedSearch!=''):
            file.write("<"+selfURI +">\t<http://extendedSearch>\t"+ "\"" + self._extendedSearch + "\" .\n")
            print("<"+selfURI +" ------ extended ----> " + self._extendedSearch)

        #fintrampa extendedSearch
            
        #file.write("<------------------------------------------------------------->")
    
    def __generateURIFromProps(self, propNames):   

        finalURI = ""
        isThesaurusLink=False
        for pName in propNames: 
            auxValue = self._props[pName]
            if isinstance(self._props[pName], ThesaurusInstance):   
                if len(propNames)>1:
                    auxValue = self._props[pName].getLabel()
                else:
                    finalURI = self._props[pName].getURI()
                    isThesaurusLink = True
            ## Check that auxValue is not a number, to get the encode without problems
            if not isinstance(auxValue, str):
                auxValue = str(auxValue)
            
            if not isThesaurusLink:
                finalURI = finalURI +hashlib.md5(auxValue.encode()).hexdigest()
    
        if isThesaurusLink:
            self._props["URI"] = finalURI
        else:
            self._props["URI"]  = self._instanceOf.getURIBase()+ finalURI
        
        if self._props["URI"] == 'http://data.arxiuvalencia.eu/production/4bae34b1dfe730592a822a11ad797d6d6591b21d8287d2d7a2fcb07b6c94b17f':
            print("here0")

        if self._props["URI"] == 'http://data.arxiuvalencia.eu/production/4bae34b1dfe730592a822a11ad797d6d9b5f7895dab4fa52d418ffc3dc3fdf31':
           print("here")

        if self._props["URI"] ==  'http://data.arxiuvalencia.eu/production/4bae34b1dfe730592a822a11ad797d6d15e05b98749751210458693e1c89e503':
            print("here2")

    def isBuilt(self):
        return self._built
    
    def setBuilt(self, built):        
        if built:
            self.__generateURIFromProps(self._uriGenerateFrom)
            self.setValueOf("id", self.getURI())
        self._built = built




        
