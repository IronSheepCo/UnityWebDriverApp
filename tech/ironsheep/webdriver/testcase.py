import json

class TestCaseStep:
    def __init__(self):
        self.command = ""
        self.target = ""
        self.arg = ""

    def toJson(self):
        return json.dumps( self.flatten()  )

    def flatten(self):
        return {"command":self.command, "target":self.target, "arg":self.arg}

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

