import httpClient as HTTPServices
import os
import tarfile
#import netHandler as netServices
#multilayerTrain()

#netServices.neuralNet.multilayerTrain()


def setup():
    problemData = "MNIST_data"
    if not os.path.exists("Data/" + problemData):
        print("Downloading Data...")
        HTTPServices.HTTPHandler.requestData()
        print("Data downloaded")
        print("Extracting files...")
        tar = tarfile.open("Data/MNIST.tar.gz")
        tar.extractall(path="Data/")
        tar.close()
        os.remove("Data/MNIST.tar.gz")
        print("Data Extracted")
    else:
        print("Data Exists")
setup()
