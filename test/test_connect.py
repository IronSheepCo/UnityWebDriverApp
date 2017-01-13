import unittest
import json

from tech.ironsheep.webdriver.command import *

import requests

class TestConnect(unittest.TestCase):

    def setUp(self):
        Config.server_ip = "127.0.0.1"

    def test_connect(self):
        response = requests.get( Config.endpoint("status") )
        self.assertEqual( response.json()["ready"], True )

    def tearDown(self):
       requests.delete( Config.endpoint("session") ) 
