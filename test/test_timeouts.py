import unittest
import json

from tech.ironsheep.webdriver.command import *

import requests

class TestTimeouts(unittest.TestCase):

    def setUp(self):
        Config.server_ip = "127.0.0.1"
        response = requests.post( Config.endpoint("session") )
        Config.session_id = response.json()["sessionId"]

    def test_get_timeouts(self):
        response = requests.get( Config.endpoint_session("timeouts") )
        data = response.json()["data"]
        self.assertEqual( data["implicit"], 0 )
        self.assertEqual( data["page load"], 300000 )
        self.assertEqual( data["script"], 30000 )

    def tearDown(self):
       requests.delete( Config.endpoint_session("") ) 

class TestSetTimeouts(unittest.TestCase):

    def setUp(self):
        Config.server_ip = "127.0.0.1"
        response = requests.post( Config.endpoint("session") )
        Config.session_id = response.json()["sessionId"]

    def test_set_implicit_timeouts(self):
        Command.timeouts( implicit = 2500 )
        response = requests.get( Config.endpoint_session("timeouts") )
        data = response.json()["data"]
        self.assertEqual( data["implicit"], 2500 )

    def test_set_page_load_timeouts(self):
        Command.timeouts( page_load = 45500 )
        response = requests.get( Config.endpoint_session("timeouts") )
        data = response.json()["data"]
        self.assertEqual( data["page load"], 45500 )
    
    def test_set_script_timeouts(self):
        Command.timeouts( script = 222500 )
        response = requests.get( Config.endpoint_session("timeouts") )
        data = response.json()["data"]
        self.assertEqual( data["script"], 222500 )
    
    def test_set_multiple_timeouts(self):
        Command.timeouts( script = 500, implicit = 0 )
        response = requests.get( Config.endpoint_session("timeouts") )
        data = response.json()["data"]
        self.assertEqual( data["script"], 500 )
        self.assertEqual( data["implicit"], 0 )
    
    def tearDown(self):
       requests.delete( Config.endpoint_session("") ) 
