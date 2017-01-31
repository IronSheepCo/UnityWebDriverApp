from kivy.uix.stacklayout import StackLayout
from kivy.uix.button import Button
from kivy.uix.treeview import TreeViewLabel, TreeViewNode
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.clock import Clock

import types
import os

from tech.ironsheep.webdriver.command import Command

class TestCaseEntry(StackLayout, TreeViewNode):
    target_input = ObjectProperty(None)
    command_button = ObjectProperty(None)
    arg_input = ObjectProperty(None)
    remove_button = ObjectProperty(None)
    step = None
    parent_testcase_view = None

    def __init__(self, **kwargs):
        super(TestCaseEntry, self).__init__(**kwargs)
        self.color_selected = [ 0.333, 0.251, 0.467 ,1]

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

    def on_arg_input(self, instance, extra):
        self.arg_input.bind(text=self.on_args)
   
    def on_args(self, instance, extra):
        if self.step is None:
            return
        self.step.arg = self.arg_input.text

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
        if self.step.arg != "":
            self.arg_input.text = self.step.arg

    def remove_step(self):
        self.parent.remove_widget(self)
        self.parent_testcase_view.test_case.steps.remove(self.step)
        self.parent_testcase_view.test_case_list.remove_node(self)

    def move_up(self):
        index = self.parent_testcase_view.test_case.steps.index(self.step)
        if index > 0:

            prevNode = self.parent_testcase_view.test_case_list.root.nodes[index-1]
            currentNode = self.parent_testcase_view.test_case_list.root.nodes[index]

            node_command = prevNode.command_button.text
            node_input = prevNode.target_input.text
            node_arg_input = prevNode.arg_input.text

            prevNode.command_button.text = currentNode.command_button.text
            prevNode.target_input.text = currentNode.target_input.text
            prevNode.arg_input.text = currentNode.arg_input.text

            currentNode.command_button.text = node_command
            currentNode.target_input.text = node_input
            currentNode.arg_input.text = node_arg_input

            val1 = self.parent_testcase_view.test_case.steps[index-1]
            val2 = self.parent_testcase_view.test_case.steps[index]

            self.parent_testcase_view.test_case_list.children[index].step = val1
            self.parent_testcase_view.test_case_list.children[index-1].step = val2

    def move_down(self):
        index = self.parent_testcase_view.test_case.steps.index(self.step)
        if index < len(self.parent_testcase_view.test_case.steps)-1:

            nextNode = self.parent_testcase_view.test_case_list.root.nodes[index+1]
            currentNode = self.parent_testcase_view.test_case_list.root.nodes[index]

            node_command = nextNode.command_button.text
            node_input = nextNode.target_input.text
            node_arg_input = nextNode.arg_input.text

            nextNode.command_button.text = currentNode.command_button.text
            nextNode.target_input.text = currentNode.target_input.text
            nextNode.arg_input.text = currentNode.arg_input.text

            currentNode.command_button.text = node_command
            currentNode.target_input.text = node_input
            currentNode.arg_input.text = node_arg_input

            val1 = self.parent_testcase_view.test_case.steps[index+1]
            val2 = self.parent_testcase_view.test_case.steps[index]

            self.parent_testcase_view.test_case_list.children[index].step = val1
            self.parent_testcase_view.test_case_list.children[index+1].step = val2
