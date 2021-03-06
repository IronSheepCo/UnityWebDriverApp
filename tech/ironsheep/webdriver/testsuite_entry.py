from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.treeview import TreeViewLabel, TreeViewNode
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, SlideTransition

import types
import os

from tech.ironsheep.webdriver.command import Command
from tech.ironsheep.webdriver.dialog import LoadDialog, SaveDialog
from tech.ironsheep.webdriver.utils.utils import Utils

class TestSuiteEntry(StackLayout):
    target_input = ObjectProperty(None)
    remove_button = ObjectProperty(None)
    load_test_button = ObjectProperty(None)
    step = None
    parent_testsuite_view = None

    def __init__(self, **kwargs):
        super(TestSuiteEntry, self).__init__(**kwargs)
        self.color_selected = [ 0.333, 0.251, 0.467 ,1]
        self._popup = None

    @staticmethod
    def load():
        return Builder.load_file('testsuite_entry.kv')
 
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
            if self.parent_testsuite_view is not None:
                #print self.parent_testsuite_view.selected_test_entry_index
                self.target_input.background_color = [0.733, 0.251, 0.467, 1]

                self.parent_testsuite_view.set_current_step_index(self.step)
            else:
                self.target_input.background_color = [1, 1, 1, 1]
        else: #object losing focus
            self.target_input.background_color = [1, 1, 1, 1]

    def load_from_step(self):
        if self.step.target != "":
            self.target_input.text = self.step.target

    def remove_step(self):
        self.parent.remove_widget(self)
        self.parent_testsuite_view.test_suite.steps.remove(self.step)
        self.parent_testsuite_view.test_suite_stack.remove_widget(self)

    def move_up(self):
        self.parent_testsuite_view.moveUp_test_entry(self.step)

    def move_down(self):
        self.parent_testsuite_view.moveDown_test_entry(self.step)

    def load_test(self):
        print "loading test case into new Suite Step"
        if self._popup != None:
            self._popup.dismiss()

        if not Utils.get_last_loaded_path() is None:
            content = LoadDialog(load=self.load_path,
                                 cancel=self.cancel,
                                 fileFilter=['*.tc'],
                                 pathToLoad=Utils.get_last_loaded_path())
        else:
            content = LoadDialog(load=self.load_path,
                                 cancel=self.cancel,
                                 fileFilter=['*.tc'])

        self._popup = Popup(title="Load test case", content=content,
                            size_hint=(0.8, 0.8))
        self._popup.open()

    def cancel(self):
        self._popup.dismiss()

    def load_path(self, path, filename):
        if self.parent_testsuite_view.test_suite.test_suite_path is None:
            abs_path = path
            a, rel_path = Utils.get_path_relative_to_app(abs_path, filename)
        else:
            abs_path = path
            suite_abs_path = Utils.get_absolute_path(self.parent_testsuite_view.test_suite.test_suite_path)
            a, rel_path = Utils.get_path_relative_to_path(abs_path, suite_abs_path, filename)

        self.target_input.text = rel_path

        self.parent_testsuite_view.testSuiteSaved = False
        rel_path, b = Utils.get_path_relative_to_app(path, filename)
        Utils.set_last_loaded_path(rel_path)
        self._popup.dismiss()

    def edit_test(self):
        if self.parent_testsuite_view.my_screen.manager.has_screen('elements'):
            elements_screen = Screen()
            elements_screen = self.parent_testsuite_view.my_screen.manager.get_screen('elements')

            if self.parent_testsuite_view.test_suite.test_suite_path is None:
                new_file = self.target_input.text
            else:
                new_file = os.path.join(self.parent_testsuite_view.test_suite.test_suite_path, self.target_input.text)
            asb_file_path = Utils.get_absolute_path(new_file)

            #check existing file
            if os.path.isfile(asb_file_path):
                filename = [2]
                filename[0] = asb_file_path
                path = os.path.dirname(asb_file_path)

                elements_screen.test_case_view.load(path=path,
                                                    filename=filename,
                                                    dontSaveFilePath=True)
                self.parent_testsuite_view.show_test_case()
            else:
                # show popup with Warning: file not found
                alert_text = "File not found at path:\n[b]%s[/b]"%(self.target_input.text)
                alert = Popup(title="Warning",
                              content=Label(text=alert_text,
                                            halign="center",
                                            markup=True),
                              size_hint=(0.6, 0.5))
                alert.open()



