import unittest
import json

from tech.ironsheep.webdriver.command import *

import requests

class TestWaitForElement(unittest.TestCase):

    def setUp(self):
        Config.server_ip = "127.0.0.1"
        response = requests.post( Config.endpoint("session") )
        Config.session_id = response.json()["sessionId"]

    def test_get_element_timeout(self):
        result = Command.wait_for_element("//uibutton", 10)
        self.assertTrue( result )

    def tearDown(self):
       requests.delete( Config.endpoint_session("") ) 
