import os

from tech.ironsheep.webdriver.testsuite import TestSuite
from tech.ironsheep.webdriver.utils.utils import Utils

class TestSuiteUtils():

    @staticmethod
    def DoRunTestSuite(filePath):
        content = ""
        test_suite = TestSuite()

        with open(filePath, "r") as stream:
            content = stream.read()

        test_suite = TestSuite.loadFromJson(content)

        dir_path = os.path.dirname(filePath)
        file_name = Utils.get_filename_from_path(filePath)
        test_suite.test_suite_path, f = Utils.get_path_relative_to_app(dir_path, file_name)

        try:
            result, step = test_suite.run()
            return TestSuiteUtils._test_suite_run_step_result(result, step, test_suite)
        except Exception:
            return False

    @staticmethod
    def _test_suite_run_step_result(status, info, test_suite):
        if status is False:
            stack_len = len(test_suite.steps)
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
