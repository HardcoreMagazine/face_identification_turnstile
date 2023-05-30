from GatewayHttpServer import GatewayHttpServer
from GatewayHttpClient import GatewayHttpClient

if __name__ == '__main__':
    GatewayHttpServer(ip='192.168.1.5').StartInThread()
    GatewayHttpClient(loc_ip='192.168.1.5',ext_ip='192.168.1.6').Launch()

