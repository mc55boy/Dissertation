import http.client, urllib.parse, urllib.request
#import urllib.request

def registerClient(clientID):
    params = urllib.parse.urlencode({'@clientID': clientID})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = http.client.HTTPConnection("localhost", 9000)
    conn.request("POST", "/registerClient", params, headers)
    response = conn.getresponse()
    if response.status == 200:
        print("OK Response")
        data = response.read()
        print(data)
    else:
        print("Connection failed")
    conn.close()

def getNewID():
    httpResponse = urllib.request.urlopen("http://localhost:9000/getNewID").read()
    assignedID = httpResponse.decode("utf-8")
    return assignedID

def getModel():
     httpResponse = urllib.request.urlopen("http://localhost:9000/getModel").read()
     nextModel = httpResponse.decode("utf-8")
     return nextModel


class HTTPHandler:

    def connectToServer():
        clientID = getNewID()
        registerClient(clientID)

    def requestModel():
        nextModel = getModel()
        print("MODEL: " + nextModel)
        urllib.request.urlretrieve("http://localhost:9000/Models/" + nextModel + ".json", "DownloadedModel/model.json")

    def requestData(datasetName):
        urllib.request.urlretrieve("http://localhost:9000/Data/" + datasetName + ".tar.gz", "Data/MNIST_data.tar.gz")

    def whichDataset():
        httpResponse = urllib.request.urlopen("http://localhost:9000/getDataset").read()
        datasetName = httpResponse.decode("utf-8")
        return datasetName
