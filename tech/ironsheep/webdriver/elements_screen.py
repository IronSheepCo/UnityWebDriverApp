from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.treeview import TreeView
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty

import requests
import json

from tech.ironsheep.webdriver.command import Config, Command, webelement_key_id
from tech.ironsheep.webdriver.treeview_text_input import TreeViewTextInput
from tech.ironsheep.webdriver.utils.utils import Utils

class ElementsScreen( Screen ):
    label = ObjectProperty(None)
    xpath_query = ObjectProperty(None)
    text_uuid = ObjectProperty(None)
    extra_param = ObjectProperty(None)
    response_area = ObjectProperty(None)
    test_case_view = ObjectProperty(None)
    
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
        #using strict=False as some elements
        #could have invalid characters in properties
        json_response = xpath_req.json(strict=False)
        print(json_response)
        #clean the tree view
        nodes = []
        for node in self.query_response.iterate_all_nodes():
            nodes.append( node )
        for node in nodes:
            self.query_response.remove_node( node )
        #populate the tree view
        for el in json_response["data"]:
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
        self.test_case_view.clear()

        if self.manager.has_screen('test_suite'):
            suite_screen = Screen()
            suite_screen = self.manager.get_screen('test_suite')
            suite_screen.test_suite_view.clear()
                

        print "Try to disconnect"
        #Config.server_ip = "127.0.0.1"

        try:
            print "Deleting current session"
            delete_session_req = requests.delete(Config.endpoint_session(""))
            print delete_session_req.json()

        except Exception:
            popup = Popup(title="Error", content=Label(text="Could not delete previous session"),
                          size_hint=(None, None), size=(300, 200))
            popup.open()

        #slide in the connect interface
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'connect'

    def on_enter(self):
        self.label.text = "connected to "+Config.server_ip
        self.query_response.bind(minimum_height=self.query_response.setter('height'))

    def show_test_suite(self):
        '''
        switch to test suite screen
        '''
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'test_suite'

    def add_to_suite(self):
        '''
        add current test case to current suite.
        If the current test case was not save we'll show a popup 
        and not insert the test case to suite.
        '''
        if self.test_case_view.testCaseSaved is False:
            popup = Popup(title="Warning",
                          content=Label(text="Current test case was not saved. \n Please save before adding to test suite.",
                                        halign='center'),
                          size_hint=(None, None),
                          size=(350, 200))
            popup.open()
        else:
            #add test case to current suite
            if self.manager.has_screen('test_suite'):
                suite_screen = Screen()
                suite_screen = self.manager.get_screen('test_suite')
                step = suite_screen.test_suite_view.add_test_suite_step()

                index = suite_screen.test_suite_view.test_suite.steps.index(step)
                rel_path, file_path = Utils.get_path_relative_to_path(self.test_case_view.test_case_path, suite_screen.test_suite_view.test_suite.test_suite_path, [self.test_case_view.test_case_name.text])
                suite_screen.test_suite_view.test_suite_stack.children[index].target_input.text = file_path
