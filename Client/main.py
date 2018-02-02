import httpClient as HTTPServices
import os
import tarfile
#import netHandler as netServices
#multilayerTrain()

#netServices.neuralNet.multilayerTrain()

def downloadData(datasetName):
    print("Downloading Data...")
    HTTPServices.HTTPHandler.requestData()
    print("Data downloaded")
    print("Extracting files...")
    tar = tarfile.open("Data/" + datasetName + ".tar.gz")
    tar.extractall(path="Data/")
    tar.close()
    os.remove("Data/" + datasetName + ".tar.gz")
    print("Data Extracted")

def setup():
    datasetName = HTTPServices.HTTPHandler.whichDataset()
    if not os.path.exists("Data/" + datasetName):
        downloadData(datasetName)

    print(datasetName)
    HTTPServices.HTTPHandler.connectToServer()


setup()
