import unittest
import json

from tech.ironsheep.webdriver.testcase import *

class TestTestCaseStep(unittest.TestCase):
    
    def test_flatten(self):
        step = TestCaseStep()
        step.command = 3
        step.arg = "args"
        step.target = "//uibutton"

        flatten = step.flatten()
        self.assertEqual( flatten["command"], 3 )
        self.assertEqual( flatten["arg"], "args" )
        self.assertEqual( flatten["target"], "//uibutton" )
    
    def test_tojson(self):
        step = TestCaseStep()
        step.command = 3
        step.arg = "args"
        step.target = "//uibutton"

        to_json = step.toJson()
        back = json.loads( to_json )
        self.assertEqual( back["command"], 3 )
        self.assertEqual( back["arg"], "args" )
        self.assertEqual( back["target"], "//uibutton" )


class TestTestCase(unittest.TestCase):
   
    def setUp(self):
        self.tc = TestCase()
        step1 = TestCaseStep()
        step1.command = 5
        step1.target = "//uibutton"
        self.tc.addStep( step1 )

    def test_create(self):
        self.assertNotEqual( self.tc, None)

    def test_add_flatten(self):
        self.assertEqual( self.tc.flatten()["name"], "Test case name" )
        self.assertEqual( len(self.tc.flatten()["step"]), 1 )
        self.assertEqual( self.tc.flatten()["step"][0]["command"], 5 )

    def test_json(self):
        to_json = self.tc.toJson()
        back = json.loads( to_json )
        self.assertEqual( back["name"], "Test case name" )
        self.assertEqual( len( back["step"] ), 1 )
        self.assertEqual( back["step"][0]["command"], 5 )

if __name__=="__main__":
    unittest.main()
