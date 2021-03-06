import Queue
import threading
from threading import Lock
import socket
import time

UDP_BROADCAST_PORT = 23923
UDP_LISTENING_FOR_STRING = "echo for clients"
SERVER_BLACKOUT_TIME = 5

class BroadCastReceiver():

    listening_for_broadcast = True

    broadcast_message_received = False
    EventOneTimeListener = Queue.Queue()

    Server_suite = {}

    def Listener(self):
        print "Starting Loop:"
        while BroadCastReceiver.listening_for_broadcast is True:
            self.serverSock.settimeout(1.0)
            try:
                data, addr = self.serverSock.recvfrom(1024)
            except socket.timeout:
                #check for Server Expiration.
                mutex.acquire(True)
                self.CheckServerExpiration()
                mutex.release()
                continue
            #print "Message: ", data, addr
            if UDP_LISTENING_FOR_STRING in data:
                val = data.split("+++")
                name = ""
                device_id = ""
                counter = 0
                for element in val:
                    if counter is 1:
                        device_id = element
                    elif counter is 2:
                        name = element
                    counter += 1

                mutex.acquire(True)
                self.Server_suite[addr[0]] = [addr[1], time.time(), name, device_id]
                print "updating ip in suite: " + addr[0]
                self.CheckServerExpiration()
                mutex.release()

    # remove old Server Values from suite
    def CheckServerExpiration(self):
        t = time.time()
        keys_to_remove = []

        for key in self.Server_suite:
            if t - self.Server_suite[key][1] > SERVER_BLACKOUT_TIME:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            self.Server_suite.pop(key, None) # remove the value from the dictionary

    def __init__(self):
        BroadCastReceiver.listening_for_broadcast = True
        global mutex
        mutex = Lock()
        self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverSock.bind(('', UDP_BROADCAST_PORT))
        # start UDP listener on a new thread
        self.clientThread = threading.Thread(target=self.Listener).start()
