from kivy.uix.stacklayout import StackLayout
from kivy.properties import ObjectProperty

from tech.ironsheep.webdriver.testlist_entry import TestListEntry
from tech.ironsheep.webdriver.testlist import TestList, TestListStep

class TestListView(StackLayout):
    test_case_list_name = ObjectProperty(None)
    test_case_list_stack = ObjectProperty(None)

    test_case_list = TestList()

    def __init__(self, **kwargs):
        super(TestListView, self).__init__(**kwargs)
        self.selected_test_list_entry_index = 0
        self.testListSaved = True
        self._popup = None

    def load_test_list_pressed(self):
        pass

    def save_test_list_pressed(self):
        pass

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

    def run_test_case(self):
        pass

    def clear(self):
        pass
