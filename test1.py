from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from testrail import *
import time
import inspect


def testcase(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AssertionError as err:
            # if function creates an archive to attach to fail collect it here and return as third parameter
            # the archive can be named by the function name func.__name__
            return R_FAIL, "{}".format(err)
    return wrapper


class TestFactory:

    @staticmethod
    @testcase
    def test_ma_values(capabilities):
        # run with selenium on locally installed browser
        # driver = webdriver.Opera()

        # this capcbility doesn't work for some reason...
        if capabilities["enableVideo"]:
            my_name = inspect.currentframe().f_code.co_name
            video_name = my_name + "." + capabilities["browserName"] + ".mp4"
            capabilities["videoName"] = video_name

        # run on selenoid with browsers running in Docker
        driver = webdriver.Remote(command_executor="http://localhost:4444/wd/hub",
                                  desired_capabilities=capabilities)

        # the test itself
        driver.get("http://python.org")
        assert "Python" in driver.title, "python is not in the title"
        elem = driver.find_element_by_name("q")
        elem.clear()
        elem.send_keys("pycon" + Keys.RETURN)
        assert "No results found." in driver.page_source, "Expected: 'No results found' on the page"
        driver.close()
        return R_PASS, ""


def test_run(run_id):
    """iterates the given testrail Test Run and executes each test"""
    tests = testrail_client.send_get('get_tests/' + run_id)
    for test in tests:
        test_id = test['id']
        test_name = test['custom_autotest_name']
        if test_name is not None:
            print("Test name: {}, autotest: {}".format(test['title'], test_name))
            assert hasattr(TestFactory, test_name)
            time1 = time.time()
            # result, comment = TestFactory.test_ma_values()
            result, comment = getattr(TestFactory, test_name)()
            elapsed = str(round(time.time() - time1)) + "s"
            print("Result: {}, {}, spent {}".format(results[result], comment, elapsed))
            testrail_client.send_post('add_result/{}'.format(test_id), {'status_id': result, 'comment': comment, 'elapsed': elapsed})


def get_test_runs():
    items = testrail_client.send_get('get_runs/1')
    for item in items:
        print("{}: {}".format(item['id'], item['name']))


def default_capabilities(browser):
    return {"browserName": browser,
            "enableVNC": True,
            "enableVideo": True
            }


# testrail_client = APIClient('https://denwer.testrail.io')
# testrail_client.user = 'eyewall@mail.ru'
# testrail_client.password = 'testrail'

R_PASS = 1
R_BLOCK = 2
R_UNTESTED = 3
R_RETEST = 4
R_FAIL = 5
results = {R_PASS: "pass", R_BLOCK: "block", R_UNTESTED: "untested", R_RETEST: "retest", R_FAIL: "fail"}

CAP_CHROME = default_capabilities("chrome")
CAP_OPERA = default_capabilities("opera")
CAP_FIREFOX = default_capabilities("firefox")
CAP_FIREFOX["version"] = "75.0"


# test_run("1")

time1 = time.time()
result, comment = TestFactory.test_ma_values(CAP_CHROME)
elapsed = str(round(time.time() - time1)) + "s"
print("Result: {}, {}, spent {}".format(results[result], comment, elapsed))

time1 = time.time()
result, comment = TestFactory.test_ma_values(CAP_OPERA)
elapsed = str(round(time.time() - time1)) + "s"
print("Result: {}, {}, spent {}".format(results[result], comment, elapsed))

time1 = time.time()
result, comment = TestFactory.test_ma_values(CAP_FIREFOX)
elapsed = str(round(time.time() - time1)) + "s"
print("Result: {}, {}, spent {}".format(results[result], comment, elapsed))


# driver = webdriver.Remote(command_executor="http://localhost:4444/wd/hub",
#                           desired_capabilities={
#                               "browserName": "chrome",
#                           })
# print(driver.capabilities)