import json
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
    
    def addStep(self, step):
        self.steps.append( step )

    def flatten(self):
        ret = {}
        ret["name"] = "Test case name"
        ret["steps"] = [ step.flatten() for step in self.steps if step.command != "" ]
        
        return ret

    def toJson(self):
        return json.dumps( self.flatten() )

    def run(self):
        for step in self.steps:
            Command.run_command_no( step.target, step.command )        

    @staticmethod
    def loadFromJson(json_string):
        dec = json.loads( json_string )
        ret = TestCase()
        
        for step in dec["steps"]:
            st = TestCaseStep.loadFromFlattent( step )
            ret.addStep( st )

        return ret
