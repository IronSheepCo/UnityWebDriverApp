import requests

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
