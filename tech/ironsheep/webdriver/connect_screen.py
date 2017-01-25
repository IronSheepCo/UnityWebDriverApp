from kivy.uix.screenmanager import Screen


from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label

from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.clock import Clock

import requests
import json
import os

import string
from functools import partial

from tech.ironsheep.webdriver.communication import BroadCastReceiver
from tech.ironsheep.webdriver.connect_entry import ConnectEntry
from tech.ironsheep.webdriver.command import Config

SERVER_SEARCH_TIME_DELAY = 1

class ConnectScreen( Screen ):
    ip = "None"
    port = ""
    connect_list = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ConnectScreen, self).__init__(**kwargs)    
        self.servers = {}
        Clock.schedule_interval(partial(ConnectScreen.timed_check, self), SERVER_SEARCH_TIME_DELAY)
        
    def addServer(self, ip, port, connectEntry):
        self.servers[ip] = [port, connectEntry]

    def add_connection_element(self, ip, port):
        print "Add Connection Element"
        ce = ConnectEntry.load()
        ce.screen = self
        self.connect_list.add_widget( ce )
        ce.target_ip.text = ce.target_ip.text + ip
        ce.target_port.text = ce.target_port.text + port
        ce.connect_button.text = "Connect"
        self.addServer(ip, port, ce)

    # Every second this method is called so we can check if we have 
    def timed_check(self, instance):
        for key in BroadCastReceiver.Server_list:
            if key not in self.servers:
                self.add_connection_element(str(key), str(BroadCastReceiver.Server_list[key][0]))

        keys_to_remove = []
        # remove all elements that are not in the Broadcast list anymore        
        for key in self.servers:
            if key not in BroadCastReceiver.Server_list:
                keys_to_remove.append(key)

        for key in keys_to_remove:            
            self.servers[key][1].parent.remove_widget(self.servers[key][1])
            self.servers.pop(key, None)# remove the value from the dictionary

    def fixed_connect_callback(self, instance):
        self.connect_to_server(instance, self.ids["ip"].text)

    def connect_to_server(self, instance, ip):
        Config.server_ip = ip
        print("clicked here")
        try:
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
        except Exception:
            popup = Popup( title="Error", content=Label(text="No server connection at specified ip"), size_hint=(None,None), size=(300,200) )
            popup.open()