import httpClient as HTTPServices
import os
import tarfile
import netHandler as netHandler
import JSONHandler as JSONHandler



myID = None

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
    #Connect to server and register client

    success, myID = HTTPServices.HTTPHandler.connectToServer()
    if success:
        print(myID)
        success, datasetName = HTTPServices.HTTPHandler.whichDataset(myID)
        if success:
            datasetLocation = "Data/" + datasetName
            if not os.path.exists(datasetLocation):
                downloadData(datasetName)
            HTTPServices.HTTPHandler.requestModel(myID)
        else:
            print("Failed to get Dataset name")
    else:
        print("Failed to register client")
        return False





def run():
    netInput = JSONHandler.JSONHandler.readJSONModel("DownloadedModel/model.json")
    accuracy = netHandler.neuralNet.multilayerTrain(datasetLocation, netInput)
    netInput["results"]["accuracy"] = str(accuracy);
    print(netInput["results"]["accuracy"])
    JSONHandler.JSONHandler.writeToJSON("DownloadedModel/model.json", netInput)

setup()
#run()
