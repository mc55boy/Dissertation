import httpClient as HTTPServices
import os
import tarfile
import netHandler as netHandler
import JSONHandler as JSONHandler

#multilayerTrain()

datasetLocation = "Data/"


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
    HTTPServices.HTTPHandler.requestModel()
    HTTPServices.HTTPHandler.connectToServer()

def run():
    netInput = JSONHandler.JSONHandler.readJSONModel("DownloadedModel/model.json")
    accuracy = netHandler.neuralNet.multilayerTrain(datasetLocation, netInput)
    netInput["results"]["accuracy"] = str(accuracy);
    print(netInput["results"]["accuracy"])
    JSONHandler.JSONHandler.writeToJSON("DownloadedModel/model.json", netInput)


setup()
run()
#netHandler.neuralNet.testBuildNet()
