from utilities.MySQLConnector import MySQLConnector as mql
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from _thread import start_new_thread
from datetime import datetime

## [robust]
take_frame = False
user = ''
#
db_addr = 'localhost'
class _RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_POST(self):
        ## Get content (request body) length
        cont_len = int(self.headers['Content-Length'])
        if cont_len == 0:
            ## Respond with 400 'bad request' if empty
            self.send_response(400)
        else:
            ## Decode request content
            content = self.rfile.read(cont_len).decode('utf-8')
            print(f'\nHTTP> Received: \"{content}\"')
            if self.path == '/query':
                self.do_query(content)
            elif self.path == '/photo':
                self.do_photo(content)

    def do_query(self, content):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(f'Added \"{content}\"', 'utf-8'))
        mql(host=db_addr).ConnectAndQuery(name=content, date=datetime.now())

    def do_photo(self, content):
        ## Set save user frame (photograph) flags
        global take_frame, user
        take_frame = True
        user = content
        ## Respond with 200 'ok' and short byte-text
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(f'Took photo of \"{content}\"', 'utf-8'))
        mql(host=db_addr).ConnectAndQuery(name=content, date=datetime.now())

class HttpServer:
    def __init__(self, loc_ip='localhost', loc_port=8080, ext_ip='localhost'):
        """
        Called when the class is instantiated.
        It initializes a few variables.
        :param self: Represent the instance of the class
        :param loc_ip: local IPv4 address of the local server (default: localhost)
        :param loc_port: port number of the local server (default: 8080)
        :param ext_ip: database server IPv4 (default: localhost)
        """
        self.loc_ip = loc_ip
        self.loc_port = loc_port
        global db_addr  # use global variable next:
        db_addr = ext_ip

    def Start(self):
        """
        Starts the HTTP server on a given IP and port.
        Uses **IP:port** provided on object initialization
        """
        webSrv = ThreadingHTTPServer((self.loc_ip, self.loc_port), _RequestHandler)
        print(f'\nHTTP> Server started on {self.loc_ip}:{self.loc_port}')
        try:
            webSrv.serve_forever()
        except KeyboardInterrupt:
            pass
        webSrv.server_close()
        print("\nHTTP> Server has stopped")

    def StartInThread(self):
        """
        [robust]
        Starts HTTP server in a new thread.
        This allows for the main program to continue running
        while the server runs in the background.
        @NOTE: will stop working when the main thread stops
        """
        ## "tuple()" - launch server with no additional params,
        ## this argument is required by start_new_method
        start_new_thread(self.Start, tuple())
