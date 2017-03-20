import json
import threading
from command import Command

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
        self.test_case_callback = None
    
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

        return 
        #TODO

        step_no = len(self.steps)
        print 'starting running test case blocking'
        for step in reversed(self.steps):
            step_no = step_no - 1

            step.no = step_no
            if self.test_case_callback != None:
                self.test_case_callback(True, step)

            result = Command.run_command_no(step.target, step.command, step.arg)
            if result is False:
                self.running_thread = None

                if self.test_case_callback != None:
                    self.test_case_callback(False, step)

                self.test_case_callback = None

                return False
            else:
                if self.test_case_callback != None:
                    self.test_case_callback(True, step)

        if self.test_case_callback != None:
            self.test_case_callback(True, None)

        self.running_thread = None
        self.test_case_callback = None
        return True

    def run(self, callback=None):
        return
        #TODO

        if callback is None:
            print 'running test case on main thread'
            return self._run_blocking()
        else:
            if self.running_thread != None:
                return 

            print('running test case on background thread')
            self.running_thread = threading.Thread(name="Thread-test case", target=self._run_blocking)
            self.test_case_callback = callback
            self.running_thread.start()

    @staticmethod
    def loadFromJson(json_string):
        dec = json.loads( json_string )
        ret = TestSuite()
        
        for step in dec["test_cases"]:
            st = TestSuiteStep.loadFromFlattent( step )
            ret.addStep( st, 0 )

        return ret
