import socket
import _pickle as pickle

# setup TCP sockets
UDP_IP = "224.1.1.1"
UDP_PORT = 4444

# setup UDP sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", UDP_PORT))
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(UDP_IP) + socket.inet_aton("0.0.0.0"))

# FUNCTIONS
def receive_udp():
    try:
        data, addr = sock.recvfrom(1024)
        print(data.decode('big5'))
    except socket.error as e:
        print("Error receiving UDP data:", e)

# CLASS
class Network:
    """
    class to connect, send and recieve information from the server

    need to hardcode the host attirbute to be the server's ip
    """
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.client.settimeout(10.0)
        self.host = "192.168.1.119" # Need to change to Server ip
        self.port = 5555
        self.addr = (self.host, self.port)

    def connect(self, name):
        """
        connects to server and returns the id of the client that connected
        :param name: str
        :return: int reprsenting id
        """
        try:
            self.client.connect(self.addr)
            self.client.send(str.encode(name))
            receive_udp()
            val = self.client.recv(8)
            return int(val.decode()) # can be int because will be an int id
        except socket.error as e:
            print("Error connecting to the server:", e)
            return None

    def disconnect(self):
        """
        disconnects from the server
        :return: None
        """
        try:
            self.client.close()
            sock.close()
        except socket.error as e:
            print("Error disconnecting from the server:", e)


    def send(self, data, pick=False):
        """
        sends information to the server

        :param data: str
        :param pick: boolean if should pickle or not
        :return: str
        """
        try:
            if pick:
                self.client.send(pickle.dumps(data))
            else:
                self.client.send(str.encode(data))
            reply = self.client.recv(2048*4)
            try:
                reply = pickle.loads(reply)
            except Exception as e:
                print("Error unpickling received data:", e)

            return reply
        except socket.error as e:
            print("Error sending data to the server:", e)
