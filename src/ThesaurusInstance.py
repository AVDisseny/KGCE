class ThesaurusInstance:
    _uri =""
    _prefLabel=""
    _broader = []
    _narrower = []
    _level = 0

    def __init__(self, uri, prefLabel, broader, level):
        self._uri = uri
        self._prefLabel = prefLabel.strip().lower()
        self._broader.append(broader)
        self._level = level

    def setlevel(self, level):
        self._level = level
    
    def getLevel(self):
        return self._level
    
    def getLabel(self):
        return self._prefLabel
    
    def addNarrower(self, narrower):
        self._narrower.append(narrower)

    def getNarrowers(self):
        return self._narrower
    
    def getURI(self):
        return self._uri
    
    def getPrefLabel(self):
        return self._prefLabel
    


    
