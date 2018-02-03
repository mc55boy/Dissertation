from pprint import pprint
import json
from collections import Counter

#def getLayers(layerJSON):
    #returnArray[][]

#def getHyperparameters(parameterJSON):



class JSONHandler:
    def readJSONModel(inputFile):
        return json.load(open(inputFile))
