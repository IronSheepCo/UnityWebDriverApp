from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.floatlayout import FloatLayout
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
from kivy.uix.filechooser import FileChooserIconView
from kivy.factory import Factory
from kivy.clock import Clock

import requests
import json
import sys
import types
import os

import Queue
import threading
import socket
import string

from tech.ironsheep.webdriver.command import Config, Command, webelement_key_id
from tech.ironsheep.webdriver.testcase import TestCase, TestCaseStep


UDP_BROADCAST_PORT = 23923
UDP_LISTENING_FOR_STRING = "echo for clients"

class TestCaseEntry(StackLayout, TreeViewNode):
    target_input = ObjectProperty(None)
    command_button = ObjectProperty(None)
    step = None

    def __init__(self, **kwargs):
        super(TestCaseEntry, self).__init__(**kwargs)

    @staticmethod
    def load():
        return Builder.load_file('test_case_entry.kv')

    def command_choose(self, instance, no):
        self.popup.dismiss()
        self.command_no = no
        self.command_button.text = Command.intToText( no )
        self.step.command = no
 
    def move_cursor_real(self, dt):
        self.target_input.do_cursor_movement( 'cursor_home', True )
        self.target_input.focus = True
    
    def move_cursor(self):
        print('moving cursor')
        Clock.schedule_once( self.move_cursor_real, 0.1 )

    def on_target_input(self, instance, extra):
        self.target_input.bind(text=self.on_text)
        #ugly hack here, 'cause I don't want to do 
        #an inheritance
        #doing some AOP here, calling the paste method 
        #but also our own cursor move to begining method
        old_paste = self.target_input.paste
        self.target_input.paste = types.MethodType(lambda _:[old_paste(),self.move_cursor()] , self.target_input)

    def on_text(self, instance, extra):
        if self.step is None:
            return
        self.step.target = self.target_input.text

    def show_commands(self, instance):
        popup_content = Builder.load_file('choose_command_content.kv')
        
        popup_content.choose = types.MethodType(self.command_choose, popup_content)

        self.popup = Popup( title='Choose command',
                        content=popup_content,
                        size_hint=(None, None),
                        size=(300,300) )
        
        self.popup.open()


    def load_from_step(self):
        if self.step.command != "":
            self.command_button.text = Command.intToText( self.step.command )
            self.command_no = self.step.command
        if self.step.target != "":
            self.target_input.text = self.step.target

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)

class TestCaseView(ScrollView):
    test_case_list = ObjectProperty(None)
    test_case = TestCase()

    def __init__(self, **kwargs):
        super(TestCaseView, self).__init__(**kwargs)

    def cancel(self):
        self._popup.dismiss()

    def clear(self):
        print('clearing test case')
        nodes = []
        for node in self.test_case_list.iterate_all_nodes():
            nodes.append( node )
        for node in nodes:
            self.test_case_list.remove_node( node )

    def save(self, path, filename):
        with open( os.path.join(path, filename), "w" ) as stream:
            stream.write( self.test_case.toJson() )
        self._popup.dismiss()
    
    def load(self, path, filename):
        content = ""
        with open( os.path.join(path, filename[0]), "r" ) as stream:
            content = stream.read()

        #clearing existing test case
        self.clear()

        self.test_case = TestCase.loadFromJson( content )

        for step in self.test_case.steps:
            self.add_step_view( step )

        self._popup.dismiss()
    
    def on_test_case_list(self, instance, value):
        self.test_case_list.bind(minimum_height=self.test_case_list.setter('height') )
    
    def run_test_case(self, instance):
        print( "running test case")
        self.test_case.run()

    def load_test_pressed(self, instance):
        print("loading test case")
        content = LoadDialog( load=self.load, cancel=self.cancel )
        self._popup = Popup( title="Save test case", content=content, 
                             size_hint=(0.8, 0.8) )
        self._popup.open()
    
    def save_test_pressed(self, instance):
        print("saving test case")
        content = SaveDialog( save=self.save, cancel=self.cancel )
        self._popup = Popup( title="Save test case", content=content, 
                             size_hint=(0.8, 0.8) )
        self._popup.open()

    def add_step_view(self, step):
        tce = TestCaseEntry.load()
        tce.step = step
        self.test_case_list.add_node( tce )
        tce.load_from_step()
        tce.move_cursor()
    
    def add_step(self, instance):
        print("adding step")
        step = TestCaseStep()
        self.test_case.addStep( step )
        self.add_step_view( step )

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

    def auto_connect_callback(self, instance):
        #check if we received a broadcast message
        BroadCastReceiver.EventOneTimeListener.put(lambda n: ConnectScreen.receive_ip(n))

        if BroadCastReceiver.broadcast_message_received == True:
            CallbackQueue.run_callback_with_thread_nonblocking()
            #continue with connection
            if (ConnectScreen.ip != None): #only if we received an IP from a Broadcast
                self.connect_callback(instance, ConnectScreen.ip)

    def fixed_connect_callback(self, instance):
        self.connect_callback(instance, self.ids["ip"].text)

    def connect_callback(self, instance, ip):
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

import time
class WebDriverApp(App):
    def build(self):

        if getattr(sys, 'frozen', False):
            os.chdir(sys._MEIPASS)

        self.sm = ScreenManager()

        self.sm.add_widget( Builder.load_file("connect_screen.kv") )
        self.sm.add_widget( Builder.load_file("elements_screen.kv") )

        return self.sm

    def on_stop(self):
        Config.listening_for_broadcast = False
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
        while Config.listening_for_broadcast is True:
            self.serverSock.settimeout(1.0)
            try:
                data, addr = self.serverSock.recvfrom(1024)            
            except socket.timeout:
                continue
            #print "Message: ", data, addr
            if (cmp(data, UDP_LISTENING_FOR_STRING) == 0 and BroadCastReceiver.broadcast_message_received == False): #broadcast received
                BroadCastReceiver.broadcast_message_received = True
                CallbackQueue.queue_callback_on_thread(lambda: BroadCastReceiver.Listener_Callback(data, addr))
                Config.listening_for_broadcast = False
    
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
        self.clientThread = threading.Thread(target=self.Listener).start() # start UDP listener on a new thread

Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)

if __name__ == '__main__':
    Config.listening_for_broadcast = True
    BroadCastReceiver() #start UDP client - move it on the Connect Button ?
    WebDriverApp().run()

