import httpClient as HTTPServices
import os
import tarfile
import netHandler as netHandler
import time
import sys
import getopt

# ClientID
myID = None

#Save location for dataset
datasetLocation = "Data/"


def downloadData(datasetName):
    print("Downloading Data...")
    HTTPServices.HTTPHandler.requestData(datasetName)
    print("Data downloaded")
    print("Extracting files...")
    tar = tarfile.open("Data/" + datasetName + ".tar")
    tar.extractall(path="Data/")
    tar.close()
    os.remove("Data/" + datasetName + ".tar")
    print("Data Extracted")


def setup(argv):
    # Connect to server and register client
    try:
        opts, args = getopt.getopt(argv, "hi:p:")
    except getopt.GetoptError:
        print('main.py -i <IP Address of Server> -p <Port to connect to>\nDefault: "localhost:9000"')
        sys.exit(2)
    serverIP = "localhost"
    serverPort = "9000"
    for opt, arg in opts:
        if opt == '-h':
            print('main.py -i <IP Address of Server> -p <Port to connect to>\nDefault: "localhost:9000"')
            sys.exit()
        elif opt in ("-i"):
            serverIP = arg
        elif opt in ("-p"):
            serverPort = arg
    serverConnection = serverIP + ":" + serverPort
    global myID
    success, myID = HTTPServices.HTTPHandler.connectToServer(serverConnection)
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
    time.sleep(0.3)
    print(" " * 50, end="\r")
    return counter


def run():
    counter = 0

    while True:

        if HTTPServices.HTTPHandler.isReady(myID):
            counter = 0
            success, datasetName = HTTPServices.HTTPHandler.whichDataset(myID)
            print(datasetName)
            if success:
                datasetLocation = "Data/" + datasetName
                if not os.path.exists(datasetLocation):
                    downloadData(datasetName)
                netModel = HTTPServices.HTTPHandler.requestModel(myID)
                modelArch = netModel['Model']['Model']
                modelID = netModel['ModelID']
                parameters = netModel['Model']['Parameters']
                accuracy = netHandler.neuralNet.multilayerTrain(datasetLocation, modelArch, parameters)
                response = {"clientID": myID, 'ModelID': modelID, "results": {"accuracy": str(accuracy)}}
                if HTTPServices.HTTPHandler.sendResults(response):
                    print("Getting next model...")
                else:
                    print("Something went wrong...")
            else:
                print("Failed to get Dataset name")
        else:
            counter = clientWait(counter, "Waiting for server to process new models")


if __name__ == "__main__":
    if setup(sys.argv[1:]):
        run()
    else:
        print("Failed to setup client")
