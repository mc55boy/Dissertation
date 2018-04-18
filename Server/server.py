from os import curdir, sep
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading
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
popCount = 0

leftToProcess = 0


def newClient():
    global connectedClients
    newID = uuid.uuid4().hex
    newClient = {"clientID": newID, "Registered": False, "Model": list()}

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

                return {'status': 200, 'response': json.dumps("Client Registered")}
        return {'status': 500, 'response': "Could not find client ID"}
    except StopIteration:
        return {'status': 500, 'response': "Client not found"}


def getModel(self):
    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length)
    global connectedClients
    try:
        jsonData = json.loads(post_data.decode('utf-8'))
        clientID = jsonData['clientID']
        client = next(item for item in connectedClients if item["clientID"] == clientID)
        # print(json.dumps(connectedClients, indent=4, sort_keys=True))
        for i, item in enumerate(connectedClients):
            if item == client:
                for model in connectedClients[i]['Model']:
                    if not model['Processed']:
                        returnText = {'Model': model, 'ModelID': model['ModelID']}

                return {'status': 200, 'response': returnText}
    except StopIteration:
        return {'status': 500, 'response': "Client not found"}


def assignModels():
    global currentPopulation
    global leftToProcess

    pop = evo_conn.recv()
    currentPopulation = list()

    for ind in pop:
        newInd = {"Model": ind[1]["Model"], "Parameters": ind[1]["Parameters"], "ModelID": ind[1]["ModelID"], "Processed": False, "clientID": None, "Result": 0}
        currentPopulation.append(newInd)
        leftToProcess += 1

    clientCounter = 0
    for i, model in enumerate(currentPopulation):
        clientCounter += 1
        if clientCounter >= numClients:
            clientCounter = 0
        connectedClients[clientCounter]['Model'].append(model)
        currentPopulation[i]['clientID'] = connectedClients[clientCounter]['clientID']


def ready(self):
    global evoState
    global useSamePop
    global serverState
    global numProcessed
    global leftToProcess
    global connectedClients
    global currentPopulation


    # Make sure that all clients are connected (server state above 0)
    # & make sure that evo has created the population (evo state 1)
    if useSamePop and not serverState.value == 0:
        assignModels()
        useSamePop = False

    if evoState.value == 1 and not serverState.value == 0:
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        global connectedClients
        try:
            jsonData = json.loads(post_data.decode('utf-8'))
            clientID = jsonData['clientID']
            client = next(item for item in connectedClients if item["clientID"] == clientID)
            # print(json.dumps(connectedClients, indent=4, sort_keys=True))
            for i, item in enumerate(connectedClients):
                if item == client:
                    if len(connectedClients[i]['Model']) == 0:
                        return {'status': 200, 'response': 'False'}
                        break
        except StopIteration:
            return {'status': 500, 'response': "Fucked it"}
        return {'status': 200, 'response': 'True'}
    else:
        return {'status': 200, 'response': 'False'}


def processResult(self):
    global currentPopulation
    global numProcessed
    global useSamePop
    global serverState
    global leftToProcess
    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length)

    try:
        jsonData = json.loads(post_data.decode('utf-8'))
        clientID = jsonData['clientID']
        modelID = jsonData['ModelID']
        result = float(jsonData['results']['accuracy'])

        for clientNum, client in enumerate(connectedClients):
            if client["clientID"] == clientID:
                for modelNum, model in enumerate(connectedClients[clientNum]['Model']):
                    if model['ModelID'] == modelID:
                        connectedClients[clientNum]['Model'][modelNum]['Result'] = float(result)
                        #connectedClients[clientNum]['Model'][modelNum]['Processed'] = True
                        del connectedClients[clientNum]['Model'][modelNum]
                        numProcessed += 1
                        leftToProcess -= 1
                        if numProcessed == len(currentPopulation):
                            useSamePop = True
                            serverState.value = 2
                            evo_conn.send(currentPopulation)
                            numProcessed = 0
                            leftToProcess = len(currentPopulation)

                        else:
                            serverState.value = 1
                        break
        return {'status': 200, 'response': "Result Recorded"}
    except StopIteration:
        return {'status': 500, 'response': "Couldn't post result"}


getPaths = {
    '/getNewID': newClient
}

postPaths = {
    '/ready': ready,
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
        # self.send_header('Content-type', 'text/html')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        if isinstance(opts['response'], dict):
            content = json.dumps(opts['response'])
        else:
            content = opts['response'].format(self.path)
        self.wfile.write(bytes(content, 'utf-8'))

    def do_POST(self):
        if self.path in postPaths:
            # Serve PUT request
            # print("POST: " + str(self.path))
            self._set_response(postPaths[self.path](self))
        else:
            self._set_response({'status': 404, 'response': 'No such page'})

    def do_GET(self):
        if self.path in getPaths:
            # Serve GET request
            # print("GET: " + str(self.path))
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


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    '''Nothing here '''


def main(evoReady, inputServerState, connection, inputNumClients, maxPop):
    try:
        global evoState
        global serverState
        global evo_conn
        global numClients

        serverState = inputServerState
        evoState = evoReady
        evo_conn = connection
        numClients = inputNumClients
        #server = HTTPServer(('', 9000), MyHandler)
        server = ThreadedHTTPServer(('', 9000), MyHandler)
        print('started httpserver...')
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down server')
        server.socket.close()


if __name__ == '__main__':
    main()
