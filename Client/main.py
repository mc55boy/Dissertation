import httpClient as HTTPServices
import os
import tarfile
# import netHandler as netHandler
import random

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


def clientWait(counter, message):
    b = message + "." * counter
    print(b, end="\r")
    counter += 1
    if counter == 5:
        counter = 0
    print(" " * 50, end="\r")
    return counter


def run():

    counter = 0

    while True:

        if HTTPServices.HTTPHandler.isReady():
            counter = 0
            success, datasetName = HTTPServices.HTTPHandler.whichDataset(myID)
            if success:
                datasetLocation = "Data/" + datasetName
                if not os.path.exists(datasetLocation):
                    downloadData(datasetName)
                netModel = HTTPServices.HTTPHandler.requestModel(myID)
                modelArch = netModel['Model']['Model']
                modelID = netModel['ModelID']
                parameters = netModel['Model']['Parameters']
                # accuracy = netHandler.neuralNet.multilayerTrain(datasetLocation, modelArch, parameters)
                accuracy = random.random()
                response = {"clientID": myID, 'ModelID': modelID, "results": {"accuracy": str(accuracy)}}
                if HTTPServices.HTTPHandler.sendResults(response):
                    print("Getting next model...")
                else:
                    print("Something went wrong...")
            else:
                print("Failed to get Dataset name")
        else:
            clientWait(counter, "Waiting for server to process new models")


if setup():
    run()
else:
    print("Failed to setup client")
