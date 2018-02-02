import http.client, urllib.parse, urllib.request
#import urllib.request

class HTTPHandler:

    def registerClient():

        params = urllib.parse.urlencode({'@id': 12524})
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

        conn = http.client.HTTPConnection("localhost", 9000)
        conn.request("POST", "/registerClient", params, headers)
        response = conn.getresponse()
        print(response.status, response.reason)
        data = response.read()
        print(data)
        conn.close()

    def requestData():
        urllib.request.urlretrieve("http://localhost:9000/Data/MNIST.tar.gz", "Data/MNIST_data.tar.gz")

    def whichDataset():
        httpResponse = urllib.request.urlopen("http://localhost:9000/getDataset").read()
        datasetName = httpResponse.decode("utf-8")
        return datasetName
