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
