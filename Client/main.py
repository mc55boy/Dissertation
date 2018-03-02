import httpClient as HTTPServices
import os
import tarfile
import netHandler as netHandler
import time

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
    # Connect to server and register client
    global myID
    success, myID = HTTPServices.HTTPHandler.connectToServer()
    if success:
        print("Successfully Registered Client")
        return True
    else:
        print("Failed to register client")
        return False


def run():

    while True:

        if HTTPServices.HTTPHandler.isReady():
            success, datasetName = HTTPServices.HTTPHandler.whichDataset(myID)
            if success:
                datasetLocation = "Data/" + datasetName
                if not os.path.exists(datasetLocation):
                    downloadData(datasetName)
                netModel = HTTPServices.HTTPHandler.requestModel(myID)
            else:
                print("Failed to get Dataset name")

            netModel = list(map(int, netModel))
            print("NETMODEL: " + str(netModel))
            #netInput = JSONHandler.JSONHandler.readJSONModel("DownloadedModel/model.json")
            accuracy = netHandler.neuralNet.multilayerTrain(datasetLocation, netModel)
            print("ACCURACY: " + str(accuracy))
            netInput = {"results": {"accuracy": 0}}
            netInput["results"]["accuracy"] = accuracy
            print(netInput["results"]["accuracy"])
            #JSONHandler.JSONHandler.writeToJSON("DownloadedModel/model.json", netInput)
        else:
            print("Not Ready...")
            time.sleep(0.5)


if setup():
    run()
else:
    print("Failed to setup client")
