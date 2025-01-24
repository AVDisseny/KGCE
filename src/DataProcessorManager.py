
import json
import pickle
import os.path

from SourceData import SourceData
from ThesaurusTerm import ThesaurusTerm
from DataObject import DataObject

REFERENCE_NAME="name"
REFERENCE_URI = "uri"

THESAURUS_DATA_FILE = "thesaurus.dat"


class DataProcessorManager:
    """
    A class that represents a manager for process data to update kwnoledge 
    graph (KG) 
    The main function of this manager is:
    1. Read data from a datasource.
    2. Process the data according a specification file in JSON format.
    3. Generate a file in N3 format with the content to update the KG.

    Attributes
    ----------
    _JSONDataFile: str
        the path of the specification file in JSON format
    _referenceURIS: dictionary
        a dictionary (str:str) . The code of a reference URI (key) and the real URI (value)
    -sourceData : list
        a list with SourceData instances with all the data sources referenced in the specification file
    _thesaurusTerm: list
        a list with ThesaurusTerm instances whit all the terms referenced in the specification file
    _dataObject: list
        a list with the DataObject instancess with all the objects referenced in the specification file

    Methods
    -------
    __init(jsonData)__
        Create a DataProcessorManager instance by loading the specification file

    loadData(reloadThesaurus)
        Load the specification file and initialized the properties of the DataProcessorManager instance
        

    process(None)
        Create instances of DataObjectInstance class related with the DataObject instances inside _dataObject list
        These instances data are obtained from the source data and following the specification file.

    
    """

    _JSONDataFile =""
    _referenceURIs = {}
    _sourceData = []
    _thesaurusTerm = []
    _dataObject=[]       

    #trampa documents
    _documents={}
    _documentObject = None
    _productObject = None
    #fin trampa documents

    #trampa alternativesearch
    
    #fin trampa alternativesearch

    def __init__(self, jsonData):
        self.JSONDataFile = jsonData
        #self._loadData()
    
    def loadData(self, reloadThesaurus=True):

        with open(self.JSONDataFile) as f:
            p = json.load(f)

            # Load the reference URIs
            for ref in p["DataProcessor"]["referenceURIs"]:
                self._referenceURIs[ref[REFERENCE_NAME]]=ref[REFERENCE_URI]
                       
            # Load the source data
            for sData in p["DataProcessor"]["sourceData"]:
                self._sourceData.append(SourceData(sData))   
                self._sourceData[len(self._sourceData)-1].show()

            # Load the ThesaurusTerms
            existsThesaurusFile = False
            if reloadThesaurus:
                existsThesaurusFile = os.path.isfile(THESAURUS_DATA_FILE)

            if existsThesaurusFile:
                pickle_file = open("thesaurus.dat","rb")
                self._thesaurusTerm = pickle.load(pickle_file)
                pickle_file.close()
                for thesaTerm in self._thesaurusTerm:
                    thesaTerm.update()
            else:
                for tRef in p["DataProcessor"]["ThesaurusTerms"]:
                    term = ThesaurusTerm(tRef, self._referenceURIs)
                    term.loadInstances()
                    self._thesaurusTerm.append(term)    
                    term.showLabels()      

                pickle_out = open("thesaurus.dat", "wb")
                pickle.dump(self._thesaurusTerm, pickle_out)
                pickle_out.close()

            # Load the DataObjects
            for tObj in p["DataProcessor"]["Objects"]:
                self._dataObject.append(DataObject(tObj,self._referenceURIs))

            # Update the DataObjects and ObjectProperties references
            for tObj2 in self._dataObject:
                tObj2.updateReferences(self._sourceData, self._dataObject,self._thesaurusTerm)
    

    ###
    ##
    ## añadir prefijo baseuri en fabricationplace??
    ## no olvidar que esta prop debería de ser no visible
    ##
    ##

    def process(self):
        processedRelatedObjects = []

        for object in self._dataObject:

            #trampa documents------------------
            if object.getName()=="Document":
                self._documentObject=object

            if object.getName()=="Product":
                self._productObject = object

            if object.getName()=="E57_Material":
                print("stop")
            #fin trampa -----------------------

            #if object.getName()=="Object":
             #   print("hello")
                
            dataBlock = 1            
    
            if (object.hasSourceData()):
                object.clearInstances()
                dataBlock = 1

                while object.getData(dataBlock):
                    print("processing data ")
                    print(object.showInstanceData(0+(dataBlock-1)*100))                   
                    dataBlock = dataBlock +1
                    #trampa para documentos
                    object.updateDocuments(dataBlock-1, self._documents)               

            print("ENTRANDO CHECK CON DATABLOCK="+str(dataBlock)+" EN OBJECT "+object.getName())    
            
            for relatedObject in object.getRelatedTo():        

                if relatedObject.getName()=="Organization" and object.getName()=="E12_Production":
                    print("h")


                print("processing related object "+relatedObject.getName())
 
                isRelated = relatedObject.isObtainedFrom(object)
                isProcessed = relatedObject.getName() in processedRelatedObjects

                if (isRelated or relatedObject.hasSourceData()): #and (not isProcessed):
                    if relatedObject.hasSourceData() or isProcessed:
                        print("is processed with "+str(object.getNumInstances()))
                        for i in range(0, object.getNumInstances()):                            
                            relatedObject.connectInstancesWith(object.getInstance(i))
                            print("is processed with instance "+str(i))
                    else:
                        relatedObject.clearInstances()
                        print("is not processed with  "+str(object.getNumInstances()))
                        # a las que no tienen nada tn time-span les pone una isntancia --- la misma
                        # falta ver que hace con las que tiene
                        for i in range(0, object.getNumInstances()):
                            if (relatedObject.getName()=="E52_Time-Span"):
                                if (object.getInstance(i).getValueOf("P4 hastimespan"))!=None:
                                    if (object.getInstance(i).getValueOf("P4 hastimespan"))!='':
                                        print("got ya")
                            relatedObject.addInstancesFromSource(object.getInstance(i))
                            print("is not processed with instance "+str(i))                       
                    print("append to related")
                    processedRelatedObjects.append(relatedObject.getName())
            
            print("salir del for");
        
        #trampa documents----------------------------------
        for doc in self._documents.keys():       
            uriDoc = self.getDocumentInstance(doc)
            if uriDoc!="":
                self._documents[doc]=uriDoc

        num = 0
        for num in range(0, self._productObject.getNumInstances()):
            prodInst = self._productObject.getInstance(num)

            imagenes = prodInst.getValueOf("imagen")
            if isinstance(imagenes,list):
                signatureDoc = self.formatDocumentSignature(prodInst.getValueOf("n_registro"))
                if signatureDoc in self._documents.keys():
                    uriDoc = self._documents[signatureDoc]                                        
                    if uriDoc!="":
                        if len(imagenes)>0:
                            instDoc = self._documentObject.getInstanceWithURI(uriDoc)
                            if instDoc!=None:
                                currentValue = instDoc.getValueOf("P65_Shows_VisualItem")
                                if not isinstance(currentValue, list):
                                    currentValue = [imagenes[0]]
                                else:
                                    currentValue.append(imagenes[0])
                                instDoc.setValueOf("P65_Shows_VisualItem", currentValue)
      

        

                        
        #fin trampa documents--------------------------

    def showInstances(self):

        #trampa extendedSearch
        organization = None
        tipology = None
        production = None
        for obj in self._dataObject:
            if obj.getName()=="Organization":
                organization = obj
            if (obj.getName()=="Object"):
                tipology = obj
            if (obj.getName()=='E12_Production'):
                production = obj
        #fin trampa


        f = open("instances.rdf", "w", encoding="utf-8")

        for object in self._dataObject:
            #trampa extendedSearch
            if (object.getName()=="Product"):
                numInstances = object.getNumInstances()
                for n in range(0, numInstances-1):
                    instance = object.getInstance(n)
                    prod = instance.getValueOf("production")
                    prodInst = production.getInstanceWithURI(prod)
                    if prodInst!=None:
                        orgURI = prodInst.getValueOf("P14 carried out byO")
                        if orgURI!=None:
                            for uOrg in orgURI:
                                orgInst = organization.getInstanceWithURI(uOrg)
                                if (orgInst!=None):
                                    instance.addExtendedSearch(orgInst.getValueOf("nombre"))
                    typo = instance.getValueOf("tipologia")
                    if (typo!=None):
                        for typoU in typo:
                            objInst = tipology.getInstanceWithURI(typoU)
                            if objInst!=None:
                                instance.addExtendedSearch(objInst.getValueOf("label"))



            #fin trampa
            object.showInstances(self._referenceURIs, f)

        f.close()
                               
        print("END processing")


    #trampa documents
    def getDocumentInstance(self, signatura):        
        numDocs = self._documentObject.getNumInstances()
        uri = ""
        auxDoc = 0
        while auxDoc<numDocs and (uri==""):            
            found = (self._documentObject.getInstance(auxDoc).getValueOf("signatura")==signatura)            
            if found:
                uri = self._documentObject.getInstance(auxDoc).getURI()
            auxDoc = auxDoc + 1
        return uri
    
    def formatDocumentSignature(self, registro):
        formatted=""
        if "AVD-" in registro[0:4]:
            endDoc = registro.find("_")
            if endDoc>4:
                formatted = registro[0:endDoc]
        return formatted
        







            

                
                




        

