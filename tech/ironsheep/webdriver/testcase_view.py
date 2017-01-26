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
    test_case_list = ObjectProperty(None)
    test_case = TestCase()

    def __init__(self, **kwargs):
        super(TestCaseView, self).__init__(**kwargs)

    def cancel(self):
        self._popup.dismiss()

    def clear(self):
        print('clearing test case')
        nodes = []
        for node in self.test_case_list.iterate_all_nodes():
            nodes.append( node )
        for node in nodes:
            self.test_case_list.remove_node( node )

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
            self.add_step_view( step )

        self._popup.dismiss()
    
    def on_test_case_list(self, instance, value):
        self.test_case_list.bind(minimum_height=self.test_case_list.setter('height') )
    
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
                node_to_select = self.test_case_list.root.nodes[ info.no - 1 ]
                self.test_case_list.select_node( node_to_select )

    def run_test_case(self, instance):
        print( "running test case")
        self.test_case.run(self._test_case_run_step_result)

    def load_test_pressed(self, instance):
        print "loading test case"
        content = LoadDialog(load=self.load, cancel=self.cancel)
        self._popup = Popup(title="Save test case", content=content,
                            size_hint=(0.8, 0.8))
        self._popup.open()

    def save_test_pressed(self, instance):
        print "saving test case"
        content = SaveDialog(save=self.save, cancel=self.cancel)
        self._popup = Popup(title="Save test case", content=content,
                            size_hint=(0.8, 0.8))
        self._popup.open()

    def add_step_view(self, step):
        tce = TestCaseEntry.load()
        tce.step = step
        self.test_case_list.add_node(tce)
        tce.load_from_step()
        tce.move_cursor()

    def add_step(self, instance):
        print "adding step"
        step = TestCaseStep()
        self.test_case.addStep(step)
        self.add_step_view(step)
