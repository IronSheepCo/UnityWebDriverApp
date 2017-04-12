import sys, getopt
import os
import socket
import requests

from tech.ironsheep.webdriver.command import Config
from tech.ironsheep.webdriver.utils.utils import Utils
from tech.ironsheep.webdriver.utils.testSuiteUtils import TestSuiteUtils

class RunTestSuite:

    UDP_BROADCAST_PORT = 23923
    UDP_LISTENING_FOR_STRING = "echo for clients"

    def RunWithParams(self, device_id, file_path):
        self.Run(device_id, file_path)

    def RunWithArgs(self, argv):
        filePath = ""
        deviceID = ""
        try:
            opts, args = getopt.getopt(argv, "-p:-i:", ["filePath=", "path=", "deviceID=", "id="])
        except getopt.GetoptError:
            print 'runtestsuite.py -path <absolute path> -id <device unique ID>'
            sys.exit(2)
        for opt, arg in opts:
            print opt
            if opt in ['-p', "--path", "--filePath"]:
                filePath = arg
            elif opt in ['-i', "--id", "--deviceID"]:
                deviceID = arg

        self.Run(deviceID, filePath)

    def Run(self, device_id, file_path):
        filePath = Utils.check_file_on_disk(file_path)
        deviceID = Utils.filter_device_id(device_id)

        if not filePath:
            print "Invalid Test Suite Path or File Not Found"
            #print 'runtestsuite.py --path <path to test suite> --id <unique device ID>'
            return
        else:
            #print 'path is :', filePath
            pass

        if not deviceID:
            print "Invalid Device ID or Parameter Not Found"
            #print 'runtestsuite.py --path <path to test case> --id <unique device ID>'
            return
        else:
            #print 'device ID is :', deviceID
            pass

        #We have a valid FileName and deviceID

        if self.Listener(deviceID):
            print "Connected to Device ID: ", deviceID #we're good. We have connected to the device
        else:
            print "The provided Device ID was not found on the network or We could not connect to it"
            return

        TestSuiteUtils.DoRunTestSuite(filePath)
        self.Disconnect()

    def Disconnect(self):
        print "Try to disconnect"
        try:
            print "Deleting current session"
            delete_session_req = requests.delete(Config.endpoint_session(""))
            print delete_session_req.json()
        except Exception:
            pass

    def Listener(self, device):
        print "Starting Loop:"
        device_connected = False

        serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serverSock.bind(('', self.UDP_BROADCAST_PORT))

        while device_connected is False:
            serverSock.settimeout(1.0)
            try:
                data, addr = serverSock.recvfrom(1024)
            except socket.timeout:
                continue
            #print "Message: ", data, addr
            if self.UDP_LISTENING_FOR_STRING in data:
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

                if device_id == device:
                    device_connected = True
                    if self.ConnectToServer(addr[0]) is False:
                        return False
                    return True
                else:
                    continue

    def ConnectToServer(self, ip):
        print "try to connect to a certain server ip: " + ip
        Config.server_ip = ip
        try:
            status_req = requests.get(Config.endpoint("status"))
            session_ready = status_req.json()["ready"]
            print session_ready
            if session_ready is False:
                print "DELETING SESSION"
                delete_session_req = requests.delete(Config.endpoint("session"))
                print delete_session_req.json()

            session_req = requests.post(Config.endpoint("session"))
            Config.session_id = session_req.json()["sessionId"]
            print "using session id "+Config.session_id

        except Exception:
            print "No server connection at specified ip"
            return False
        return True


if __name__ == "__main__":
    RunTestSuite().RunWithArgs(sys.argv[1:])
