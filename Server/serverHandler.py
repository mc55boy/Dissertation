import string,cgi,time
from os import curdir, sep
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer

#POTENTIALLY IMPLEMENT FOR THE MESSAGES TO SEND BACK JSON OR XML TO MAKE IT EASIER TO PROCESS DATA
#ON THE CLIENT END

numberOfConnectedClients = 0
datasetInUse = None
connectedClients = [None]

def newClient():
    newID = uuid.uuid4().hex
    if newID not in connectedClients:
        if len(connectedClients) == 1 and connectedClients[0] == None:
            connectedClients[0] = newID
            return {'status': 200, 'response': str(connectedClients[0])}
        else:
            connectedClients.append(newID)
            return {'status': 200, 'response': str(newID)}
    return {'status': 500, 'response': "Failed"}

def testFunction():
    response = {'status': 200, 'response': 'Test function called'}
    return response

def whichDataset():
    datasetInUse = "MNIST_data"
    response = {'status': 200, 'response': datasetInUse}
    return response

def whichModel():
    modelInUse = "1"
    response = {'status': 200, 'response': modelInUse}
    return response

def registerClient():
    response = {'status': 200, 'response': "registered"}
    return response



getPaths = {
    '/getDataset': whichDataset,
    '/getNewID': newClient,
    '/testFunction': testFunction
}

postPaths = {
    '/getModel': whichModel,
    '/registerClient': registerClient
}



class MyHandler(BaseHTTPRequestHandler):

    def _set_response(self, opts): #This is just a duplicate of handle_http. rewrite this to handle both
        self.send_response(opts['status'])
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content = opts['response'].format(self.path)
        self.wfile.write(bytes(content, 'utf-8'))

    def do_POST(self):


        if self.path in postPaths:
            #Serve PUT request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            print(post_data.decode('utf-8'))
            self._set_response(postPaths[self.path]())
        else:
            self._set_response({'status': 404, 'response': 'No such page'})

    def do_GET(self):

        #paths = {
        #    '/getDataset': {'status': 200, 'response': 'MNIST_data'},
        #    '/getModel': {'status': 200, 'response': str(1)},
        #    '/getNewID': {'status': 200, 'response': str(1)}
        #}



        if self.path in getPaths:
            #Serve GET request
            #self._set_response(paths[self.path])
            self._set_response(getPaths[self.path]())
        else:
            #Serve file
            try:
                requestedFile = open(curdir + sep + self.path, 'rb')
                self.send_response(200)
                self.send_header('Content-type',    'text/html')
                self.end_headers()
                self.wfile.write(requestedFile.read())
                requestedFile.close()
                return

            except IOError:
                self.send_error(404,'File Not Found: %s' % self.path)


def main():
    try:
        server = HTTPServer(('', 9000), MyHandler)
        print('started httpserver...')
        server.serve_forever()
    except KeyboardInterrupt:
        print ('^C received, shutting down server')
        server.socket.close()

if __name__ == '__main__':
    main()
