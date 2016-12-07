import requests

class Config:
    @staticmethod
    def endpoint(endpoint):
        return "http://"+Config.server_ip+":8080/"+endpoint
    @staticmethod
    def endpoint_session(endpoint):
        return "http://"+Config.server_ip+":8080/session/"+Config.session_id+"/"+endpoint

class Command:
    def click(self, uuid):
        pass
      # requests.post( 
