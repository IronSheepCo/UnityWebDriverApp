from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty

from tech.ironsheep.webdriver.command import Config

class TestSuiteScreen(Screen):
    title_label = ObjectProperty(None)
    back_button = ObjectProperty(None)
    test_suite_view = ObjectProperty(None)
    test_suite_stack = ObjectProperty(None)

    def on_enter(self):
        self.title_label.text = "connected to "+Config.server_ip
        self.test_suite_stack.bind(minimum_height=self.test_suite_stack.setter('height') )
        self.test_suite_view.my_screen = self

    def Back(self):
        self.test_suite_view.show_test_case()
