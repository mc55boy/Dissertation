from pprint import pprint
import json


class JSONHandler:
    def getJSONModel(inputFile):
        parsedJSON = json.load(open(inputFile))
        print("list values: %s" % parsedJSON['neuralNet']['layers'])
        for 
        #pprint(parsedJSON)
