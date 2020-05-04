# TODO:
#   1. Create full cycle from starting tests in Testrail to adding results back to Testrail
#   2. Run tests in parallel (all kind of tests, not only web UI)
#   3. Kubernetes
#   4. What if some tests will need Virtual Machines? Will devops manage VMs? Tests will use their API
#   5. Think of non-destructive tests, so that they can execute in one Docker container

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from testrail import *
import time
import inspect
from traceback import format_tb
import multiprocessing
import sys


class Function:
    def __init__(self, func, driver):
        self.func = func
        self.driver = driver


class ProcessFactory:
    max_processes = 2
    # max_processes = multiprocessing.cpu_count() - 1
    active_processes = []
    queue = []

    @classmethod
    def run(cls, func, driver):
        print("RUN")
        if len(cls.active_processes) <= cls.max_processes:
            cls.active_processes.append(multiprocessing.Process(target=func, args=(driver,)))
            cls.active_processes[-1].start()
            print(f"Process {func.__name__} is started")
        else:
            cls.queue.append(Function(func, *args, **kwargs))
            print(f"Process {func.__name__} is added to queue")

    @classmethod
    def finished(cls):
        print("FINISH")
        if len(cls.queue) > 0:
            Func = cls.queue.pop(0)
            cls.active_processes.append(multiprocessing.Process(target=Func.func, args=(Func.driver,)))
            cls.active_processes[-1].start()
            print(f"Process {Func.func.__name__} is taken from queue and started")


def test_case_web(func):
    def wrapper(capabilities):
        try:
            capabilities["name"] = func.__name__

            if capabilities["enableVideo"]:
                video_name = func.__name__ + "." + capabilities["browserName"] + "." + time.strftime("%Y%m%d-%H%M%S") + ".mp4"
                capabilities["videoName"] = video_name

            if capabilities["enableLog"]:
                log_name = func.__name__ + "." + capabilities["browserName"] + "." + time.strftime("%Y%m%d-%H%M%S") + ".log"
                capabilities["logName"] = log_name

            # Selenoid should be started in advance with:
            # > cm.exe selenoid start --vnc
            driver = webdriver.Remote(command_executor="http://localhost:4444/wd/hub",
                                      desired_capabilities=capabilities)

            # func(driver, *args, **kwargs)
            # ProcessFactory.run(lambda: func(driver, *args, **kwargs))
            ProcessFactory.run(func, driver)
            ProcessFactory.finished()
        except AssertionError as err:
            # TODO: if function creates an archive to attach to fail collect it here and return as third parameter
            #       the archive can be named by the function name func.__name__
            if str(err) != "":
                return R_FAIL, f"{err}"
            else:
                lines = format_tb(err.__traceback__)
                return R_FAIL, lines[-1].split("\n")[1]
        else:
            # TODO: handle all other possible errors and return PASS only if no errors
            return R_PASS, ""
    return wrapper


class TestFactory:

    @staticmethod
    @test_case_web
    def test_ma_values(driver):
        driver.get("http://python.org")
        assert "Python" in driver.title, "python is not in the title"
        elem = driver.find_element_by_name("q")
        elem.clear()
        elem.send_keys("pycon" + Keys.RETURN)
        assert "No results found." in driver.page_source
        driver.close()


def test_run(run_id):
    """iterates the given Test Run and executes each test"""
    tests = testrail_client.send_get('get_tests/' + run_id)
    for test in tests:
        test_id = test['id']
        test_name = test['custom_autotest_name']
        if test_name is not None:
            print(f"Test name: {test['title']}, autotest: {test_name}")
            assert hasattr(TestFactory, test_name)
            time1 = time.time()
            # result, comment = TestFactory.test_ma_values()
            result, comment = getattr(TestFactory, test_name)()
            elapsed = str(round(time.time() - time1)) + "s"
            print(f"Result: {results[result]}, {comment}, spent {elapsed}")
            testrail_client.send_post(f'add_result/{test_id}',
                                      {'status_id': result, 'comment': comment, 'elapsed': elapsed}
                                      )


def get_test_runs():
    items = testrail_client.send_get('get_runs/1')
    for item in items:
        print("{}: {}".format(item['id'], item['name']))


def default_capabilities(browser):
    return {"browserName": browser,
            "enableVNC": True,
            "enableVideo": False,
            "enableLog": False
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
result, comment = TestFactory.test_ma_values(CAP_CHROME)
elapsed = str(round(time.time() - time1)) + "s"
print("Result: {}, {}, spent {}".format(results[result], comment, elapsed))

time1 = time.time()
result, comment = TestFactory.test_ma_values(CAP_OPERA)
elapsed = str(round(time.time() - time1)) + "s"
print("Result: {}, {}, spent {}".format(results[result], comment, elapsed))


#
# time1 = time.time()
# result, comment = TestFactory.test_ma_values(CAP_FIREFOX)
# elapsed = str(round(time.time() - time1)) + "s"
# print("Result: {}, {}, spent {}".format(results[result], comment, elapsed))

