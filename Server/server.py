from os import curdir, sep
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
import json


# POTENTIALLY IMPLEMENT FOR THE MESSAGES TO SEND BACK JSON OR XML TO MAKE IT EASIER TO PROCESS DATA
# ON THE CLIENT END

# Global variables

datasetInUse = None
connectedClients = [None]

evoState = None
serverState = None
evo_conn = None
currentPopulation = list()
useSamePop = True
numClients = None
registeredClients = 0
numProcessed = 0


def newClient():
    newID = uuid.uuid4().hex
    newClient = {"clientID": newID, "Registered": False, "Model": "None"}

    if len(connectedClients) == 1 and connectedClients[0] is None:
        connectedClients[0] = newClient
    else:
        connectedClients.append(newClient)

    return {'status': 200, 'response': str(newID)}


def whichDataset(self):
    datasetInUse = "MNIST_data/"
    response = {'status': 200, 'response': datasetInUse}
    return response


def transformModel(ind):
    returnList = []
    for item in ind:
        returnList.append(item)
    return ' '.join(str(e) for e in returnList)


def getModel(self):
    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length)
    global connectedClients
    try:
        jsonData = json.loads(post_data.decode('utf-8'))
        clientID = jsonData['clientID']
        client = next(item for item in connectedClients if item["clientID"] == clientID)
        for i, item in enumerate(connectedClients):
            if item == client:
                return {'status': 200, 'response': transformModel(currentPopulation[i]["Model"])}
    except StopIteration:
        return {'status': 500, 'response': "Client not found"}


def registerClient(self):
    global connectedClients
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
                global registeredClients
                registeredClients += 1
                if registeredClients == numClients:
                    global serverState
                    serverState.value = 1

                return {'status': 200, 'response': "Client Registered"}
        return {'status': 500, 'response': "Could not find client ID"}
    except StopIteration:
        return {'status': 500, 'response': "Client not found"}


def assignModels():
    pop = evo_conn.recv()
    for ind in pop:
        print(ind)
    global currentPopulation
    currentPopulation = list()

    for ind in pop:
        newInd = {"Model": ind["Model"], "ModelID": ind["ModelID"], "Processed": False, "clientID": None, "Result": 0}
        currentPopulation.append(newInd)
    for client in range(len(connectedClients)):
        connectedClients[client]["Model"] = currentPopulation[client]["Model"]
        currentPopulation[client]["clientID"] = connectedClients[client]["clientID"]


def ready():
    global evoState
    global currentPopulation
    global useSamePop
    if evoState.value == 1:
        if useSamePop or serverState.value == 2:
            assignModels()
            useSamePop = False
        return {'status': 200, 'response': 'True'}
    else:
        useSamePop = True
        return {'status': 200, 'response': 'False'}


def processResult(self):
    global currentPopulation
    global numProcessed
    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length)
    try:
        jsonData = json.loads(post_data.decode('utf-8'))
        clientID = jsonData['clientID']
        result = float(jsonData['results']['accuracy'])
        ind = next(item for item in currentPopulation if item["clientID"] == clientID)
        for i, item in enumerate(currentPopulation):
            if item == ind:
                ind['Result'] = result
                ind['Processed'] = True
                currentPopulation[i] = ind
                numProcessed += 1
                if numProcessed == len(currentPopulation):
                    serverState.value = 2
                    evo_conn.send(currentPopulation)
                    print("Processed: " + str(currentPopulation))
                    numProcessed = 0
                return {'status': 200, 'response': "Result Recorded"}
    except StopIteration:
        return {'status': 500, 'response': "Couldn't post result"}


getPaths = {
    '/getNewID': newClient,
    '/ready': ready
}

postPaths = {
    '/getModel': getModel,
    '/getDataset': whichDataset,
    '/registerClient': registerClient,
    '/result': processResult
}


class MyHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        return

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


def main(evoReady, inputServerState, connection, inputNumClients):
    try:
        global evoState
        global serverState
        global evo_conn
        global numClients
        serverState = inputServerState
        evoState = evoReady
        evo_conn = connection
        numClients = inputNumClients
        server = HTTPServer(('', 9000), MyHandler)
        print('started httpserver...')
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down server')
        server.socket.close()


if __name__ == '__main__':
    main()
