import requests
import urllib3.exceptions
import http.client
from ThesaurusInstance import ThesaurusInstance

class ThesaurusTerm:
    _name=""
    _type =""
    _langAttribute="lang"
    _langValue="en"
    _urlBase=""
    _urlScheme=""
    _urlNarrowers=""
    _parentStartWord=""
    _instances = []
    _floorInstances = []
    _labelInstances = {}

    def __init__(self, sourceJSON,referenceURIs):
        self._name = sourceJSON["name"]
        if (sourceJSON["type"] in referenceURIs):
            self._type = referenceURIs[sourceJSON["type"]]
        else:
            self._type = sourceJSON["type"]
        self._langAttribute = sourceJSON["langAttribute"]
        self._langValue = sourceJSON["langValue"]
        self._urlBase = sourceJSON["urlBase"]
        self._urlScheme = sourceJSON["urlScheme"]
        self._urlNarrowers = sourceJSON["urlNarrowers"]
        self._parentStartWord = sourceJSON["parentStartWord"]

    def show(self):
        print("THESAURUSTERM type = "+self._type)
        print("name = "+self._name)
        print("langAttribute = "+self._langAttribute)
        print("langValue = "+self._langValue)
        print("urlBase   = "+self._urlBase)
        print("urlScheme    = "+self._urlScheme)
        print("urlNarrowers ="+self._urlNarrowers)
        print("parentStart  ="+self._parentStartWord)
        print("------------------------------")
    
    def getName(self):
        return self._name
    
    def getType(self):
        return self._type
    
    def getLangAttribute(self):
        return self._langAttribute
    
    def getLangValue(self):
        return self._langValue
    
    def getUrlBase(self):
        return self._urlBase
    
    def getUrlScheme(self):
        return self._urlScheme
    
    def getUrlNarrowers(self):
        return self._urlNarrowers
    
    def getParentStartWord(self):
        return self._parentStartWord
    
    def loadInstances(self):
        
        self._instances = []
        self._floorInstances = []

        responseBase = requests.get(self._urlBase + self._urlScheme + "&" + self._langAttribute +"="+self._langValue)
        
        data = responseBase.json()
        pos = 0

        print("hay "+str(len(data['topconcepts']))+" objetos")
        while (pos < len(data['topconcepts'])):
            labelParent = data['topconcepts'][pos]['label']
            if (labelParent.lower().startswith(self.getParentStartWord())):        
                print("processig thesuarusTerm " + str(pos))
                uriParent = data['topconcepts'][pos]['uri']
                parentInstance = ThesaurusInstance(uriParent,data['topconcepts'][pos]['label'],None, 0)
                #self._instances.append(parentInstance)
                self._addInstance(parentInstance)
                self.loadInstanceChilds(parentInstance,1)                     
            pos = pos +1                       
                

        
    def _prepareLabel(self, label):
        if type(label)==str:
            return label.strip().lower()
        else:
            return label
    
    def _addInstance(self, instance):
        self._instances.append(instance)
        self._labelInstances[self._prepareLabel(instance.getLabel())]=instance

    def _addFloorInstance(self, instance):
        self._floorInstances.append(instance)
        self._labelInstances[self._prepareLabel(instance.getLabel())]=instance

    def showLabels(self):
        for label in self._labelInstances.keys():
            print(label)

    def loadInstanceChilds(self, parent, pos):

        responseIter = requests.get(self._urlBase + self._urlNarrowers + parent.getURI() + "&" + self._langAttribute +"="+self._langValue)
        data = responseIter.json()

        #self._instances.append(parent)
        self._addInstance(parent)

        if len(data['narrower']) == 0:
            self._addFloorInstance(parent)
            #self._floorInstances.append(parent)

        for dato in data['narrower']:
            # Check parent-child recursion
            if dato['uri']!=parent.getURI():
                childInstance = ThesaurusInstance(dato['uri'], dato['prefLabel'], parent, pos)                      
                self.loadInstanceChilds(childInstance, pos + 1 )                       
                self._addInstance(childInstance)
            
            #self._instances.append(childInstance)
    
    def update(self):
        for instanceAux in self._instances:
            self._labelInstances[self._prepareLabel(instanceAux.getLabel())]=instanceAux
            
    def getInstanceWithLabel(self, label):
        label = label.lower()
        for key in self._labelInstances.keys():
            if label==key:
                return self._labelInstances[label]
        return None
            





