from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.treeview import TreeView, TreeViewLabel

import requests
import json

webelement_key_id = "element-6066-11e4-a52e-4f735466cecf"

class Config:
    @staticmethod
    def endpoint(endpoint):
        return "http://"+Config.server_ip+":8080/"+endpoint
    @staticmethod
    def endpoint_session(endpoint):
        return "http://"+Config.server_ip+":8080/session/"+Config.session_id+"/"+endpoint

class ElementsScreen( Screen ):
    def __init__(self, **kwargs ):
        super( ElementsScreen, self).__init__(**kwargs)
        layout = StackLayout()
        height = 40
        self.add_widget( layout )
        #adding connect label
        self.label = Label( height=height, size_hint=(1, None) )
        layout.add_widget( self.label )
        #adding xpath query
        xpath_label = Label( text="XPath query", height=height, size_hint=(0.5, None) )
        layout.add_widget( xpath_label )
        #adding text input
        self.xpath_query = TextInput( multiline=False, height=height, size_hint=(0.5, None), text="//uibutton" )
        layout.add_widget( self.xpath_query )
        #adding button
        self.query_button = Button( text="Run query", height=height, size_hint=(1, None) )
        layout.add_widget( self.query_button )
        self.query_button.bind( on_press = self.run_query_callback )
        #query label
        query_response_label = Label( text="Response results", height=height, size_hint=(1,None) )
        layout.add_widget( query_response_label )
        #query response area
        self.query_response = TreeView(height=200, size_hint=(1,None), hide_root=True)
        layout.add_widget( self.query_response )

    def run_query_callback(self, instance):
        print("running xpath query "+self.xpath_query.text)
        payload = {"using":"xpath","value":self.xpath_query.text}
        xpath_req = requests.post( Config.endpoint_session("elements"), data=json.dumps(payload) )
        print(xpath_req.json())
        for el in xpath_req.json()["data"]:
            node = self.query_response.add_node( TreeViewLabel(text=el[webelement_key_id], is_open=True) )
            self.query_response.add_node( TreeViewLabel(text=el["name"]) , node )

    def on_enter(self):
        self.label.text = "connected to "+Config.server_ip


class ConnectScreen( Screen ):
    def __init__(self, **kwargs):
        super(ConnectScreen, self).__init__(**kwargs)
        layout = StackLayout()
        height = 40
        layout.add_widget(Label(text='Server IP', height=height, size_hint=(0.5, None)))
        self.ip = TextInput(multiline=False, height=height, size_hint=(0.5, None), text="127.0.0.1" )
        layout.add_widget( self.ip )
        self.connect_button = Button(text='Connect', height=height, size_hint=(1.0, None) )
        layout.add_widget( self.connect_button  )
        self.connect_button.bind( on_press = self.connect_callback )
        self.add_widget( layout )


    def connect_callback(self, instance):
        Config.server_ip = self.ip.text
        status_req = requests.get( Config.endpoint("status") )
        session_ready = status_req.json()["ready"]
        print( session_ready )
        if session_ready == False :
            print("DELETING SESSION")
            delete_session_req = requests.delete( Config.endpoint("session") )
            print( delete_session_req.json() )
        
        session_req = requests.post( Config.endpoint("session") )
        Config.session_id = session_req.json()["sessionId"]
        print("using session id "+Config.session_id)
        
        self.manager.current = 'elements'

class WebDriverApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget( ConnectScreen(name="connect") )
        self.sm.add_widget( ElementsScreen(name="elements") ) 
        return self.sm

    def on_stop(self):
        delete_req = requests.delete(Config.endpoint_session(""))
        print("deleting session with id "+Config.session_id)

if __name__ == '__main__':
    WebDriverApp().run()
