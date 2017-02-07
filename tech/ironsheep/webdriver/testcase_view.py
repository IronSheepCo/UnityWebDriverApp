from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
import json
import os

from tech.ironsheep.webdriver.testcase import TestCase, TestCaseStep
from tech.ironsheep.webdriver.testcase_entry import TestCaseEntry
from tech.ironsheep.webdriver.dialog import LoadDialog, SaveDialog

class TestCaseView(ScrollView):
    test_case_stack = ObjectProperty(None)
    test_case = TestCase()

    def __init__(self, **kwargs):
        super(TestCaseView, self).__init__(**kwargs)
        self.selected_test_entry_index = 0

    def cancel(self):
        self._popup.dismiss()

    def clear(self):
        print('clearing test case')
        nodes = []
        for node in self.test_case_stack.children:
            nodes.append( node )
        for node in nodes:
            self.test_case_stack.remove_widget( node )

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
            self.add_stack_step_view( step )

        self._popup.dismiss()
        
    def _test_case_run_step_result(self, status, info):
        if status == False:
            alert_text = "Test case failed at [b]step %i[/b] \n Step target: [b]%s[/b]"%(info.no, info.target)
            alert = Popup(title="Error running test case",
                          content=Label(text=alert_text,
                          halign="center",
                          markup=True),
                          size_hint=(0.75, 0.75)
                         )

            alert.open()
        else:
            if info is None:
                alert_text = "Success"
                alert = Popup(title="Test case result",
                              content=Label(text=alert_text,
                              halign="center",
                              markup=True),
                              size_hint=(0.4, 0.4)
                             )

                alert.open()
            else:
                stack_len = len(self.test_case_stack.children)
                node_to_select = self.test_case_stack.children[info.no]
                self.test_case_stack.children[info.no].on_focus(None, True)
                if info.no < stack_len-1:
                    self.test_case_stack.children[info.no+1].on_focus(None, False)
                
                #self.test_case_list.select_node( node_to_select )

                #scrolling to current tree view node
                #for an unkown reason the widgets in the treeview
                #need to be reversed to get the desired behaviour

                #total_nodes = len(self.test_case_stack.children)
                self.test_case_stack.parent.scroll_to( self.test_case_stack.children[ info.no ] )

    def run_test_case(self, instance):
        print( "running test case")
        self.test_case.run(self._test_case_run_step_result)

    def load_test_pressed(self, instance):
        print "loading test case"
        content = LoadDialog(load=self.load, cancel=self.cancel)
        self._popup = Popup(title="Load test case", content=content,
                            size_hint=(0.8, 0.8))
        self._popup.open()

    def save_test_pressed(self, instance):
        print "saving test case"
        content = SaveDialog(save=self.save, cancel=self.cancel)
        self._popup = Popup(title="Save test case", content=content,
                            size_hint=(0.8, 0.8))
        self._popup.open()

    def add_stack_step_view(self, step, index=None):
        tce = TestCaseEntry.load()
        tce.step = step
        tce.parent_testcase_view = self
        if index is None:
            index = 0
        elif index < 0:
            index = 0
        elif index >= len(self.test_case_stack.children):
            index = len(self.test_case_stack.children)-1

        self.test_case_stack.add_widget(tce, index)

        tce.load_from_step()
        tce.move_cursor()

    def add_step(self, instance):
        print "adding step"

        step = TestCaseStep()
        self.test_case.addStep(step, self.selected_test_entry_index)
        self.add_stack_step_view(step, self.selected_test_entry_index)

    def set_current_step_index(self, step):
        index = self.test_case.steps.index(step)
        self.selected_test_entry_index = index

    def moveUp_testcase_entry(self, step):
        index = self.test_case.steps.index(step)
        if index < len(self.test_case.steps)-1:
            self.switch_testcase_entries(index, index+1)
            pass
        else:
            self.switch_testcase_entries(index, 0)
            pass

    def moveDown_testcase_entry(self, step):
        index = self.test_case.steps.index(step)
        if index > 0:
            self.switch_testcase_entries(index, index-1)
            pass
        else:
            self.switch_testcase_entries(index, len(self.test_case.steps)-1)
            pass

    def switch_testcase_entries(self, index_1, index_2):
        val1 = self.test_case.steps[index_1]
        val2 = self.test_case.steps[index_2]

        prevNode = self.test_case_stack.children[index_1]
        prevNode.step = val1
        currentNode = self.test_case_stack.children[index_2]
        currentNode.step = val2

        node_command = prevNode.command_button.text
        node_input = prevNode.target_input.text
        node_arg_input = prevNode.arg_input.text

        prevNode.command_button.text = currentNode.command_button.text
        prevNode.target_input.text = currentNode.target_input.text
        prevNode.arg_input.text = currentNode.arg_input.text

        currentNode.command_button.text = node_command
        currentNode.target_input.text = node_input
        currentNode.arg_input.text = node_arg_input



