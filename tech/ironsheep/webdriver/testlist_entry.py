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
from tech.ironsheep.webdriver.dialog import LoadDialog, SaveDialog

class TestListEntry(StackLayout):
    target_input = ObjectProperty(None)
    remove_button = ObjectProperty(None)
    load_test_button = ObjectProperty(None)
    step = None
    parent_testlist_view = None

    def __init__(self, **kwargs):
        super(TestListEntry, self).__init__(**kwargs)
        self.color_selected = [ 0.333, 0.251, 0.467 ,1]
        self._popup = None

    @staticmethod
    def load():
        return Builder.load_file('testlist_entry.kv')
 
    def move_cursor_real(self, dt):
        self.target_input.do_cursor_movement( 'cursor_home', True )
        self.target_input.focus = True
    
    def move_cursor(self):
        print('moving cursor')
        Clock.schedule_once( self.move_cursor_real, 0.1 )

    def on_target_input(self, instance, extra):
        self.target_input.bind(text=self.on_text)
        self.target_input.bind(focus=self.on_focus)
        
        #ugly hack here, 'cause I don'  t want to do 
        #an inheritance
        #doing some AOP here, calling the paste method 
        #but also our own cursor move to begining method
        old_paste = self.target_input.paste
        self.target_input.paste = types.MethodType(lambda _:[old_paste(),self.move_cursor()] , self.target_input)

    def on_text(self, instance, extra):
        if self.step is None:
            return
        self.step.target = self.target_input.text

    def on_focus(self, instance, value):
        if value: #object Focused
            if self.parent_testlist_view is not None:
                #print self.parent_testlist_view.selected_test_entry_index
                self.target_input.background_color = [0.733, 0.251, 0.467, 1]

                self.parent_testlist_view.set_current_step_index(self.step)
            else:
                self.target_input.background_color = [1, 1, 1, 1]
        else: #object losing focus
            self.target_input.background_color = [1, 1, 1, 1]

    def load_from_step(self):
        if self.step.target != "":
            self.target_input.text = self.step.target

    def remove_step(self):
        self.parent.remove_widget(self)
        self.parent_testlist_view.test_case.steps.remove(self.step)
        self.parent_testlist_view.test_case_list_stack.remove_widget(self)

    def move_up(self):
        self.parent_testlist_view.moveUp_testcase_entry(self.step)

    def move_down(self):
        self.parent_testlist_view.moveDown_testcase_entry(self.step)

    def load_test(self):
        print "loading test case into new List Step"
        if self._popup != None:
            self._popup.dismiss()

        content = LoadDialog(load=self.get_path, cancel=self.cancel)
        self._popup = Popup(title="Load test case", content=content,
                            size_hint=(0.8, 0.8))
        self._popup.open()

    def cancel(self):
        self._popup.dismiss()

    def get_path(self, path, filename):
        rel_path = os.path.relpath(path, Command.appDir)
        if rel_path == ".":
            the_path = filename[0][len(path)+1:]
        else:
            the_path = os.path.relpath(path, Command.appDir) + filename[0][len(path):]
        #print the_path
        self.target_input.text = the_path
        self.testCaseSaved = False

        self._popup.dismiss()
