from pprint import pprint
import json
from collections import Counter

#def getLayers(layerJSON):
    #returnArray[][]

#def getHyperparameters(parameterJSON):



class JSONHandler:
    def readJSONModel(inputFile):
        return json.load(open(inputFile))

    def writeToJSON(outputFile, data):
        with open(outputFile, 'w') as outfile:
            json.dump(data, outfile, indent=4)
