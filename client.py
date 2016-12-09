from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.treeview import TreeView, TreeViewLabel, TreeViewNode
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.lang import Builder

import requests
import json
import sys

from tech.ironsheep.webdriver.command import Config, Command

webelement_key_id = "element-6066-11e4-a52e-4f735466cecf"

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
    def __init__(self, **kwargs ):
        super( ElementsScreen, self).__init__(**kwargs)
        layout = StackLayout()
        height = 30
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
        query_response_label = Label( text="Response results", height=height, size_hint=(0.5, None) )
        layout.add_widget( query_response_label )
        #test case label
        layout.add_widget( Label( text="Current test case", height=height, size_hint=(0.5, None) ) )
        #scroll view
        scrollView = ScrollView( size_hint=(0.5, 0.5) )
        layout.add_widget( scrollView )
        #query response area
        self.query_response = TreeView(size_hint=(1,None), root_options={'text':'Results'} )
        self.query_response.bind(minimum_height= self.query_response.setter('height') )
        scrollView.add_widget( self.query_response )
        #test area
        test_label = Label( text="Test zone", height=height, size_hint=(1.0, None) )
        layout.add_widget( test_label )
        #uuid label
        uuid_label = Label( text="UUID", height=height, size_hint=(0.1, None), halign='left', valign='middle' )
        uuid_label.bind(size=uuid_label.setter('text_size'))
        layout.add_widget( uuid_label )
        #test uid
        self.text_uuid = TextInput( height=height, multiline=False, size_hint=(0.4, None) )
        layout.add_widget( self.text_uuid )
        #button for click
        click_button = Button( text="Click", height = height, size_hint=(0.15, None) )
        click_button.bind( on_press=self.pressed_click)
        layout.add_widget( click_button )
        #button for get attribute
        attribute_button = Button( text="Attribute", height = height, size_hint=(0.15, None) )
        attribute_button.bind( on_press=self.pressed_attribute )
        layout.add_widget( attribute_button )
        #button for sending keys
        send_keys_button = Button( text="Send keys", height = height, size_hint=(0.15, None) )
        send_keys_button.bind( on_press=self.pressed_send_keys )
        layout.add_widget( send_keys_button )
        #area for extra param
        extra_label = Label( text="Extra param", height=height, size_hint=(0.1, None), halign='left', valign='middle' )
        extra_label.bind( size=extra_label.setter('text_size') )
        layout.add_widget( extra_label )
        #test extra param
        self.extra_param = TextInput( height=height, multiline=False, size_hint=(0.4, None) )
        layout.add_widget( self.extra_param )
        #button for getting name
        get_name_button = Button( text="Name", height = height, size_hint=(0.15, None) )
        get_name_button.bind( on_press=self.pressed_get_name )
        layout.add_widget( get_name_button )
        #button for getting text
        get_text_button = Button( text="Text", height = height, size_hint=(0.15, None) )
        get_text_button.bind( on_press=self.pressed_get_text )
        layout.add_widget( get_text_button )
        #response label
        response_label = Label( text="Response", height=height, size_hint=(1,None) )
        layout.add_widget( response_label )
        #response area
        self.response_area = TextInput( height=2*height, size_hint=(1, None) )
        layout.add_widget( self.response_area )
    
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


class ConnectScreen( Screen ):
    def connect_callback(self, instance):
        Config.server_ip = self.ids["ip"].text
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

class WebDriverApp(App):
    def build(self):

        if getattr(sys, 'frozen', False):
                os.chdir(sys._MEIPASS)

        self.sm = ScreenManager()

        #self.sm.add_widget( ConnectScreen(name="connect") )
        self.sm.add_widget( Builder.load_file("connect_screen.kv") )
        self.sm.add_widget( ElementsScreen(name="elements") ) 
        return self.sm

    def on_stop(self):
        delete_req = requests.delete(Config.endpoint_session(""))
        print("deleting session with id "+Config.session_id)

if __name__ == '__main__':
    WebDriverApp().run()
