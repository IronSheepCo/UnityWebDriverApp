from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.treeview import TreeView, TreeViewLabel, TreeViewNode
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.properties import ObjectProperty

import requests
import json
import sys

import Queue
import threading
import socket
import string

from tech.ironsheep.webdriver.command import Config, Command

webelement_key_id = "element-6066-11e4-a52e-4f735466cecf"

UDP_BROADCAST_PORT = 23923
UDP_LISTENING_FOR_STRING = "echo for clients"

class TestCaseEntry(StackLayout, TreeViewNode):
    def __init__(self, **kwargs):
        super(TestCaseEntry, self).__init__(**kwargs)

    @staticmethod
    def load():
        return Builder.load_file('test_case_entry.kv')

class TestCaseView(ScrollView):
    test_case_list = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(TestCaseView, self).__init__(**kwargs)

    def on_test_case_list(self, instance, value):
        self.test_case_list.bind(minimum_height=self.test_case_list.setter('height') )
    
    def load_test_pressed(self, instance):
        print("loading test case")

    def save_test_pressed(self, instance):
        print("saving test case")

    def add_step(self, instance):
        print("adding step")
        self.test_case_list.add_node(TestCaseEntry.load())

class TreeViewTextInput(TextInput,TreeViewNode):
    def __init__(self, **kwargs):
        super( TreeViewTextInput, self ).__init__(**kwargs)
        self.readonly = True
        self.multiline = False
        self.background_color = (0,0,0,0)
        self.height = 30
        self.foreground_color = (1, 1, 1, 1)
        self.color = (1, 1, 1, 1)
        self.bind( on_double_tap = self.copy_to_clipboard )
        #hack to make the text visible
        self.is_leaf = False

    def copy_to_clipboard(self, instance):
        print('copied to clipboard')
        self.copy( data=self.text )



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
        if response["data"] != None:
            self.response_area.text = response["data"]

    def pressed_get_name(self, instance):
        print('getting name '+self.text_uuid.text)
        
        response = Command.name( self.text_uuid.text )
        
        if response["data"] != None:
            self.response_area.text = response["data"]

    def run_query_callback(self, instance):
        print("running xpath query "+self.xpath_query.text)
        payload = {"using":"xpath","value":self.xpath_query.text}
        xpath_req = requests.post( Config.endpoint_session("elements"), data=json.dumps(payload) )
        print(xpath_req.json())
        #clean the tree view
        nodes = []
        for node in self.query_response.iterate_all_nodes():
            nodes.append( node )
        for node in nodes:
            self.query_response.remove_node( node )
        #populate the tree view
        for el in xpath_req.json()["data"]:
            node = self.query_response.add_node( TreeViewTextInput(text=el[webelement_key_id], is_open=True ) )
            self.query_response.add_node( TreeViewTextInput(text=el["name"], multiline=False), node )

    def on_enter(self):
        self.label.text = "connected to "+Config.server_ip
        self.query_response.bind(minimum_height=self.query_response.setter('height') )


class ConnectScreen( Screen ):
    ip = None

    @staticmethod
    def receive_ip(ip):
        ConnectScreen.ip = ip[0]

    def start_connect_callback(self, instance):
        #check if we received a broadcast message
        BroadCastReceiver.EventOneTimeListener.put(lambda n: ConnectScreen.receive_ip(n))

        if BroadCastReceiver.broadcast_message_received == True:
            CallbackQueue.run_callback_with_thread_nonblocking()
            #continue with connection
            if (ConnectScreen.ip != None):
                self.connect_callback(instance, ConnectScreen.ip)

    def connect_callback(self, instance, ip = None):
        if (ip == None):
            Config.server_ip = self.ids["ip"].text
        else:    
            Config.server_ip = ip
        print("clicked here")
        try:
            #print Config.server_ip
            #print Config.endpoint("status")
            status_req = requests.get( Config.endpoint("status") )
            session_ready = status_req.json()["ready"]
            #print status_req.json()
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

class WebDriverApp(App):
    def build(self):

        if getattr(sys, 'frozen', False):
                os.chdir(sys._MEIPASS)

        self.sm = ScreenManager()

        self.sm.add_widget( Builder.load_file("connect_screen.kv") )
        self.sm.add_widget( Builder.load_file("elements_screen.kv") )

        return self.sm

    def on_stop(self):
        delete_req = requests.delete(Config.endpoint_session(""))
        print("deleting session with id "+Config.session_id)




class CallbackQueue():
    callback_queue = Queue.Queue()

    @staticmethod
    def queue_callback_on_thread(func_to_call_from_main_thread):
        CallbackQueue.callback_queue.put(func_to_call_from_main_thread)

    @staticmethod
    def run_callback_with_thread_blocking():
        callback = CallbackQueue.callback_queue.get() #blocks until an item is available
        callback()

    @staticmethod
    def run_callback_with_thread_nonblocking():        
        while True:
            try:
                callback = CallbackQueue.callback_queue.get(False) #doesn't block
            except Queue.Empty: #raised when queue is empty
                break
            callback()

class BroadCastReceiver():
    #serverSock = socket
    broadcast_message_received = False
    EventOneTimeListener = Queue.Queue()

    def Listener(self):
        print "Starting Loop:"
        while self._stop is False:
            data, addr = self.serverSock.recvfrom(1024)            
            #print "Message: ", data, addr
            if (cmp(data, UDP_LISTENING_FOR_STRING) == 0 and BroadCastReceiver.broadcast_message_received == False): #broadcast received
                BroadCastReceiver.broadcast_message_received = True
                CallbackQueue.queue_callback_on_thread(lambda: BroadCastReceiver.Listener_Callback(data, addr))
                self._stop = True
    
    @staticmethod
    def Listener_Callback(data, addr):
        # add code to pass data on the main Thread
        print "Message: ", data, addr
        BroadCastReceiver.broadcast_message_received = False
        while True:
            try:
                callback = BroadCastReceiver.EventOneTimeListener.get(False)
            except Queue.Empty: #raised when queue is empty
                break
            callback(addr)

    def __init__(self):
        self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverSock.bind(('', UDP_BROADCAST_PORT))
        self._stop = False
        self.clientThread = threading.Thread(target=self.Listener).start() # start UDP listener on a new thread

        #while True: #test for Thread callback
        #    CallbackQueue.run_callback_with_thread_blocking()
    
if __name__ == '__main__':
    BroadCastReceiver() #start UDP client - move it on the Connect Button ?
    WebDriverApp().run()

