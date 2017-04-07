from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.filechooser import FileChooserController

from tech.ironsheep.webdriver.command import Command

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    filechooser = ObjectProperty(None)    

    def __init__(self, **kwargs):
        super(LoadDialog, self).__init__(**kwargs)
        
        if "fileFilter" in kwargs:
            self.ChangeFileFilter(kwargs['fileFilter'])
        if "pathToLoad" in kwargs:
            self.PathToLoad(kwargs['pathToLoad'])
        else:
            self.PathToLoad(Command.appDir)

    def PathToLoad(self, path):
        self.filechooser.path = path
    
    def ChangeFileFilter(self, val):
        self.filechooser.filters = val
        
class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    filechooser = ObjectProperty(None)    

    def __init__(self, **kwargs):
        super(SaveDialog, self).__init__(**kwargs)        
        if "fileFilter" in kwargs:
            self.ChangeFileFilter(kwargs['fileFilter'])
        if "pathToLoad" in kwargs:
            self.PathToLoad(kwargs['pathToLoad'])
        else:
            self.PathToLoad(Command.appDir)

    def PathToLoad(self, path):
        self.filechooser.path = path

    def ChangeFileFilter(self, val):
        self.filechooser.filters = val