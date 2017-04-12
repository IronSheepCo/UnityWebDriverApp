class StartUpUtils():

    parameter_list = ["id", "path", "type"]

    @staticmethod
    def ParseParameters(arg_list):
        par_dict = {StartUpUtils.parameter_list[0]: None, StartUpUtils.parameter_list[1]: None, StartUpUtils.parameter_list[2]: "case"}
        error = False

        for i, par in enumerate(arg_list):
            key, value = StartUpUtils.GetParameterValue(par)

            if key is None or value is None:
                print "[", par, "] is not a Valid Parameter."
                error = True
            else:
                value = value.lower()
                if key in StartUpUtils.parameter_list:
                    if key == "type":
                        if value == "case" or value == "suite":
                            par_dict[key] = value
                        else:
                            print "[", key, "] must have a value from the following list: {case, suite}. Default value is case."
                            error = True
                    else:        
                        par_dict[key] = value
                else:
                    print "[", key, "] is not a Valid Key."
                    error = True
        if error:
            print "Run example:  IRONforge.exe id=25aea4ca221786e606d2e6eff49d0ca4 path=C:\testSuite.ts type=suite"

        return par_dict[StartUpUtils.parameter_list[0]], par_dict[StartUpUtils.parameter_list[1]], par_dict[StartUpUtils.parameter_list[2]]

    @staticmethod
    def GetParameterValue(item):
        index = item.find("=")
        if not index == -1:
            return item[:index], item[index+1:]
        else:
            return None, None
