from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty

from tech.ironsheep.webdriver.command import Config

class TestListScreen(Screen):
    title_label = ObjectProperty(None)
    back_button = ObjectProperty(None)
    test_case_list_view = ObjectProperty(None)
    test_case_list_stack = ObjectProperty(None)

    def on_enter(self):
        self.title_label.text = "connected to "+Config.server_ip
        self.test_case_list_stack.bind(minimum_height=self.test_case_list_stack.setter('height') )
        self.test_case_list_view.my_screen = self

    def Back(self):
        self.test_case_list_view.show_test_case()
