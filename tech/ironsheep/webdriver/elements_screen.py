from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.treeview import TreeView
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty

import requests
import json

from tech.ironsheep.webdriver.command import Config, Command, webelement_key_id
from tech.ironsheep.webdriver.treeview_text_input import TreeViewTextInput

class ElementsScreen( Screen ):
    label = ObjectProperty(None)
    xpath_query = ObjectProperty(None)
    text_uuid = ObjectProperty(None)
    extra_param = ObjectProperty(None)
    response_area = ObjectProperty(None)
    
    def pressed_click(self, instance):
        print('clicking element '+self.text_uuid.text)
        Command.click( self.text_uuid.text )

    def pressed_attribute(self, instance):
        print('getting attribute '+self.extra_param.text)
        Command.attribute( self.text_uuid.text, self.extra_param.text)

    def pressed_send_keys(self, instance):
        print('sending keys '+self.extra_param.text)
        Command.send_keys( self.text_uuid.text, self.extra_param.text)

    def pressed_get_text(self, instance):
        response = Command.attribute( self.text_uuid.text, 'text' )
        if response != None:
            self.response_area.text = response

    def pressed_get_name(self, instance):
        print('getting name '+self.text_uuid.text)
        
        response = Command.name( self.text_uuid.text )
        
        if response != None:
            self.response_area.text = response

    def pressed_highlight(self, instance):
        print('highlighting '+self.text_uuid.text)

        response = Command.highlight( self.text_uuid.text )

    def run_query_callback(self, instance):
        print("running xpath query "+self.xpath_query.text)
        xpath_req = Command.run_query( self.xpath_query.text )
        print(xpath_req.json())
        #clean the tree view
        nodes = []
        for node in self.query_response.iterate_all_nodes():
            nodes.append( node )
        for node in nodes:
            self.query_response.remove_node( node )
        #populate the tree view
        for el in xpath_req.json()["data"]:
            node = self.query_response.add_node( TreeViewTextInput(text=el["name"], is_open=False ) )
            self.query_response.add_node( TreeViewTextInput(text="uuid: %s"%el[webelement_key_id], multilin=False), node)
            for key in el:
                if key in ['name', webelement_key_id]:
                    continue
                self.query_response.add_node( TreeViewTextInput(text="%s : %s"%(key, el[key]), multiline=False), node)
            
    def run_clear_query_callback(self, instance):
        print "Clear Query"
        self.xpath_query.text = "//uibutton"
        
    def disconnect_from_app(self, instance):
        print "Try to disconnect"
        #Config.server_ip = "127.0.0.1"
        
        try:
            print("Deleting current session")
            delete_session_req = requests.delete(Config.endpoint_session(""))
            print( delete_session_req.json() )
              
        except Exception:
            popup = Popup( title="Error", content=Label(text="Could not delete previous session"), size_hint=(None,None), size=(300,200) )
            popup.open()
        
        #slide in the connect interface
        self.manager.current = 'connect'

    def on_enter(self):
        self.label.text = "connected to "+Config.server_ip
        self.query_response.bind(minimum_height=self.query_response.setter('height') )
