# TODO:
#   1. Create full cycle from starting tests in Testlink to adding results back to Testlink
#   2. Run tests in parallel (all kind of tests, not only web UI)
#   3. Kubernetes (?)
#   4. What if some tests will need Virtual Machines? Will devops manage VMs? Tests will use their API
#   5. Think of non-destructive tests, so that they can execute one after another in one Docker container

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
from traceback import format_tb
import multiprocessing
from lib_testlink import *
import json
import requests

# ------------------------------------------------------------- Constants

BASE_URL = "http://demo1.cyber.rt-solar.ru"

R_PASS = 'p'
R_BLOCK = 'b'
R_FAIL = 'f'
results = {R_PASS: "pass", R_BLOCK: "block", R_FAIL: "fail"}

SELENOID_URL = "http://localhost:4444/wd/hub"

USE_LOCAL_FOX = True

# ------------------------------------------------------------- Classes


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
            cls.queue.append(Function(func, driver))
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
            if USE_LOCAL_FOX:
                driver = webdriver.Firefox()
            else:
                driver = webdriver.Remote(command_executor=SELENOID_URL,
                                          desired_capabilities=capabilities)

            func(driver)
            # ProcessFactory.run(lambda: func(driver, *args, **kwargs))
            # ProcessFactory.run(func, driver)
            # ProcessFactory.finished()
        except AssertionError as err:
            # TODO: if function creates an archive to attach to fail, collect it here and return as third parameter
            #       the archive can be named by the function name func.__name__
            # if assert has the message return it as comment, otherwise use the assert body
            if str(err) != "":
                return R_FAIL, f"{err}"
            else:
                lines = format_tb(err.__traceback__)
                return R_FAIL, lines[-1].split("\n")[1]
        else:
            # TODO: handle all other possible errors and return PASS only if no errors
            return R_PASS, ""
    return wrapper


class TestFramework:
    @classmethod
    def run(cls, func, capabilities, test_case, test_plan, build):
        # look for the function in the inherited classes
        child = None
        for item in cls.__subclasses__():
            if hasattr(item, func):
                child = item
                break
        assert child is not None, f"The function {func} is not implemented"
        print(f"For {test_case} running {func}() from {child.__name__}")
        time1 = time.time()
        result, comment = getattr(child, func)(capabilities)
        elapsed = str(round(time.time() - time1))
        print("Test {} on {}, {}, spent {}s. {}".format(test_case, capabilities["browserName"], results[result], elapsed, comment))
        submit_result(test_case, test_plan, build, result, elapsed, comment, None)
        return result, comment, elapsed


def get_build(test_plan):
    r = requests.get(f"{BASE_URL}/api/version")
    app_build = json.loads(r.content)["version"]

    # now check if such build exists
    for build in tls.getBuildsForTestPlan(test_plan):
        if app_build == build['name']:
            return build['id']

    # if not - add new
    return tls.createBuild(test_plan, app_build, "Created by autotest")


def default_capabilities(browser):
    return {"browserName": browser,
            "enableVNC": True,
            "enableVideo": False,
            "enableLog": False
            }





