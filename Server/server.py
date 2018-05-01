from os import curdir, sep
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

'''
SERVER STATES:
0 = Waiting for clients to register with server
1 = Waiting for clients to process networks
2 = Networks have been processed and next generation is being processed

EVO STATES:
0 = Population not generate
1 = Population ready to use
'''


# Global variables

# Dataset location
datasetInUse = None

# Client global variables
connectedClients = [None]
numClients = 0
registeredClients = 0

# Population global variables
currentPopulation = list()
numProcessed = 0
popCount = 0
leftToProcess = 0

# Threading global variables used for ready signal and
# population transfer
evoState = None
serverState = None
evo_conn = None
useSamePop = True


# Returns a UUID for client registration
def newClient():
    global connectedClients
    newID = uuid.uuid4().hex
    newClient = {"clientID": newID, "Registered": False, "Model": list()}

    if len(connectedClients) == 1 and connectedClients[0] is None:
        connectedClients[0] = newClient
    else:
        connectedClients.append(newClient)

    return {'status': 200, 'response': str(newID)}


# Returns the current dataset in use to Client
def whichDataset(self):
    global datasetInUse
    response = {'status': 200, 'response': datasetInUse}
    return response


# Uses UUID sent from Client to fully register
def registerClient(self):
    global connectedClients
    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length)
    jsonData = json.loads(post_data.decode('utf-8'))
    clientID = jsonData['clientID']
    # Find clientID in generated clients and register if found
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


# Returns model for particular client by searching for ClientID in registerClient
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
                for model in connectedClients[i]['Model']:
                    if not model['Processed']:
                        returnText = {'Model': model, 'ModelID': model['ModelID']}

                return {'status': 200, 'response': returnText}
    except StopIteration:
        return {'status': 500, 'response': "Client not found"}


# Distribute models equally amongst registered clients
def assignModels():
    global currentPopulation
    global leftToProcess
    # Receive population from thread pipe
    pop = evo_conn.recv()
    currentPopulation = list()
    for ind in pop:
        newInd = {"Model": ind["Model"], "Parameters": ind["Parameters"], "ModelID": ind["ModelID"], "Processed": False, "clientID": None, "Result": 0}
        currentPopulation.append(newInd)
        leftToProcess += 1

    clientCounter = 0
    for i, model in enumerate(currentPopulation):
        clientCounter += 1
        if clientCounter >= numClients:
            clientCounter = 0
        connectedClients[clientCounter]['Model'].append(model)
        currentPopulation[i]['clientID'] = connectedClients[clientCounter]['clientID']


# If both server and evoHandler are in the correct states + clients have
# a network still assigned to them
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

    # Make sure that new population has been generated + all clients have been registered
    if evoState.value == 1 and not serverState.value == 0:
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        global connectedClients
        try:
            jsonData = json.loads(post_data.decode('utf-8'))
            clientID = jsonData['clientID']
            client = next(item for item in connectedClients if item["clientID"] == clientID)
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


# Receive result and use client ID and Model ID to assign result to relevant model in population
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
                        del connectedClients[clientNum]['Model'][modelNum]
                        numProcessed += 1
                        leftToProcess -= 1
                        print(str(numProcessed) + "/" + str(len(currentPopulation)) + " processed...", end="\r")
                        # Check if all networks been processed
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


# HTTP links referencing relavant functions
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


# HTTP Server handler
# Processed http requests, formats into usable data as well as simple first line error handling
class MyHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        return

    def _set_response(self, opts):
        self.send_response(opts['status'])
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


# Setup global variables sent from core
def main(evoReady, inputServerState, connection, inputNumClients, maxPop, datasetLocation):
    try:
        global evoState
        global serverState
        global evo_conn
        global numClients
        global datasetInUse

        datasetInUse = datasetLocation
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
