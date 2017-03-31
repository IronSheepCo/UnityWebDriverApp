from kivy.uix.stacklayout import StackLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, SlideTransition
import json
import os

from tech.ironsheep.webdriver.testsuite_entry import TestSuiteEntry
from tech.ironsheep.webdriver.testsuite import TestSuite, TestSuiteStep
from tech.ironsheep.webdriver.utils import Utils
from tech.ironsheep.webdriver.dialog import LoadDialog, SaveDialog
from tech.ironsheep.webdriver.confirmPopup import ConfirmPopup
from tech.ironsheep.webdriver.command import Config

class TestSuiteView(StackLayout):
    test_case_suite_name = ObjectProperty(None)
    test_case_suite_stack = ObjectProperty(None)

    my_screen = Screen()

    test_case_suite = TestSuite()

    def __init__(self, **kwargs):
        super(TestSuiteView, self).__init__(**kwargs)
        self.selected_test_suite_entry_index = 0
        self.testSuiteSaved = True
        self._popup = None

    def run_test_case(self):
        pass

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

        content = LoadDialog(load=self.load, cancel=self.cancel, fileFilter=['*.ts'])
        self._popup = Popup(title="Load test suite", content=content,
                            size_hint=(0.8, 0.8))
        self._popup.open()
    
    def load(self, path, filename):
        content = ""
        if not filename:
            return

        with open( os.path.join(path, filename[0]), "r" ) as stream:
            content = stream.read()

        #clearing existing test case
        self.clear()

        self.test_case_suite = TestSuite.loadFromJson(content)

        for step in reversed(self.test_case_suite.steps):
            self.add_stack_step_view(step)

        self.test_case_suite_name.text = filename[0][filename[0].rindex('\\')+1:]
        self.testSuiteSaved = True

        self._popup.dismiss()

    def save_test_suite_pressed(self, instance):
        print "saving test suite"
        content = SaveDialog(save=self.save, cancel=self.cancel, fileFilter = ['*.ts'])
        self._popup = Popup(title="Save test suite", content=content,
                            size_hint=(0.8, 0.8))
        self._popup.open()

    def save(self, path, filename):
        try: #remove all illegal characters.
            newFilename = Utils.get_valid_filename(filename[filename.rindex('\\')+1:])
        except: #rindex will throw an exception if the string searched was not found.
            newFilename = Utils.get_valid_filename(filename)

        #if the user tries to save the file with no name, or the name of just the extension, we return. (no saving)
        if len(newFilename) == 0 or newFilename==".ts": 
            return

        suiteName = newFilename
        if len(newFilename) >= 3:
            if newFilename[len(newFilename)-3:] != ".ts":
                newFilename += ".ts"
        else:
            newFilename += ".ts"
        with open( os.path.join(path, newFilename), "w" ) as stream:
            stream.write( self.test_case_suite.toJson(suiteName) )
        self._popup.dismiss()
        self.testSuiteSaved = True

        self.test_case_suite_name.text = newFilename[:len(newFilename)-3]

    def add_test_suite_step(self):
        print "adding test suite step"
        step = TestSuiteStep()

        self.test_case_suite.addStep(step, self.selected_test_suite_entry_index)
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
        elif index >= len(self.test_case_suite_stack.children):
            index = len(self.test_case_suite_stack.children)-1

        self.test_case_suite_stack.add_widget(tce, index)

        tce.load_from_step()
        tce.target_input.focus = True#.move_cursor()

    def set_current_step_index(self, step):
        index = self.test_case_suite.steps.index(step)
        self.selected_test_suite_entry_index = index

    def clear(self):
        print('clearing test case suite')
        nodes = []
        for node in self.test_case_suite_stack.children:
            nodes.append( node )
        for node in nodes:
            self.test_case_suite_stack.remove_widget( node )
            self.test_case_suite.steps.remove(node.step)
        self.testSuiteSaved = True
        self.test_case_suite_name.text = "Current Test Case Suite"

    def add_stack_step_view(self, step, index=None):
        tce = TestSuiteEntry.load()
        tce.step = step
        tce.parent_testsuite_view = self
        if index is None:
            index = 0
        elif index < 0:
            index = 0
        elif index >= len(self.test_case_suite_stack.children):
            index = len(self.test_case_suite_stack.children)-1

        self.test_case_suite_stack.add_widget(tce, index)

        tce.load_from_step()
        tce.target_input.focus = True#.move_cursor()

    def moveUp_test_entry(self, step):
        index = self.test_case_suite.steps.index(step)
        if index < len(self.test_case_suite.steps)-1:
            self.switch_test_entries(index, index+1)
        else:
            self.switch_test_entries(index, 0)
        self.testSuiteSaved = False

    def moveDown_test_entry(self, step):
        index = self.test_case_suite.steps.index(step)
        if index > 0:
            self.switch_test_entries(index, index-1)
        else:
            self.switch_test_entries(index, len(self.test_case_suite.steps)-1)
        self.testSuiteSaved = False

    def switch_test_entries(self, index_1, index_2):
        val1 = self.test_case_suite.steps[index_1]
        val2 = self.test_case_suite.steps[index_2]

        prevNode = self.test_case_suite_stack.children[index_1]
        prevNode.step = val1
        currentNode = self.test_case_suite_stack.children[index_2]
        currentNode.step = val2

        node_input = prevNode.target_input.text
        prevNode.target_input.text = currentNode.target_input.text
        currentNode.target_input.text = node_input

    def run_test_suite(self, instance):
        pass
