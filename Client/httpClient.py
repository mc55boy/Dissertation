import http.client
import urllib.request

class HTTPHandler:

    def requestData():
        urllib.request.urlretrieve("http://localhost:9000/Data/MNIST.tar.gz", "Data/MNIST.tar.gz")
