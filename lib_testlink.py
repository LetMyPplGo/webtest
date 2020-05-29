import testlink

SERVER_URL = "http://tl.cyber.rt-solar.ru/lib/api/xmlrpc/v1/xmlrpc.php"
DEVKEY = "3b4b411e146366a7d233408c6dfd8fe6"
PROJECT_NAME = "CyberPolygon"
DO_NOT_SUBMIT_RESULTS = True


tls = testlink.TestlinkAPIClient(SERVER_URL, DEVKEY)

# print(tls.about())

# tc_info = tls.getTestCase(None, testcaseexternalid='CP-3')
# print(tc_info)
# tls.copyTCnewTestCase(tc_info[0]['testcase_id'], testsuiteid=newSuiteID, testcasename='a new test case name')
# print(tls.whatArgs('reportTCResult'))


def submit_result(test_case, test_plan, build, result, elapsed, comment, attach=None):
    if DO_NOT_SUBMIT_RESULTS:
        print ("DO_NOT_SUBMIT_RESULTS is True, do not send results to Testlink")
        return

    result_id = tls.reportTCResult(None, test_plan, None, result, comment, buildid=build, testcaseexternalid=test_case, execduration=float(elapsed))
    if attach is not None:
        # attach a file to the result
        print(f"Add attach to result {result_id}")
    return 0


def iterate_scripts_for_test_plan(test_plan, only_with_script=True):
    """
    Here we iterate all testcases for given testplan and return testcase ID + script associated with the testcase
    :param test_plan: ID of the test plan
    :param only_with_script: return only testcases with filled script (custom field in the Testlink)
    :return: ID of the Test Case + Env
    """
    project_id = tls.getProjectIDByName(PROJECT_NAME)

    for test_case_id in tls.getTestCasesForTestPlan(test_plan):
        # print(test_case_id)
        test_case = tls.getTestCase(test_case_id)[0]
        ext_id = test_case['full_tc_external_id']
        version = test_case['version']
        script_name = tls.getTestCaseCustomFieldDesignValue(ext_id, int(version), project_id,  'script', 'value')
        if script_name != '' or not only_with_script:
            yield ext_id, script_name

