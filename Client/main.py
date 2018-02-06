import httpClient as HTTPServices
import os
import tarfile
import netHandler as netHandler
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
    datasetLocation = "Data/" + datasetName
    if not os.path.exists(datasetLocation):
        downloadData(datasetName)
    HTTPServices.HTTPHandler.connectToServer()
    netInput = JSONHandler.JSONHandler.readJSONModel("example.json")
    netHandler.neuralNet.multilayerTrain(datasetLocation, netInput)


setup()
#netHandler.neuralNet.testBuildNet()
