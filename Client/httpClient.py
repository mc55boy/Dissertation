import urllib.parse
import urllib.request
#import urllib.request
import json


def sendGet(url):
    print("SENDING: " + url)
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
        success = True
    elif response.status == 404:
        print("Not found")
    elif response.status == 500:
        print("SERVER ERROR")
        print(response.read())
    else:
        print("Connection failed")
    return success, response.read().decode('utf-8')


def registerClient(clientID):
    dataToSend = json.dumps({'clientID': clientID}).encode('utf-8')
    url = "/registerClient"
    header = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    return sendPost(url, dataToSend, header)


def getModel(myID):
    url = "/getModel"
    dataToSend = json.dumps({"clientID" : myID}).encode('utf-8')
    header = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    success, response = sendPost(url, dataToSend, header)
    if success:
        return response.split()
    else:
        print("FAILED")
        print(response)
        return response


class HTTPHandler:
    def isReady():
        success, response = sendGet("ready")
        if response == "True":
            return True
        else:
            return False



    def connectToServer():
        #Get new ID
        success, response = sendGet("getNewID")
        if success:
            tempID = response
            success, response = registerClient(response)
            if success:
                print("New ID: " + tempID)
                print(response)
                return True, tempID
            else:
                print(response)
                return False, None
        else:
            print("Failed to obtain new ID")
            return False, None


    def requestModel(myID):
        nextModel = getModel(myID)
        return nextModel
        #urllib.request.urlretrieve("http://localhost:9000/Models/" + nextModel + ".json", "DownloadedModel/model.json")

    def requestData(datasetName):
        urllib.request.urlretrieve("http://localhost:9000/Data/" + datasetName + ".tar.gz", "Data/MNIST_data.tar.gz")

    def whichDataset(myID):
        dataToSend = json.dumps({'clientID': myID}).encode('utf-8')
        url = "/getDataset"
        header = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        return sendPost(url, dataToSend, header)

        #httpResponse = urllib.request.urlopen("http://localhost:9000/getDataset").read()
        #datasetName = httpResponse.decode("utf-8")
        #return datasetName
