from kivy.uix.stacklayout import StackLayout
from kivy.lang import Builder
from kivy.properties import ObjectProperty

class ConnectEntry(StackLayout):
    target_ip = ObjectProperty(None)
    target_port = ObjectProperty(None)
    target_name = ObjectProperty(None)
    target_device_id = ObjectProperty(None)
    connect_button = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ConnectEntry, self).__init__(**kwargs)

    @staticmethod
    def load():
        return Builder.load_file("connect_entry.kv")

    def connect_to_server_callback(self, instance):
        print "try to connect to a certain server ip: " + self.target_ip.text + " and port: " + self.target_port.text + " with name: " + self.target_name.text + " and ID: " + self.target_device_id.text
        self.screen.connect_to_server(None, self.target_ip.text)