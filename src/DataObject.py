from SourceData import SourceData
from ObjectProperty import ObjectProperty
from DataObjectInstance import DataObjectInstance
from ThesaurusInstance import ThesaurusInstance
import hashlib

class DataObject:
    _name=""
    _source=[]
    _type = []
    _uriBase=""
    _relatedTo=[]
    _properties=[]
    _thesaurusProperties=[]

    __sourceAux = []
    __relatedToAux = []

    _inverseRelationName=""
    _inverseRelationPredicate=""
    _instances = []
    _instancesURI = {}
    _sourcesWithData = {}
    # producto - produccion
    # antes de asignar la uri a la instacia en dataobjectinstance
    # se mira que no exista _inverse[producto.id]
    # si existe, la instancia no se crea y las entradas que no tiene la instancia ya creada se le son asginadas
    # sino existe, todo sigue igual y se añade en inverse la uri que referencia  (_inverse[producto]=produccion.uri)
    
    _inverse = {}

    def __init__(self, sourceJSON, referenceURIs):    

        self._type=[]

        self._inverse={}

        if "name" in sourceJSON.keys():
            self._name = sourceJSON["name"]    

        if "type" in sourceJSON.keys():
            if not isinstance(sourceJSON["type"], list):
                print("ERROR type of object "+self._name+" is not a list")
            else:
                for typeAux in sourceJSON["type"]:
                    typeName = typeAux["name"]
                    if typeName in referenceURIs:
                        self._type.append(referenceURIs[typeName])
                    else:
                        self._type.append(typeName)

        if "uriBase" in sourceJSON.keys():
            self._uriBase = sourceJSON["uriBase"]
        
        if "inverseRelationName" in sourceJSON.keys():
            self._inverseRelationName = sourceJSON["inverseRelationName"]

        if "inverseRelationPredicate" in sourceJSON.keys():
            if (sourceJSON["inverseRelationPredicate"] in referenceURIs):
                self._inverseRelationPredicate = referenceURIs[sourceJSON["inverseRelationPredicate"]]
            else:
                self._inverseRelationPredicate = sourceJSON["inverseRelationPredicate"]        
        
        self.__sourceAux=[]
        if ("source" in sourceJSON.keys()):
            for sAux in sourceJSON["source"]:                
                self.__sourceAux.append(sAux["name"])  
                if "dataValue" in sAux.keys():
                    self._sourcesWithData[sAux["name"]]=sAux

        self.__relatedToAux=[]
        if ("relatedTo" in sourceJSON.keys()):
            for rAux in sourceJSON["relatedTo"]:
                self.__relatedToAux.append(rAux["name"])

        self._properties=[]
        self._thesaurusProperties = []
        if ("properties" in sourceJSON.keys()):
            for prop in sourceJSON["properties"]:
                property = ObjectProperty(prop, referenceURIs)
                self._properties.append(property)
                if property.getRelatedThesaurusTerm()!="":
                    self._thesaurusProperties.append(property.getName())

    # trampa documents------------------------------------------
    def updateDocuments(self, dataBlock, documents):
        if self._name=="Product":
            start = (dataBlock-1)*100
            end = start + 100
            i=0
            auxInstance = self.getInstance(0)
            while i<end and (not isinstance(auxInstance, DataObjectInstance)):
                numRegistro = auxInstance.getValueOf("n_registro")
                numRegistro = self.formatDocumentSignature(numRegistro)
                if numRegistro!="" and numRegistro not in documents.keys():
                    documents[numRegistro]=""
                auxInstance = self.getInstance(i)
                i+=1
            #for i in range(start,end):
            #    auxInstance = self.getInstance(i)
            #    numRegistro = auxInstance.getValueOf("n_registro")
            #    numRegistro = self.formatDocumentSignature(numRegistro)
            #    if numRegistro!="" and numRegistro not in documents.keys():
            #        documents[numRegistro]=""

    def formatDocumentSignature(self, registro):
        formatted=""
        if "AVD-" in registro[0:4]:
            endDoc = registro.find("_")
            if endDoc>4:
                formatted = registro[0:endDoc]
        return formatted
    
    # fin trampa documents------------------------------------------

    def getSourceWithDataInfo(self, sourceName):
        if sourceName in self._sourcesWithData.keys():
            return self._sourcesWithData[sourceName]
        else:
            return None
        
    def getInverseRelationName(self):
        return self._inverseRelationName

    def getPropertyByName(self, name):
        for prop in self._properties:
            if prop.getName()==name:
                return prop
        return None
    
    def getURIBase(self):
        return self._uriBase
    
    def getInstanceWithURI(self, URI):
        if URI in self._instancesURI.keys():
            return self._instancesURI[URI]
        else:
            return None
    
    def show(self):
        print("OBJECT type = "+self._type)
        print("name = "+self._name)
        print("uriBase   = "+self._uriBase)
        print("inverseRelationName = "+self._inverseRelationName)
        print("inverseRelationPredicate ="+self._inverseRelationPredicate)        
        print(self._source)
        if self.hasSourceData():
            print("TIENE SOURCEDATAS")

        print(self._relatedTo)        
        for p in self._properties:
            p.show()
        print("------------------------------")

    def getName(self):
        return self._name
    
    def getSourceDatas(self):
        sDatas = []
        for source in self._source:
            if isinstance(source, SourceData):
                sDatas.append(source)

        return sDatas
    
    def hasSourceData(self):
        return len(self.getSourceDatas())>0
    
    def updateReferences(self,source, object, thesaurusTerm):

        self._source =  []

        # Link the SourceData instances from Source Tag
        for sAux in self.__sourceAux:
            for sourceD in source:
                if (sAux == sourceD.getName()):
                    self._source.append(sourceD)                    
                
        # Link the DataObject instances from Source tag
        for sAux in self.__sourceAux:
            for objectLink in object:
                if (sAux == objectLink.getName()):
                    self._source.append(objectLink)

        self._relatedTo = []

        # Link the DataObject instances with RelatedTo
        for rAux in self.__relatedToAux:
            for objectLink in object:
                if (rAux == objectLink.getName()):
                    self._relatedTo.append(objectLink)

        # Update the propierties references
        for prop in self._properties:
            prop.updateReferences(object, thesaurusTerm, self._properties)            
    
    def getData(self, dataBlock):

        hasData = False
        for sourceD in self.getSourceDatas():
            if sourceD.isPaged():            
                hasData = hasData or self.addInstances(sourceD.loadData(dataBlock))  

        for sourceD in self.getSourceDatas():  
            if sourceD.hasDataAttribute():
                for instance in self._instances:
                    instance.updateWith(sourceD)

        return hasData
    
    def generateDefaultInstance(self):
        props = {}
        for prop in self._properties:
            props[prop.getName()]=prop.getValue()

        return DataObjectInstance(props, self)
    
    def getPropertiesThatContainsInValue(self, word):
        propsFound=[]
        word = word.lower()+"."
        for prop in self._properties:
            if (word in prop.getValue().lower()):
                propsFound.append(prop)
        
        return propsFound

    def getPropertiesRelatedWith(self, relatedName):
        propsFound=[]
        relatedName = relatedName.lower()
        for prop in self._properties:
            if (relatedName in prop.getRelatedTo().lower()):
                propsFound.append(prop)
        
        return propsFound
    
    def connectInstancesWith(self, source):
   
        sourceObject = source.getObject()
        #if source.getValueOf("label")=="Yiropa":
         #   print("hello")

        #if self._name=="Organization": 
        # Este vendra bien para ver el timestamp, habra que mirar si la propiedad es la del timestamp
        #if source._instanceOf.getName()=="E12_Production":
         #   print("hello")
        propertiesName = sourceObject.getPropertiesRelatedWith(self.getName())

        foundListProperty = False
        pos = 0        

        while pos<len(propertiesName) and ( not foundListProperty ):
            
            sourcePropName = propertiesName[pos].getName()
            sourcePropValue = source.getValueOf(sourcePropName)
           
            if sourcePropValue=="":
                source.removeProperty(sourcePropName)
            else:
                if isinstance(sourcePropValue, list):
                    finalValues = []
                    for auxPropValue in sourcePropValue:
                        strPropValue = str(auxPropValue)
                        if self._uriBase+strPropValue in self._instancesURI.keys():                            
                            finalValues.append(self._uriBase+ strPropValue)                                                 
                    source.setValueOf(sourcePropName, finalValues)
                            
                else:
                    sourcePropValue = str(sourcePropValue)
                    if self._uriBase+sourcePropValue in self._instancesURI.keys():
                        source.setValueOf(sourcePropName, self._uriBase+ sourcePropValue )    
                    else:
                        source.removeProperty(sourcePropName)

            pos = pos + 1
            

    def addInstancesFromSource(self, source):

        if type(source)==int:
            return

        if not source.hasActiveRelation():
            return                
        
        instancesCreated = []

        propID = self.getPropertyByName("id")
        generateFrom = propID.getGenerateFrom()
        
        sourceObject = source.getObject()    

        propertiesName = self.getPropertiesWithGeneratedFrom(sourceObject.getName())

        foundListProperty = False
        pos = 0



        ## break en 250
        ## a raiz de desarrollar el poner self_inverse para que no hayan varias production de un mismo product
        ## se ve que una instancia de P108 has produced de la clase "Production" tiene "auto" de valor, en lugar de la uri del producto.
        ## cosas raras:
        ## 1: la propiedad id de la instancia de producto fuente tiene dos valores, la uri y "auto"
        ## 2: propertiesName tiene como valores varias propiedaes, incluidas las que no son source de Producto (como took_place, etc.)
        ## el problema a solucionar es primero, porque product.id tiene dos valores, cuando sólo debería de tener 1

        createInstance = False

        while pos<len(propertiesName) and ( not foundListProperty ):
            propName = propertiesName[pos]
       
            sourcePropName = self.getPropertyByName(propName).getValue()[len(sourceObject.getName())+1:]  

            sourcePropValue = source.getValueOf(sourcePropName)
            sourcePropIsRelated = sourceObject.getPropertyByName(sourcePropName).getRelatedTo()

            if type(sourcePropValue)==list and (not self.getPropertyByName(propName).getRelatedTo()) and source.hasActivePropertyRelation(sourcePropName):
 
                foundListProperty = True
                propPos = 0
                
                instanceAux = None                

                for propValue in sourcePropValue:

                    if propValue=='':
                        break

                    if isinstance(propValue, list):
                        if propValue[0]=='':
                            break


                    #debuggerarlo y ver la URI que da error, que es la que necesitamos parar y hacer stop aquí, antes de llegar a la siguiente

                    if instanceAux==None:
                        instanceAux = self.generateDefaultInstance()                                         
                        createInstance = True                        
                    else:
                        createInstance = False
                    
                    #instanceAux = None

                    instanceAux.setURIFrom(generateFrom)   

                    if createInstance:
                        instanceAux.setValueOf(propName,[])

                    if isinstance(propValue, dict):
                        if propValue['lang']!="":                            
                            instanceAux.addValueToProp(propName, propValue['name']+"\"@"+propValue['lang'])          
                            #instanceAux.setValueOf(propName, propValue['name']+"\"@"+propValue['lang'])          
                    else:
                        instanceAux.addValueToProp(propName, propValue)                 
                        #instanceAux.setValueOf(propName, propValue)

                    if createInstance:                
                        for pName in propertiesName:
                            if pName != propertiesName[pos]:
                                newPropName = self.getPropertyByName(pName).getValue()
                                if sourceObject.getName() in newPropName:
                                    newPropName = self.getPropertyByName(pName).getValue()[len(sourceObject.getName())+1:]
                                if newPropName.lower() == "id":
                                    instanceAux.setValueOf(pName, source.getURI())
                                else:
                                    instanceAux.setValueOf(pName, source.getValueOf(newPropName))


                        # Check the existence of another instance uri with the same inverse relation
                        # in this case the new instance is not created, and the properties of instanceAux
                        # goes to the previous instance. Anyway it is created and added to the instances list
                        # of the data object

                        #inverseValue = instanceAux.getValueOf(self.getInverseRelationName())

                        #if inverseValue not in self._inverse.keys():                        
                        instanceAux.setBuilt(True)        
                            
                        #self._inverse[inverseValue] = instanceAux.getURI()

                        ##modificated
                        for pName in propertiesName:                               
                            newPropName = self.getPropertyByName(pName).getValue()[len(sourceObject.getName())+1:]
                            inversePropName = self.getPropertyByName(pName).getInverse()
                            if inversePropName!="" and (not source.getValueOf(newPropName) in self._inverse.keys())!="":
                                self._inverse[source.getValueOf(newPropName)]=source.getURI()    
                                source.setValueOf(inversePropName,instanceAux.getURI())                    
                        ##modifcated

                        if createInstance:
                            instancesCreated.append(instanceAux)
                            self.addInstance(instanceAux)

                    sourcePropValue[propPos] = instanceAux.getURI()
                    """
                    else:                        
                        existingInstance = sourceObject.getInstanceWithURI(inverseValue)
                        if existingInstance is None:
                            print("hello")
                        existingInstance.addDataFromInstance(instanceAux)
                    """

                    propPos = propPos + 1
                #source.setValueOf(self._inverseRelationName, sourcePropValue)
            else:
                pos = pos + 1                                                   

        # mete en las propstolink aquellas propiedades de la fuente (menos el id) que tienen relación con la nueva instancia
        # luego a esas propiedades les metera la uri de esta instancia comprobando si en el fuente
        # el related es el nombre del objeto de la nueva instancia


        if not foundListProperty:
            sourcePropsToLink = []
            instanceAux = self.generateDefaultInstance()
            instanceAux.setURIFrom(generateFrom)

            previouslyInversed = False
            instanceHasData = False

            for pName in propertiesName:                               
                newPropName = self.getPropertyByName(pName).getValue()[len(sourceObject.getName())+1:]
                if newPropName.lower() == "id":
                    instanceAux.setValueOf(pName, source.getURI())
                    inversePropName = self.getPropertyByName(pName).getInverse()
                    if inversePropName!="" and (not source.getValueOf(newPropName) in self._inverse.keys())!="":
                        self._inverse[source.getValueOf(newPropName)]=source.getURI()
                        sourcePropsToLink.append(inversePropName) 
                    else:
                        previouslyInversed = True
                else:
                    if source.getValueOf(newPropName)!=None:
                        if source.getValueOf(newPropName)!='':
                            instanceAux.setValueOf(pName, source.getValueOf(newPropName))
                            sourcePropsToLink.append(newPropName)         
                            instanceHasData = True      

            # Check the existence of another instance uri with the same inverse relation
            # in this case the new instance is not created, and the properties of instanceAux
            # goes to the previous instance. Anyway it is created and added to the instances list
            # of the data object
            #inverseValue = instanceAux.getValueOf(self.getInverseRelationName())
            #if inverseValue not in self._inverse.keys() or inverseValue==None: 
            if not previouslyInversed and instanceHasData:
                instanceAux.setBuilt(True)   
                #self._inverse[inverseValue] = instanceAux.getURI()
                instancesCreated.append(instanceAux)            
                #instanceAux.setValueOf(self._inverseRelationName, source.getURI())
                self.addInstance(instanceAux)
                for sourcePName in sourcePropsToLink:
                    if sourceObject.getPropertyByName(sourcePName)!=None:
                        if sourceObject.getPropertyByName(sourcePName).getRelatedTo()==self.getName():
                            source.setValueOf(sourcePName, instanceAux.getURI())


        self._instances.extend(instancesCreated)

        return instancesCreated
    
    def showInstances(self, references, file):
        for uri in self._instancesURI.keys(): 
            instanceAux = self._instancesURI[uri]
            if self._type!="":
                instanceAux.showNTriples(self._type, references, file)

    def clearInstances(self):
        self._instances=[]
        self._instancesURI={}

    
    def getPropertiesWithGeneratedFrom(self, generatorName):

        generated =[]
        for prop in self._properties:
            if generatorName.lower()+"." in prop.getValue().lower():
                generated.append(prop.getName())
        
        return generated
    
    def addInstances(self, instances):    
        primera = True  
        for inst in instances:
           # if (self.getName()=="Product"):
           #     if (inst["acf"]["material"]=="" or inst["acf"]["material"]==None):
           #         print("hello")
                
            instanceAux = DataObjectInstance(self.getPropertiesOfInstace(inst), self)

           # if (self.getName()=="Product"):
            #    if (instanceAux.getValueOf("nombre")=="Yiropa"):
             #       print("hello2");

            idValue = instanceAux.getValueOf("id")

            if idValue == "auto":
                instanceAux.setURI (idValue)
            else:
                instanceAux.setURI(self._uriBase + str(idValue))

            self.linkInstanceToThesuarusTerm(instanceAux)

            self._instances.append(instanceAux)
            self.addInstance(instanceAux)     
    
        #self._instances.extend(instances)                
        return len(instances)>0
    


    def addInstance(self, instance):
        if instance.getURI() in self._instancesURI:
            self._instancesURI[instance.getURI()].addDataFromInstance(instance)
        else:
            self._instancesURI[instance.getURI()]=instance
        


    def getNumInstances(self):
        return len(self._instances)
    
    def getInstance(self, index):
        if (index>=0 and index<len(self._instances)):
            return self._instances[index]
        else:
            return 0
        
    def showInstanceData(self, index):
        print(self._instances[index].show())
    
    def getPropertiesOfInstace(self, instance):

        props = {}

        #instance = self.getInstance(index)

        if instance!=0:
            for auxProp in self._properties:
                propKey = auxProp.getPropertyKey()

                if propKey!="":
                    propKeys = auxProp.getPropertyKeys()
                    if propKey in instance.keys():                   
                        if len(propKeys) == 1:
                            props[auxProp.getName()] = instance[propKeys[0]]
                        elif len(propKeys) == 2:
                            props[auxProp.getName()] = instance[propKeys[0]][propKeys[1]]
                        elif len(propKeys) == 3:
                            if isinstance(propKeys[2],list):
                                props[auxProp.getName()] = instance[propKeys[0]][propKeys[1]][int(propKeys[2])]
                            else:
                                props[auxProp.getName()] = instance[propKeys[0]][propKeys[1]][propKeys[2]]
                
                    if auxProp.getName() not in props.keys():
                        props[auxProp.getName()]=""
                    else:
                        props[auxProp.getName()] = auxProp.formatValue(props[auxProp.getName()])

                else:
                    props[auxProp.getName()] = ""
                        
        
        return props
    
    
    #el problema del tesauro es que cuando lee de archivo parce que no lee bien
    
    def linkInstanceToThesuarusTerm(self, instance):
        for propName in self._thesaurusProperties:
            if instance.getValueOf(propName)!="":
                property = self.getPropertyByName(propName)
                if property!=None:
                    term = property.getRelatedThesaurusTerm()[0]
                    theInstances = []
                    if type(instance.getValueOf(propName))==str:
                        foundInstance = term.getInstanceWithLabel(instance.getValueOf(propName).lower())
                        if foundInstance!=None:
                            theInstances.append(foundInstance)                        
                    else:
                        nPos = 0
                        while nPos<len(instance.getValueOf(propName)):  
                            if type(instance.getValueOf(propName)[nPos])==ThesaurusInstance:
                                foundInstance = term.getInstanceWithLabel(instance.getValueOf(propName)[nPos].getPrefLabel())   
                            else:                     
                                foundInstance = term.getInstanceWithLabel(instance.getValueOf(propName)[nPos].strip().lower())
                            if foundInstance!=None:                       
                                theInstances.append(foundInstance) #term.getInstanceWithLabel(instance.getValueOf(propName)[nPos].lower()))
                            nPos = nPos + 1
                    if len(theInstances)>0:
                        instance.setValueOf(propName,theInstances)
                        #trampa extendedsearch
                        if propName in ['tecnica','material']:
                            for v in theInstances:
                                instance.addExtendedSearch(v.getPrefLabel())
                        #fin trampaExtendedSearch


    
    def getRelatedTo(self):
        return self._relatedTo
    
    def isObtainedFrom(self, object):
        if object in self._source:
            return True
        else:
            return False
                 






            
        








        

