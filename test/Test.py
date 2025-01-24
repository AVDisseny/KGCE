from DataProcessorManager import DataProcessorManager

manager = DataProcessorManager("dataProcessorAVD.json")

manager.loadData()

manager.process()

manager.showInstances()





   