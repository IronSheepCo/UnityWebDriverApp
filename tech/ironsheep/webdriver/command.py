import requests
import json

class Config:
    @staticmethod
    def endpoint(endpoint):
        return "http://"+Config.server_ip+":8080/"+endpoint
    @staticmethod
    def endpoint_session(endpoint):
        return "http://"+Config.server_ip+":8080/session/"+Config.session_id+"/"+endpoint

class Command:
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
    
