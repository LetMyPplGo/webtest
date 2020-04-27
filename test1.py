from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from testrail import *
import time


class TestFactory:

    @staticmethod
    def test_ma_values():
        driver = webdriver.Opera()
        driver.get("http://python.org")
        if "Python" not in driver.title: return R_FAIL, "python is not in the title"
        elem = driver.find_element_by_name("q")
        elem.clear()
        elem.send_keys("pycon" + Keys.RETURN)
        if "No results found." not in driver.page_source: return R_FAIL, "no results found"
        driver.close()
        return R_PASS, ""


def test_run(run_id):
    """iterates the given tesrail test run and executes each test"""
    tests = client.send_get('get_tests/' + run_id)
    for test in tests:
        test_id = test['id']
        test_name = test['custom_autotest_name']
        if test_name is not None:
            print("Test name: {}, autotest: {}".format(test['title'], test_name))
            assert hasattr(TestFactory, test_name)
            time1 = time.time()
            result, comment = TestFactory.test_ma_values()
            # result, comment = getattr(TestFactory, test_name)
            elapsed = str(round(time.time() - time1)) + "s"
            print("Result: {}, {}, spent {}".format(results[result], comment, elapsed))
            client.send_post('add_result/{}'.format(test_id), {'status_id': result, 'comment': comment, 'elapsed': elapsed})



client = APIClient('https://denwer.testrail.io')
client.user = 'eyewall@mail.ru'
client.password = 'testrail'

R_PASS = 1
R_BLOCK = 2
R_UNTESTED = 3
R_RETEST = 4
R_FAIL = 5
results = {R_PASS: "pass", R_BLOCK: "block", R_UNTESTED: "untested", R_RETEST: "retest", R_FAIL: "fail"}

# items = client.send_get('get_runs/1')
# for item in items:
#     print("{}: {}".format(item['id'], item['name']))

test_run("1")