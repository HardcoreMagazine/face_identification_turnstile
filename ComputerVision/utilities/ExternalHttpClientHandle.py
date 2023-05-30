import http.client
from datetime import datetime
from utilities.MySQLConnector import MySQLConnector as mql


class CVHttpClient:
    def __send_request(self, addr, name):
        """
        Sends an HTTP GET request to the server.
        :param addr: server address (gate)
        :param name: user's name to display on gate
        """
        conn = http.client.HTTPConnection(addr, timeout=5)
        conn.request("GET", "/", body=name)
        resp = conn.getresponse()
        print(f'\nCV/CLIENT> STATUS: {resp.status}/{resp.reason} @ {resp.read()}')
        resp.close()
        conn.close()

    def LaunchAndRequest(self, name):
        """
        Launches MySQL journal query and opens gate.
        :param name: user name to journal.
        """
        try:
            mql(host=self.db_ip).ConnectAndQuery(name, datetime.now())
            self.__send_request(f"{self.ext_ip}:{self.ext_port}", name)
        except ConnectionRefusedError: # Unknown error or KeyboardInterrupt
            print(f'\nCV/CLIENT> Unable to reach server \"{self.ext_ip}:{self.ext_port}\"')
        except Exception: # KeyboardInterrupt or any other (unknown) error
            pass

    def __init__(self, ext_ip, ext_port, db_ip):
        """
        Called when the class is instantiated.
        It initializes a few variables.
        :param self: Represent the instance of the class
        :param ext_ip: IPv4 address of remote server (gate)
        :param ext_port: port number of remote server (gate)
        :param db_ip: IPv4 address of remote server (database)
        """
        self.ext_ip = ext_ip
        self.ext_port = ext_port
        self.db_ip = db_ip

