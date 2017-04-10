from kivy.uix.label import Label
from kivy.uix.stacklayout import StackLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, SlideTransition
import json
import os

from tech.ironsheep.webdriver.testsuite_entry import TestSuiteEntry
from tech.ironsheep.webdriver.testsuite import TestSuite, TestSuiteStep
from tech.ironsheep.webdriver.utils.utils import Utils
from tech.ironsheep.webdriver.dialog import LoadDialog, SaveDialog
from tech.ironsheep.webdriver.confirmPopup import ConfirmPopup
from tech.ironsheep.webdriver.command import Config

class TestSuiteView(StackLayout):
    test_suite_name = ObjectProperty(None) # this is the test Suite FileName without the path
    test_suite_stack = ObjectProperty(None)
    test_suite_path = None # this is the folder of the Test Suite File
    last_loaded_path = None

    my_screen = Screen()

    test_suite = TestSuite()

    def __init__(self, **kwargs):
        super(TestSuiteView, self).__init__(**kwargs)
        self.selected_test_suite_entry_index = 0
        self.testSuiteSaved = True
        self._popup = None

    def show_test_case(self):
        self.my_screen.manager.transition = SlideTransition(direction='right')
        self.my_screen.manager.current = 'elements'

    def cancel(self):
        '''
        dismiss the active popup.
        '''
        self._popup.dismiss()

    def load_test_suite_pressed(self, instance):
        if self._popup != None:
            self._popup.dismiss()

        print "last_loaded_path=", self.last_loaded_path

        if not self.last_loaded_path is None:
            content = LoadDialog(load=self.load,
                                 cancel=self.cancel,
                                 fileFilter=['*.ts'],
                                 pathToLoad=self.last_loaded_path)
        else:
            content = LoadDialog(load=self.load,
                                 cancel=self.cancel,
                                 fileFilter=['*.ts'])

        self._popup = Popup(title="Load test suite", content=content,
                            size_hint=(0.8, 0.8))
        self._popup.open()
    
    def load(self, path, filename):
        content = ""
        if not filename:
            return

        with open(os.path.join(path, Utils.get_filename_from_path(filename[0])), "r") as stream:
            content = stream.read()

        #clearing existing test case
        self.clear()

        self.test_suite = TestSuite.loadFromJson(content)

        for step in reversed(self.test_suite.steps):
            self.add_stack_step_view(step)

        self.test_suite_path, file_path = Utils.get_path_relative_to_app(path, filename)
        self.last_loaded_path = self.test_suite_path #only for opening FileBrowser on last directory
        self.test_suite_name.text = Utils.get_filename_from_path(file_path)
        self.testSuiteSaved = True

        self._popup.dismiss()

    def save_test_suite_pressed(self, instance):
        print "saving test suite"

        if not self.last_loaded_path is None:
            content = SaveDialog(save=self.save,
                                 cancel=self.cancel,
                                 fileFilter=['*.ts'],
                                 pathToLoad=self.last_loaded_path)
        else:
            content = SaveDialog(save=self.save,
                                 cancel=self.cancel,
                                 fileFilter=['*.ts'])

        self._popup = Popup(title="Save test suite", content=content,
                            size_hint=(0.8, 0.8))
        self._popup.open()

    def save(self, path, filename):
        #remove all illegal characters.
        new_filename = Utils.get_valid_filename(Utils.get_filename_from_path(filename))

        #if the user tries to save the file with no name,
        #or the name of just the extension, we return. (no saving)
        if len(new_filename) == 0 or new_filename == ".ts":
            return

        suite_name = new_filename
        if len(new_filename) >= 3:
            if new_filename[len(new_filename)-3:] != ".ts":
                new_filename += ".ts"
        else:
            new_filename += ".ts"
        with open(os.path.join(path, new_filename), "w") as stream:
            stream.write(self.test_suite.toJson(suite_name))

        self._popup.dismiss()
        self.testSuiteSaved = True

        self.test_suite_path, file_path = Utils.get_path_relative_to_app(path, new_filename)
        self.last_loaded_path = self.test_suite_path #only for opening FileBrowser on last directory
        self.test_suite_name.text = new_filename

    def add_test_suite_step(self):
        print "adding test suite step"
        step = TestSuiteStep()

        self.test_suite.addStep(step, self.selected_test_suite_entry_index)
        self.add_test_suite_view(step, self.selected_test_suite_entry_index)

        self.testSuiteSaved = False
        return step

    def add_test_suite_view(self, step, index=None):
        tce = TestSuiteEntry.load()
        tce.step = step
        tce.parent_testsuite_view = self
        if index is None:
            index = 0
        elif index < 0:
            index = 0
        elif index >= len(self.test_suite_stack.children):
            index = len(self.test_suite_stack.children)-1

        self.test_suite_stack.add_widget(tce, index)

        tce.load_from_step()
        tce.target_input.focus = True#.move_cursor()

    def set_current_step_index(self, step):
        index = self.test_suite.steps.index(step)
        self.selected_test_suite_entry_index = index

    def clear(self):
        print('clearing test case suite')
        nodes = []
        for node in self.test_suite_stack.children:
            nodes.append( node )
        for node in nodes:
            self.test_suite_stack.remove_widget( node )
            self.test_suite.steps.remove(node.step)
        self.testSuiteSaved = True
        self.test_suite_name.text = "Current Test Case Suite"

    def add_stack_step_view(self, step, index=None):
        tce = TestSuiteEntry.load()
        tce.step = step
        tce.parent_testsuite_view = self
        if index is None:
            index = 0
        elif index < 0:
            index = 0
        elif index >= len(self.test_suite_stack.children):
            index = len(self.test_suite_stack.children)-1

        self.test_suite_stack.add_widget(tce, index)

        tce.load_from_step()
        tce.target_input.focus = True#.move_cursor()

    def moveUp_test_entry(self, step):
        index = self.test_suite.steps.index(step)
        if index < len(self.test_suite.steps)-1:
            self.switch_test_entries(index, index+1)
        else:
            self.switch_test_entries(index, 0)
        self.testSuiteSaved = False

    def moveDown_test_entry(self, step):
        index = self.test_suite.steps.index(step)
        if index > 0:
            self.switch_test_entries(index, index-1)
        else:
            self.switch_test_entries(index, len(self.test_suite.steps)-1)
        self.testSuiteSaved = False

    def switch_test_entries(self, index_1, index_2):
        val1 = self.test_suite.steps[index_1]
        val2 = self.test_suite.steps[index_2]

        prevNode = self.test_suite_stack.children[index_1]
        prevNode.step = val1
        currentNode = self.test_suite_stack.children[index_2]
        currentNode.step = val2

        node_input = prevNode.target_input.text
        prevNode.target_input.text = currentNode.target_input.text
        currentNode.target_input.text = node_input

    def run_test_suite(self, instance):
        print( "running test suite")
        self.test_suite.run(self._test_suite_run_step_result)

    def _test_suite_run_step_result(self, status, info):
        if status is False:
            stack_len = len(self.test_suite_stack.children)
            alert_text = "Test suite failed at [b]step %i[/b] \n Step target: [b]%s[/b]"%(stack_len-info.no, info.target)

            alert = Popup(title="Error running test suite",
                          content=Label(text=alert_text,
                          halign="center",
                          markup=True),
                          size_hint=(0.6, 0.5)
                         )

            alert.open()
        else:
            if info is None:
                alert_text = "Success"
                alert = Popup(title="Test suite result",
                              content=Label(text=alert_text,
                              halign="center",
                              markup=True),
                              size_hint=(0.4, 0.4)
                             )

                alert.open()
            else:
                stack_len = len(self.test_suite_stack.children)
                node_to_select = self.test_suite_stack.children[info.no]

                #print "try to focus"
                self.test_suite_stack.children[info.no].on_focus(None, True)
                if info.no < stack_len-1:
                    self.test_suite_stack.children[info.no+1].on_focus(None, False)

                self.test_suite_stack.parent.scroll_to(self.test_suite_stack.children[ info.no ])

