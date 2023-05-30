import http.client
import time

class GatewayHttpClient:
    """
    Request types:
    * 1 - open gate [localhost:9090] - test purposes only!
    * 2 - trigger MySQL request on detector module [localhost:8080/query] - test purposes only!
    * 3 - trigger PHOTO request on detector module [localhost:8080/photo]
    """
    def __send_request(self, addr, req_type, name=None, path=None):
        try:
            conn = http.client.HTTPConnection(addr, timeout=5)
            if name and path:
                conn.request(method=req_type, url=path, body=name)
            else:
                conn.request(req_type, "/")
            resp = conn.getresponse()
            print(f'GATE_SIM/CLIENT> STATUS: {resp.status}/{resp.reason}; {resp.read()}')
            resp.close()
            conn.close()
        except ConnectionRefusedError:
            print(f'GATE_SIM/CLIENT> Unable to reach server \"{addr}\"')

    def Launch(self):
        time.sleep(1) # delay to exclude console jabbering
        print('GATE_SIM/CLIENT> Request types: 1 - open gates; 2 - send mysql '
              'query of USER; 3 - take photo of USER')
        print('GATE_SIM/CLIENT> Any other numeric input will stop this client')
        while True:
            try:
                reqType = int(input('GATE_SIM/CLIENT> Select request type: '))
                if reqType < 1 or reqType > 3:
                    break
                if reqType == 1:
                    self.__send_request(f"{self.loc_ip}:{self.loc_port}", "GET")
                    time.sleep(12+1)
                    # 12 -> gates delay (time until closed) +1 to exclude console jabbering
                    continue
                name = input('GATE_SIM/CLIENT> Select visitor name: ')
                if len(name) == 0 or name.isspace():
                    print('GATE_SIM/CLIENT> Empty name selected')
                    continue
                name = name.upper()
                if reqType == 2:
                    self.__send_request(f"{self.ext_ip}:{self.ext_port}", "POST", name, "/query")
                elif reqType == 3:
                    self.__send_request(f"{self.ext_ip}:{self.ext_port}", "POST", name, "/photo")
            except ValueError:
                #print('GATE_SIM/CLIENT> Number conversion error')
                pass
            except KeyboardInterrupt:
                pass

    def __init__(self, loc_ip='localhost', loc_port=9090, ext_ip='localhost', ext_port=8080):
        self.loc_ip = loc_ip
        self.loc_port = loc_port
        self.ext_ip = ext_ip
        self.ext_port = ext_port
