from os import curdir, sep
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from multiprocessing import Value
import time


# POTENTIALLY IMPLEMENT FOR THE MESSAGES TO SEND BACK JSON OR XML TO MAKE IT EASIER TO PROCESS DATA
# ON THE CLIENT END


datasetInUse = None
connectedClients = [None]
models = [None]

isEvoReady = None
evo_conn = None
currentPopulation = None
useSamePop = True


def newClient():
    newID = uuid.uuid4().hex
    newClient = {"clientID": newID, "Registered": False, "Model": "None"}

    if len(connectedClients) == 1 and connectedClients[0] is None:
        connectedClients[0] = newClient
    else:
        connectedClients.append(newClient)

    return {'status': 200, 'response': str(newID)}


def testFunction():
    response = {'status': 200, 'response': 'Test function called'}
    return response


def whichDataset(self):
    datasetInUse = "MNIST_data"
    response = {'status': 200, 'response': datasetInUse}
    return response


def whichModel(self):
    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length)
    try:
        jsonData = json.loads(post_data.decode('utf-8'))
        clientID = jsonData['clientID']
        client = next(item for item in connectedClients if item["clientID"] == clientID)
        for i, item in enumerate(connectedClients):
            if item == client:
                return {'status': 200, 'response': "1"}
    except StopIteration:
        return {'status': 500, 'response': "Client not found"}


def registerClient(self):
    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length)
    jsonData = json.loads(post_data.decode('utf-8'))
    clientID = jsonData['clientID']
    try:
        client = next(item for item in connectedClients if item["clientID"] == clientID)
        for i, item in enumerate(connectedClients):
            if item == client:
                client['Registered'] = True
                connectedClients[i] = client
                return {'status': 200, 'response': "Client Registered"}
    except StopIteration:
        return {'status': 500, 'response': "Client not found"}


def ready():
    global isEvoReady
    global currentPopulation
    global useSamePop
    isReady = isEvoReady.value
    if isReady == 1:
        if useSamePop:
            currentPopulation = evo_conn.recv()
            useSamePop = False
        for ind in currentPopulation:
            print(ind)
        return {'status': 200, 'response': 'True'}
    else:
        useSamePop = True
        return {'status': 200, 'response': 'False'}


def processResult(self):
    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length)
    try:
        jsonData = json.loads(post_data.decode('utf-8'))
        clientID = jsonData['clientID']

    except StopIteration:
        return {'status': 500, 'response': "Couldn't post result"}


getPaths = {
    '/getNewID': newClient,
    '/testFunction': testFunction,
    '/ready': ready
}

postPaths = {
    '/getModel': whichModel,
    '/getDataset': whichDataset,
    '/registerClient': registerClient,
    '/result': processResult
}


class MyHandler(BaseHTTPRequestHandler):

    def _set_response(self, opts): # This is just a duplicate of handle_http. rewrite this to handle both
        self.send_response(opts['status'])
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content = opts['response'].format(self.path)
        self.wfile.write(bytes(content, 'utf-8'))

    def do_POST(self):
        if self.path in postPaths:
            # Serve PUT request
            self._set_response(postPaths[self.path](self))
        else:
            self._set_response({'status': 404, 'response': 'No such page'})

    def do_GET(self):
        if self.path in getPaths:
            # Serve GET request
            self._set_response(getPaths[self.path]())
        else:
            # Serve file
            try:
                requestedFile = open(curdir + sep + self.path, 'rb')
                self.send_response(200)
                self.send_header('Content-type',    'text/html')
                self.end_headers()
                self.wfile.write(requestedFile.read())
                requestedFile.close()
                return

            except IOError:
                self.send_error(404, 'File Not Found: %s' % self.path)


def main(initialFlag, connection):
    try:
        global isEvoReady
        global evo_conn
        isEvoReady = initialFlag
        evo_conn = connection
        server = HTTPServer(('', 9000), MyHandler)
        print('started httpserver...')
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down server')
        server.socket.close()


if __name__ == '__main__':
    main()
