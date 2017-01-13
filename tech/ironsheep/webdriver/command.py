import requests
import json
import time

webelement_key_id = "element-6066-11e4-a52e-4f735466cecf"

class Config:
    SESSION_PORT = "4569"
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
        return ""

    @staticmethod
    def run_command_no(xpath_query, no):
        if no == 5:
            time.sleep( float(xpath_query) )
            return

        response = Command.run_query( xpath_query ).json()
        
        if "data" in response:
            el = response["data"][0]
            uuid = el[webelement_key_id]
            if no == 1:
                Command.click( uuid )
            if no == 6:
                Command.wait_for_element( xpath_query )
        else:
            return

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
        print( response.json() )
        return response.json()
    
    @staticmethod
    def attribute(uuid,name):
        endpoint = 'element/'+uuid+'/attribute/'+name
        print(endpoint)
        response = requests.get( Config.endpoint_session(endpoint) )
        print( response.json() )
        return response.json()

    @staticmethod
    def send_keys(uuid, keys):
        endpoint = 'element/'+uuid+'/value'
        print(endpoint)
        payload = {'text':keys}
        response = requests.post( Config.endpoint_session(endpoint), json=payload )
        print( response.json() )
        return response.json()
    
    @staticmethod
    def name(uuid):
        endpoint = 'element/'+uuid+'/name'
        print(endpoint)
        response = requests.get( Config.endpoint_session(endpoint) )
        print( response.json() )
        return response.json()

    @staticmethod
    def timeouts( implicit=-1, page_load=-1, script=-1):
        endpoint = 'timeouts'
        params = {}
        if implicit >= 0:
            params["implicit"] = implicit
        if page_load >= 0:
            params["page load"] = page_load
        if script >= 0:
            params["script"] = script
        payload = {'parameters':params}
        
        response = requests.post( Config.endpoint_session(endpoint), json=payload)

        if 'error' in response.json():
            return False
        else:
            return True

    @staticmethod
    def wait_for_element(xpath, timeout = 30):
        Command.timeouts( implicit=timeout*1000 )
        response = Command.run_query( xpath ).json()
        if "data" in response:
            return True
        return False

    @staticmethod
    def highlight(uuid):
        endpoint = 'element/'+uuid+'/highlight'
        response = requests.get( Config.endpoint_session(endpoint) )
        print( response.json() )
        return response.json()
    
