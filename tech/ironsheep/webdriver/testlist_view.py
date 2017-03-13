from kivy.uix.stacklayout import StackLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
import json
import os

from tech.ironsheep.webdriver.testlist_entry import TestListEntry
from tech.ironsheep.webdriver.testlist import TestList, TestListStep
from tech.ironsheep.webdriver.utils import Utils
from tech.ironsheep.webdriver.dialog import LoadDialog, SaveDialog
from tech.ironsheep.webdriver.confirmPopup import ConfirmPopup

class TestListView(StackLayout):
    test_case_list_name = ObjectProperty(None)
    test_case_list_stack = ObjectProperty(None)

    test_case_list = TestList()

    def __init__(self, **kwargs):
        super(TestListView, self).__init__(**kwargs)
        self.selected_test_list_entry_index = 0
        self.testListSaved = True
        self._popup = None
    
    def run_test_case(self):
        pass

    def load_test_list_pressed(self):
        pass

    def cancel(self):
        self._popup.dismiss()

    def save_test_list_pressed(self, instance):
        print "saving test list"
        content = SaveDialog(save=self.save, cancel=self.cancel)
        self._popup = Popup(title="Save test list", content=content,
                            size_hint=(0.8, 0.8))
        self._popup.open()
    
    def save(self, path, filename):
        newFilename = Utils.get_valid_filename(filename)
        listName = newFilename
        if len(newFilename) >= 3:
            if newFilename[len(newFilename)-3:] != ".ts":
                newFilename += ".ts"
        else:
            newFilename += ".ts"
        with open( os.path.join(path, newFilename), "w" ) as stream:
            stream.write( self.test_case_list.toJson(listName) )
        self._popup.dismiss()
        self.testCaseSaved = True

    def add_test_case_step(self, instance):
        print "adding test case step"
        step = TestListStep()

        self.test_case_list.addStep(step, self.selected_test_list_entry_index)
        self.add_test_case_view(step, self.selected_test_list_entry_index)

        self.testListSaved = False

    def add_test_case_view(self, step, index=None):
        tce = TestListEntry.load()
        tce.step = step
        tce.parent_testlist_view = self
        if index is None:
            index = 0
        elif index < 0:
            index = 0
        elif index >= len(self.test_case_list_stack.children):
            index = len(self.test_case_list_stack.children)-1

        self.test_case_list_stack.add_widget(tce, index)

        tce.load_from_step()
        tce.target_input.focus = True#.move_cursor()

    def set_current_step_index(self, step):
        index = self.test_case_list.steps.index(step)
        self.selected_test_list_entry_index = index

    def clear(self):
        print('clearing test case list')
        nodes = []
        for node in self.test_case_list_stack.children:
            nodes.append( node )
        for node in nodes:
            self.test_case_list_stack.remove_widget( node )
            self.test_case_list.steps.remove(node.step)
        self.testListSaved = True
        self.test_case_list_name.text = "Current Test Case List"

    def moveUp_test_entry(self, step):
        index = self.test_case_list.steps.index(step)
        if index < len(self.test_case_list.steps)-1:
            self.switch_test_entries(index, index+1)
        else:
            self.switch_test_entries(index, 0)
        self.testListSaved = False

    def moveDown_test_entry(self, step):
        index = self.test_case_list.steps.index(step)
        if index > 0:
            self.switch_test_entries(index, index-1)
        else:
            self.switch_test_entries(index, len(self.test_case_list.steps)-1)
        self.testListSaved = False

    def switch_test_entries(self, index_1, index_2):
        val1 = self.test_case_list.steps[index_1]
        val2 = self.test_case_list.steps[index_2]

        prevNode = self.test_case_list_stack.children[index_1]
        prevNode.step = val1
        currentNode = self.test_case_list_stack.children[index_2]
        currentNode.step = val2

        node_input = prevNode.target_input.text
        prevNode.target_input.text = currentNode.target_input.text
        currentNode.target_input.text = node_input