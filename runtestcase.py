import sys, getopt
import os
import socket
import requests

from tech.ironsheep.webdriver.testcase import TestCase, TestCaseStep
from tech.ironsheep.webdriver.utils import Utils
from tech.ironsheep.webdriver.command import Config


class RunTestCase:

    test_case = TestCase()
    UDP_BROADCAST_PORT = 23923
    UDP_LISTENING_FOR_STRING = "echo for clients"

    def main(self, argv):
        filePath = ""
        deviceID = ""
        try:
            opts, args = getopt.getopt(argv, "-p:-i:", ["filePath=", "path=", "deviceID=", "id="])
        except getopt.GetoptError:
            print 'runtestcase.py -path <absolute path> -id <device unique ID>'
            sys.exit(2)
        for opt, arg in opts:
            print opt
            if opt in ['-p', "--path", "--filePath"]:
                filePath = arg
            elif opt in ['-i', "--id", "--deviceID"]:
                deviceID = arg

        filePath = Utils.check_file_on_disk(filePath)
        deviceID = Utils.filter_device_id(deviceID)

        if not filePath:
            print "Invalid Test Case Path or File Not Found"
            print 'runtestcase.py --path <path to test case> --id <unique device ID>'
            return
        else:
            #print 'path is :', filePath
            pass

        if not deviceID:
            print "Invalid Device ID or Parameter Not Found"
            print 'runtestcase.py --path <path to test case> --id <unique device ID>'
            return
        else:
            #print 'device ID is :', deviceID
            pass

        #We have a valid FileName and deviceID

        if self.Listener(deviceID):
            print "Connected to Device ID: ", deviceID #we're good. We have connected to the device
            #pass 
        else:
            print "The provided Device ID was not found on the network or We could not connect to it"
            return

        content = ""
        with open(filePath, "r") as stream:
            content = stream.read()

        self.test_case = TestCase.loadFromJson(content)
        #print "test case step counter:", len(test_case.steps)

        try:
            result, step = self.test_case.run()
            self._test_case_run_step_result(result, step)

        except Exception:
            self.Disconnect()
            return

        self.Disconnect()

    def Disconnect(self):
        print "Try to disconnect"
        try:
            print "Deleting current session"
            delete_session_req = requests.delete(Config.endpoint_session(""))
            print delete_session_req.json()
        except Exception:
            pass


    def _test_case_run_step_result(self, status, info):
        if status is False:
            stack_len = len(self.test_case.steps)
            alert_text = "Test case failed at [b]step %i[/b] \n Step target: [b]%s[/b]"%(stack_len-info.no, info.target)
            print alert_text
        else:
            if info is None:
                alert_text = "Success"
                print alert_text
            else:
                pass
                print info
                #test_case.steps[info.no]

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
    RunTestCase().main(sys.argv[1:])
