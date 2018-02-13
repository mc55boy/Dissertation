import http.client, urllib.parse, urllib.request
#import urllib.request
import json

myID = None


def sendGet(url):
    try:
        httpResponse = urllib.request.urlopen("http://localhost:9000/" + url).read()
        response = httpResponse.decode("utf-8")
        return True, response
    except urllib.error.URLError as e:
        return False, e.reason


def sendPost(url, dataToSend, header):

    success = False


    request = urllib.request.Request("http://localhost:9000" + url, data=dataToSend, headers=header)
    response = urllib.request.urlopen(request)

    if response.status == 200:
        print("OK Response")
        data = response.read()
        success = True
    elif response.status == 404:
        print("Not found")
    elif response.status == 500:
        print("SERVER ERROR")
        print(response.read())
    else:
        print("Connection failed")
    return success, response.read()


def registerClient(clientID):
    dataToSend = json.dumps({'clientID': clientID}).encode('utf-8')
    url = "/registerClient"
    header = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    return sendPost(url, dataToSend, header)


def getModel():
    url = "/getModel"
    dataToSend = json.dumps({"ID" : myID}).encode('utf-8')
    header = {'Content-Type': 'application/json'}
    success, response = sendPost(url, dataToSend, header)

    if success:
        print(response)
    else:
        print("FAILED")
        print(response)
    return nextModel


class HTTPHandler:

    def testFunction():
        success, response = sendGet("testFunction")
        if success:
            print(response)
        else:
            print(response)


    def connectToServer():
        #Get new ID
        success, response = sendGet("getNewID")
        if success:
            print("New ID: " + response)
            success, response = registerClient(response)
            if success:
                print("Registered Client")
            else:
                print("Failed to register client")
        else:
            print("Failed to obtain new ID")


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
