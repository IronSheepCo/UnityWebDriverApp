import json
import threading
import os

from command import Command
from tech.ironsheep.webdriver.utils.utils import Utils
from tech.ironsheep.webdriver.utils.testCaseUtils import TestCaseUtils

class TestSuiteStep:
    def __init__(self):
        self.target = ""

    def toJson(self):
        return json.dumps( self.flatten()  )

    def flatten(self):
        return {"target":self.target}

    @staticmethod
    def loadFromFlattent(flatten):
        ret = TestSuiteStep()
        ret.target = flatten

        return ret

class TestSuite:
    def __init__(self):
        self.steps = []
        self.running_thread = None
        self.test_suite_callback = None
        self.test_suite_path = None
    
    def addStep(self, step, index):
        self.steps.insert(index, step)

    def flatten(self, suiteName):
        ret = {}
        ret["name"] = suiteName
        ret["test_cases"] = [step.target for step in reversed(self.steps)]

        return ret

    def toJson(self, suiteName):
        return json.dumps( self.flatten(suiteName) )

    def _run_blocking(self):
        step_no = len(self.steps)
        print 'starting running test suite blocking'
        for step in reversed(self.steps):
            step_no = step_no - 1
            step.no = step_no
            if self.test_suite_callback != None:
                self.test_suite_callback(True, step) # this will try to focus on the step item

            if self.test_suite_path is None:
                asb_file_path = Utils.get_absolute_path(step.target)
            else:
                new_file = os.path.join(self.test_suite_path, step.target)
                asb_file_path = Utils.get_absolute_path(new_file)


            file_path = Utils.check_file_on_disk(asb_file_path) # == FilePath to TestCases
            if not file_path:
                print "File Not Found!"
                self.running_thread = None

                if self.test_suite_callback != None:
                    self.test_suite_callback(False, step)

                self.test_suite_callback = None
                return (False, step)
            else:
                # run the test case
                if not TestCaseUtils.DoRunTestCase(file_path):
                    self.running_thread = None

                    if self.test_suite_callback != None:
                        self.test_suite_callback(False, step)

                    self.test_suite_callback = None
                    return (False, step)
                else:
                    if self.test_suite_callback != None:
                        self.test_suite_callback(True, step) # do focus

        if self.test_suite_callback != None:
            self.test_suite_callback(True, None)

        self.running_thread = None
        self.test_suite_callback = None
        return (True, None)

    def run(self, callback=None):
        if callback is None:
            print 'running test suite on main thread'
            return self._run_blocking()
        else:
            if self.running_thread != None:
                return

            print 'running test suite on background thread'
            self.running_thread = threading.Thread(name="Thread-test sutie", target=self._run_blocking)
            self.test_suite_callback = callback
            self.running_thread.start()

    @staticmethod
    def loadFromJson(json_string):
        dec = json.loads( json_string )
        ret = TestSuite()

        for step in dec["test_cases"]:
            st = TestSuiteStep.loadFromFlattent(step)
            ret.addStep(st, 0)

        return ret
