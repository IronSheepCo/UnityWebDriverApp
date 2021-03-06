import requests
import json
import time
import subprocess
import threading
from threading import Lock

webelement_key_id = "element-6066-11e4-a52e-4f735466cecf"

class Config:
    session_id = ""
    SESSION_PORT = "4569"
    server_ip = ""
    @staticmethod
    def endpoint(endpoint):
        return "http://%s:%s/%s" % (Config.server_ip, Config.SESSION_PORT, endpoint )
    @staticmethod
    def endpoint_session(endpoint):
        return "http://%s:%s/session/%s/%s" %(Config.server_ip, Config.SESSION_PORT, Config.session_id, endpoint)

class Command:
    @staticmethod
    def intToText(no):
        if no == 1:
            return "Click"
        if no == 2:
            return "Get text"
        if no == 3:
            return "Get attribute"
        if no == 4:
            return "Get name"
        if no == 5:
            return "Wait"
        if no == 6:
            return "WaitForElement"
        if no == 7:
            return "WaitAndClick"
        if no == 8:
            return "WaitAndGetText"
        if no == 9:
            return "Visible"
        if no == 10:
            return "WaitAndGetName"
        if no == 11:
            return "WaitForVisible"
        if no == 12:
            return "AssertText"
        if no == 13:
            return "AssertAttribute"
        if no == 14:
            return "AssertVisible"
        if no == 15:
            return "AssertElement"
        if no == 16:
            return "RunShellScript"
        return ""

    @staticmethod
    def run_command_no(xpath_query, no, arg=None):
        timeout = 30

        if no == 5:
            time.sleep(float(xpath_query))
            return True
        if no == 6:
            try:
                timeout = float(arg)
            except ValueError:
                pass
            return Command.wait_for_element(xpath_query, timeout)
        if no == 7:
            try:
                timeout = float(arg)
            except ValueError:
                pass
            return Command.wait_and_click(xpath_query, timeout)
        if no == 8:
            try:
                timeout = float(arg)
            except ValueError:
                pass
            return Command.wait_and_get_text(xpath_query, timeout)
        if no == 10:
            try:
                timeout = float(arg)
            except ValueError:
                pass
            return Command.wait_and_get_name(xpath_query, timeout)
        if no == 11:
            try:
                timeout = float(arg)
            except ValueError:
                pass
            return Command.wait_for_visible(xpath_query, timeout)
        if no == 16:
            if arg == "": t = float(timeout)
            else: t = float(arg)
            return Command.run_shell_script(xpath_query, t)

        response = Command.run_query( xpath_query ).json(strict=False)

        if "data" in response:
            if len(response["data"]) == 0:
                #expecting result here
                #but none provided, so return False
                return False

            el = response["data"][0]
            uuid = el[webelement_key_id]

            if no == 1:
                Command.click(uuid)
            if no == 2:
                return Command.attribute(uuid, "text")
            if no == 3:
                return Command.attribute(uuid, arg)
            if no == 4:
                return Command.name(uuid)
            if no == 9:
                return Command.is_visible(uuid)
            if no == 12:
                return Command.assert_text(uuid, arg)
            if no == 13:
                split = arg.split("=")
                attr = split[0]
                value = split[1]
                return Command.assert_attribute(uuid, attr, value)
            if no == 14:
                return Command.is_visible(uuid)
            if no == 15:
                #this is ok, if the element is not found
                #we already return false
                #so this is ok :)
                return True
            return True
        else:
            return False

        return False

    @staticmethod
    def run_query(query):
        payload = {"using":"xpath","value":query}
        xpath_req = requests.post( Config.endpoint_session("elements"), data=json.dumps(payload) )
        return xpath_req

    @staticmethod
    def click(uuid):
        endpoint = 'element/'+uuid+'/click'
        print(endpoint)
        response = requests.get( Config.endpoint_session(endpoint) )
        print( response.json(strict=False) )
        return response.json(strict=False)
   
    @staticmethod
    def _check_for_data( json_data ):
        if "data" in json_data:
            return json_data["data"]
        else:
            return json_data["message"]

    @staticmethod
    def attribute(uuid,name):
        endpoint = 'element/'+uuid+'/attribute/'+name
        print(endpoint)
        response = requests.get( Config.endpoint_session(endpoint) )
        json_response = response.json(strict=False)
        print( json_response )
        return Command._check_for_data( json_response )

    @staticmethod
    def send_keys(uuid, keys):
        endpoint = 'element/'+uuid+'/value'
        print(endpoint)
        payload = {'text':keys}
        response = requests.post( Config.endpoint_session(endpoint), json=payload )
        print( response.json(strict=False) )
        return response.json(strict=False)
    
    @staticmethod
    def name(uuid):
        endpoint = 'element/'+uuid+'/name'
        print(endpoint)
        response = requests.get( Config.endpoint_session(endpoint) )
        print( response.json(strict=False) )
        return Command._check_for_data( response.json(strict=False) )

    @staticmethod
    def timeouts( implicit=-1, page_load=-1, script=-1):
        endpoint = 'timeouts'
        params = {}
        if implicit >= 0:
            params["implicit"] = int(implicit)
        if page_load >= 0:
            params["page load"] = int(page_load)
        if script >= 0:
            params["script"] = int(script)
        payload = {'parameters':params}
        
        response = requests.post( Config.endpoint_session(endpoint), json=payload)

        if 'error' in response.json(strict=False):
            return False
        else:
            return True

    @staticmethod
    def wait_for_element(xpath, timeout = 30):
        Command.timeouts( implicit=timeout*1000 )
        response = Command.run_query( xpath ).json(strict=False)
        if "data" in response:
            el = response["data"][0]
            uuid = el[webelement_key_id]
            return uuid
        return False
    
    @staticmethod
    def wait_and_click(xpath, timeout = 30):
        uuid = Command.wait_for_element( xpath, timeout)
        if uuid == False:
            return False
        return Command.click( uuid ) 

    @staticmethod
    def wait_and_get_text(xpath, timeout = 30):
        uuid = Command.wait_for_element( xpath, timeout)
        if uuid == False:
            return False
        return Command.attribute( uuid, "text" ) 
    
    @staticmethod
    def wait_and_get_name(xpath, timeout = 30):
        uuid = Command.wait_for_element( xpath, timeout)
        if uuid == False:
            return False
        return Command.name( uuid ) 
   
    @staticmethod
    def is_visible(uuid):
        endpoint = 'element/'+uuid+'/visible'
        response = requests.get( Config.endpoint_session(endpoint) )
        return Command._check_for_data( response.json(strict=False) )

    @staticmethod
    def assert_text(uuid, text_to_check):
       text = Command.attribute( uuid, "text")
       return text == text_to_check

    @staticmethod
    def assert_attribute(uuid, attr_name, attr_value):
        value = Command.attribute( uuid, attr_name )
        return value == attr_value

    @staticmethod
    def wait_for_visible(xpath, timeout = 30):
        now = time.time()
        while time.time() - now < timeout:
            response = Command.run_query( xpath ).json(strict=False)

            if "data" in response:
                if len(response["data"]) == 0:
                    #expecting result here
                    #but none provided, so return False
                    continue
            else:
                continue
            
            el = response["data"][0]
            uuid = el[webelement_key_id]

            is_visible = Command.is_visible( uuid )

            if is_visible == True:
                return True

        return False

    @staticmethod
    def highlight(uuid):
        endpoint = 'element/'+uuid+'/highlight'
        response = requests.get( Config.endpoint_session(endpoint) )
        print( response.json(strict=False) )
        return response.json(strict=False)

    @staticmethod
    def run_shell_script(script="ls", timeouts=30):
        global shell_cmd_mutex
        global shell_cmd_status
        shell_cmd_mutex = Lock()
        shell_cmd_status = True

        waitingTime = 0
        scriptThread = threading.Thread(target=Command.do_run_shell_script, args=[script, timeouts]).start()
        while waitingTime<timeouts and shell_cmd_mutex.locked() is True:
            time.sleep(0.5)
            waitingTime += 0.5
        
        if shell_cmd_mutex.locked():
            shell_cmd_mutex.release()
            scriptThread.exit()
            return False
        else:
            return shell_cmd_status is True #force it to return value not reference

        if scriptThread.isAlive():
            print "it is Alive!!!"
            scriptThread._stop()

    @staticmethod
    def do_run_shell_script(script, timeouts):
        try:
            shell_cmd_mutex.acquire(True)
            p = subprocess.check_call(script, cwd=str(Command.appDir), shell=True)
        except subprocess.CalledProcessError as e:
            print "Shell Script received an error:"
            print e.cmd
            shell_cmd_status = False

        shell_cmd_mutex.release()
