import requests
import json

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
    
