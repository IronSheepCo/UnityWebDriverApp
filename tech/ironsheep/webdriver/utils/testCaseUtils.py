from tech.ironsheep.webdriver.testcase import TestCase, TestCaseStep

class TestCaseUtils():

    @staticmethod
    def DoRunTestCase(filePath):
        content = ""
        test_case = TestCase()
        with open(filePath, "r") as stream:
            content = stream.read()

        test_case = TestCase.loadFromJson(content)
        #print "test case step counter:", len(test_case.steps)

        try:
            result, step = test_case.run()
            return TestCaseUtils._test_case_run_step_result(result, step, test_case)
        except Exception:
            return False

    @staticmethod
    def _test_case_run_step_result(status, info, test_case):
        if status is False:
            stack_len = len(test_case.steps)
            alert_text = "Test case failed at [b]step %i[/b] \n Step target: [b]%s[/b]"%(stack_len-info.no, info.target)
            print alert_text
            return False
        else:
            if info is None:
                alert_text = "Success"
                print alert_text
                return True
            else:
                print info
                return True
                #test_case.steps[info.no]