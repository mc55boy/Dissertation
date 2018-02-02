import http.client
import urllib.request

class HTTPHandler:

    def requestData():
        urllib.request.urlretrieve("http://localhost:9000/Data/MNIST.tar.gz", "Data/MNIST_data.tar.gz")

    def whichDataset():
        httpResponse = urllib.request.urlopen("http://localhost:9000/getDataset").read()
        datasetName = httpResponse.decode("utf-8")
        return datasetName
