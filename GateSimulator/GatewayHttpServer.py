from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from _thread import start_new_thread
from threading import Timer


class _RequestHandler(BaseHTTPRequestHandler):
    timeout = 12
    def do_GET(self):
        self.send_response(200)
        print(f'\nGATE_SIM/SERVER> Gate open for {self.timeout} seconds')
        Timer(self.timeout, lambda: print('GATE_SIM/SERVER> Gate closed')).start()

class GatewayHttpServer:
    def Start(self):
        webSrv = ThreadingHTTPServer((self.ip, self.port), _RequestHandler)
        print(f'\nGATE_SIM/SERVER> Server started on {self.ip}:{self.port}')
        try:
            webSrv.serve_forever()
        except KeyboardInterrupt:
            pass
        webSrv.server_close()
        print("\nGATE_SIM/SERVER> Server has stopped")

    def StartInThread(self):
        ## Launch server with no arguments ("tuple()")
        ## using new thread
        #@ Note: will stop working when the main program ends
        start_new_thread(self.Start, tuple())

    def __init__(self, ip='localhost', port=9090):
        self.ip = ip
        self.port = port
