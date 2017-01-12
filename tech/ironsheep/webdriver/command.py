import requests
import json
import time

webelement_key_id = "element-6066-11e4-a52e-4f735466cecf"

class Config:
    SESSION_PORT = "4569"
    @staticmethod
    def endpoint(endpoint):
        return "http://"+Config.server_ip+":"+Config.SESSION_PORT+"/"+endpoint
    @staticmethod
    def endpoint_session(endpoint):
        return "http://"+Config.server_ip+":"+Config.SESSION_PORT+"/session/"+Config.session_id+"/"+endpoint

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
    def highlight(uuid):
        endpoint = 'element/'+uuid+'/highlight'
        response = requests.get( Config.endpoint_session(endpoint) )
        print( response.json() )
        return response.json()
    
