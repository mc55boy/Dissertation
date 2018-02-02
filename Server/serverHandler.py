import string,cgi,time
from os import curdir, sep
#from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from http.server import BaseHTTPRequestHandler, HTTPServer

class MyHandler(BaseHTTPRequestHandler):


    def _set_response(self, opts): #This is just a duplicate of handle_http. rewrite this to handle both
        self.send_response(opts['status'])
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        content = opts['response'].format(self.path)
        self.wfile.write(bytes(content, 'utf-8'))

    def do_POST(self):
        paths = {
            '/registerClient': {'status': 200, 'response': 'hello'},
        }

        if self.path in paths:
            #Serve PUT request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            print(post_data.decode('utf-8'))
            self._set_response(paths[self.path])
            #self.wfile.write("POST request {}".format(self.path).encode('utf-8'))
        else:
            self._set_response({'status': 404})
            #self.wfile.write("POST request {}".format(self.path).encode('utf-8'))

    def do_GET(self):
        paths = {
            '/getDataset': {'status': 200, 'response': 'MNIST_data'},
            '/getModel': {'status': 200, 'response': 'hello'},
            '/getNewID': {'status': 200, 'response': '1'}
        }

        if self.path in paths:
            #Serve GET request
            self._set_response(paths[self.path])
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
