from kivy.properties import StringProperty
from os.path import join, dirname
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout


class ConfirmPopup(FloatLayout):
    text = StringProperty('')
    ok_text = StringProperty('OK')
    cancel_text = StringProperty('Cancel')

    __events__ = ('on_ok', 'on_cancel')

    def __init__(self):
        super(ConfirmPopup, self).__init__()
        self.ok_callback = lambda : True
        self.cancel_callback = lambda : True

    def ok(self):
        self.dispatch('on_ok')

    def cancel(self):
        self.dispatch('on_cancel')

    def on_ok(self):
        if self.ok_callback != None:
            self.ok_callback()

    def on_cancel(self):
        if self.cancel_callback != None:
            self.cancel_callback()
