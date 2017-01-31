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
import traceback

import Queue
import threading
import socket
import string
import time
from functools import partial

from tech.ironsheep.webdriver.command import Config, Command, webelement_key_id
from tech.ironsheep.webdriver.testcase import TestCase, TestCaseStep
from tech.ironsheep.webdriver.communication import BroadCastReceiver
#from tech.ironsheep.webdriver.testcase_entry import TestCaseEntry
from tech.ironsheep.webdriver.testcase_view import TestCaseView
from tech.ironsheep.webdriver.elements_screen import ElementsScreen
from tech.ironsheep.webdriver.connect_screen import ConnectScreen
from tech.ironsheep.webdriver.connect_entry import ConnectEntry
from tech.ironsheep.webdriver.treeview_text_input import TreeViewTextInput
from tech.ironsheep.webdriver.dialog import LoadDialog, SaveDialog

class WebDriverApp(App):
    def build(self):

        if getattr(sys, 'frozen', False):
            os.chdir(sys._MEIPASS)

        self.sm = ScreenManager()

        self.sm.add_widget(Builder.load_file("connect_screen.kv"))
        self.sm.add_widget(Builder.load_file("elements_screen.kv"))

        return self.sm

    def on_stop(self):
        BroadCastReceiver.listening_for_broadcast = False
        if Config.server_ip != "" and Config.server_ip != None:
            print "deleting session with id " + Config.session_id
            delete_req = requests.delete(Config.endpoint_session(""))

Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)

if __name__ == '__main__':
    BroadCastReceiver() #start UDP client - move it on the Connect Button ?
    try:
        #catch unhandled exception
        WebDriverApp().run()
    except Exception as e:
        print("Stoping beacause of uncaught exception")
        print(e)
        print(traceback.print_exc())
        #allow app to finish gracefully
        #usually useful for closing 
        #the current web driver session
        App.get_running_app().stop()


