import httpClient as HTTPServices
import os
import tarfile
import netHandler as netServices
import JSONHandler as JSONHandler
#multilayerTrain()

def downloadData(datasetName):
    print("Downloading Data...")
    HTTPServices.HTTPHandler.requestData(datasetName)
    print("Data downloaded")
    print("Extracting files...")
    tar = tarfile.open("Data/" + datasetName + ".tar.gz")
    tar.extractall(path="Data/")
    tar.close()
    os.remove("Data/" + datasetName + ".tar.gz")
    print("Data Extracted")

def setup():
    datasetName = HTTPServices.HTTPHandler.whichDataset()
    print(datasetName)
    datasetLocation = "Data/" + datasetName
    if not os.path.exists(datasetLocation):
        downloadData(datasetName)
    HTTPServices.HTTPHandler.connectToServer()

def run():
    netServices.neuralNet.multilayerTrain(datasetLocation)


#setup()
#run()
JSONHandler.JSONHandler.getJSONModel("testNetFile.json")
