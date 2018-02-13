import http.client, urllib.parse, urllib.request
#import urllib.request
import json

myID = None

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

def sendGet(url):
    try:
        httpResponse = urllib.request.urlopen("http://localhost:9000/" + url).read()
        response = httpResponse.decode("utf-8")
        return True, response
    except urllib.error.URLError as e:
        return False, e.reason

def getNewID():
    success, response = sendGet("getNewID")
    if success:
        myID = response
        print(response)
    else:
        print(response)

    #return assignedID

def getModel():

    dataToSend = json.dumps({"ID" : myID}).encode('utf-8')

    request = urllib.request.Request("http://localhost:9000/getModel", data=dataToSend, headers={'Content-Type': 'application/json'})
    response = urllib.request.urlopen(request)
    print(response.decode('utf-8'))
    #httpResponse = urllib.request.urlopen("http://localhost:9000/getModel", data=dataToSend, headers={'Content-Type': 'application/json'}).read()
    #nextModel = response.decode("utf-8")
    return nextModel


class HTTPHandler:

    def testFunction():
        success, response = sendGet("testFunction")
        if success:
            print(response)
        else:
            print(response)


    def connectToServer():
        registerClient(getNewID())

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
