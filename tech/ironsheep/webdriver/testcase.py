import json
import threading
from command import Command

class TestCaseStep:
    def __init__(self):
        self.command = ""
        self.target = ""
        self.arg = ""

    def toJson(self):
        return json.dumps( self.flatten()  )

    def flatten(self):
        return {"command":self.command, "target":self.target, "arg":self.arg}

    @staticmethod
    def loadFromFlattent(flatten):
        ret = TestCaseStep()
        ret.command = flatten["command"]
        ret.target = flatten["target"]
        ret.arg = flatten["arg"]

        return ret

class TestCase:
    def __init__(self):
        self.steps = []
        self.running_thread = None
        self.test_case_callback = None
    
    def addStep(self, step, index):
        self.steps.insert(index, step)

    def flatten(self, filename):
        ret = {}
        ret["name"] = filename
        ret["steps"] = [ step.flatten() for step in reversed(self.steps) if step.command != "" ]
        
        return ret

    def toJson(self, filename):
        return json.dumps( self.flatten(filename) )

    def _run_blocking(self):

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

                return (False, step)
            else:
                if self.test_case_callback != None:
                    self.test_case_callback(True, step) # do focus?

        if self.test_case_callback != None:
            self.test_case_callback(True, None)

        self.running_thread = None
        self.test_case_callback = None
        return (True, None)

    def run(self, callback=None):
        if callback is None:
            print 'running test case on main thread'
            return self._run_blocking()
        else:
            if self.running_thread != None:
                return

            print 'running test case on background thread'
            self.running_thread = threading.Thread(name="Thread-test case", target=self._run_blocking)
            self.test_case_callback = callback
            self.running_thread.start()

    @staticmethod
    def loadFromJson(json_string):
        dec = json.loads( json_string )
        ret = TestCase()
        
        for step in dec["steps"]:
            st = TestCaseStep.loadFromFlattent( step )
            ret.addStep( st, 0 )

        return ret
