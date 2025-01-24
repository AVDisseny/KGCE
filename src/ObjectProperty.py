class ObjectProperty:
    _name = ""
    _predicate = ""
    _value = ""
    _type = ""
    _relatedToTesauroTerm = ""
    _sourceFor = []
    _relatedTo = ""    
    _useRegularExpression = ""
    _generateFrom =[]
    _source =""
    _inverse =""
    _lang=""

    _sourceForAux = []
    _relatedToAux = ""
    _relatedToTesauroTermAux =""

    REGULAR_EXPRESSION_URL = "URL"
    REGULAR_EXPRESION_STRING_CSV = "STRING_CSV"

    TYPE_ARRAY = "ARRAY"

    def __init__(self, sourceJSON, referenceURIs):
        if ("name" in sourceJSON.keys()):
            self._name = sourceJSON["name"]
        
        if "predicate" in sourceJSON.keys():
            if (sourceJSON["predicate"] in referenceURIs):
                self._predicate = referenceURIs[sourceJSON["predicate"]]
            else:
                self._predicate = sourceJSON["predicate"]   

        if "source" in sourceJSON.keys():
            self._source = sourceJSON["source"]
        
        if "value" in sourceJSON.keys():
            self._value = sourceJSON["value"]

        if "inverse" in sourceJSON.keys():
            self._inverse = sourceJSON["inverse"]

        if "generateFrom" in sourceJSON.keys():
            self._generateFrom = []
            for generateF in sourceJSON["generateFrom"]:
                self._generateFrom.append(generateF["name"])

        if "type" in sourceJSON.keys():
            if (sourceJSON["type"] in referenceURIs):
                self._type = referenceURIs[sourceJSON["type"]]
            else:
                self._type = sourceJSON["type"]
        
        if "relatedToTesauroTerm" in sourceJSON.keys():
            self._relatedToTesauroTermAux = sourceJSON["relatedToTesauroTerm"]

        if "relatedTo" in sourceJSON.keys():
            self._relatedToAux = sourceJSON["relatedTo"]

        if "useRegularExpression" in sourceJSON.keys():
            self._useRegularExpression = sourceJSON["useRegularExpression"]

        if "lang" in sourceJSON.keys():
            self._lang=sourceJSON["lang"]

        self.__sourceForAux=[]
        if ("sourceFor" in sourceJSON.keys()):
            for sFAux in sourceJSON["sourceFor"]:
                self.__sourceForAux.append(sFAux["name"])

    def getInverse(self):
        return self._inverse
    
    def show(self):
        print("PROPERTY name = "+self._name+" predi="+self._predicate+" value = "+self._value)
        print(self._sourceFor)

    def getName(self):
        return self._name
    
    def getValue(self):
        return self._value
    
    def getGenerateFrom(self):
        return self._generateFrom
    
    def getUseRegularExpression(self):
        return self._useRegularExpression
    
    def getRelatedThesaurusTerm(self):
        if self._relatedToTesauroTerm=="":
            return self._relatedToTesauroTermAux
        else:
            return self._relatedToTesauroTerm
        
    def getRelatedTo(self):
        if self._relatedTo=="":
            return self._relatedTo
        else:
            return self._relatedToAux
    
    def getLang(self):
        return self._lang
        
    def getSource(self):
        return self._source
    
    def getPropertyKey(self):
        startPos = self._value.find("[")+2
        endPos = self._value.find("]")-1

        return self._value[startPos:endPos]
    
    def getPredicate(self):
        return self._predicate
    
    def getPropertyKeys(self):

        keys = []
        startPos = self._value.find("[")+2
        endPos = self._value.find("]")-1

        while startPos!=-1:
            keys.append(self._value[startPos:endPos])
            startPos = self._value.find("[", startPos)
            if (startPos!=-1):
                startPos = startPos + 2
                endPos = self._value.find("]", startPos)-1
        
        return keys

            


    def updateReferences(self, object, thesaurusTerm, properties):        
        
        # Link the objects instances in relatedTo tag
        self._relatedTo= []
        for auxRelated in self._relatedToAux:
            for objectLink in object:
                if (auxRelated == objectLink.getName()):
                    self._relatedTo.append(objectLink)

        # Link the thesaurusTerm instances in relatedToTesauroTerm tag
        self._relatedToTesauroTerm = []        
        for termLink in thesaurusTerm:
            if self._relatedToTesauroTermAux == termLink.getName():
                self._relatedToTesauroTerm.append(termLink)

        # Link the ObjectProperty instances in sourceFor tag
        self._sourceFor = []
        for auxSource in self.__sourceForAux:
            for auxProp in properties:
                if (auxSource == auxProp.getName()):
                    self._sourceFor.append(auxProp)

    def formatValue(self, value):

        result = value

        if self._useRegularExpression == self.REGULAR_EXPRESSION_URL:
            result = self.formatRegularExpressionURL(value)

        return result
    
        
    def formatRegularExpressionURL(self, value):

        result = []

        startPos = value.find("http");
        endPos = value.find(" ", startPos)

        while (startPos!=-1):
            result.append(value[startPos:endPos])
            startPos = value.find("http",startPos+2)
            endPos = value.find(" ",startPos)
        
        return result
    
    

        
        
    

        

