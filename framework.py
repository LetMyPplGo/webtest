# TODO:
#   1. Create full cycle from starting tests in Testrail to adding results back to Testrail
#   2. Run tests in parallel (all kind of tests, not only web UI)
#   3. Kubernetes
#   4. What if some tests will need Virtual Machines? Will devops manage VMs? Tests will use their API
#   5. Think of non-destructive tests, so that they can execute in one Docker container

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
import inspect
from traceback import format_tb
import multiprocessing
import sys
from lib_testlink import *
import lib_pages


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
            driver = webdriver.Remote(command_executor="http://localhost:4444/wd/hub",
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


class TestFactory:
    @classmethod
    def run(cls, func, capabilities, test_case, test_plan):
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
        submit_result(test_case, test_plan, G_BUILD, result, elapsed, comment, None)
        return result, comment, elapsed


class Test_UI(TestFactory):
    @staticmethod
    @test_case_web
    def event_run_button(driver):
        page = lib_pages.PageLogin(driver)
        page.open_main()
        page.enter_name("admin@example.com")
        page.enter_pass("1qaz@WSX")
        # page.click_enter()

        page.click_forgot_pass()
        page.enter_email("pupkin@email.ru")
        page.click_send_email()

        # wait = WebDriverWait(driver, 10)
        #
        # driver.get("http://demo1.cyber.rt-solar.ru")
        # # assert "КИБЕРПОЛИГОН" in driver.title, "КИБЕРПОЛИГОН is not in the title"
        #
        # elem = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']")))
        # # elem = driver.find_element_by_xpath("//input[@type='text']")
        # elem.clear()
        # elem.send_keys("admin@example.com")
        #
        # elem = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
        #
        # # elem = driver.find_element_by_xpath("//input[@type='password']")
        # elem.clear()
        # elem.send_keys("1qaz@WSX" + Keys.RETURN)

        # elem = wait.until(EC.presence_of_element_located((By.XPATH, "// span[contains(., 'Административная панель')]")))
        # # elem = driver.find_element_by_xpath("// span[contains(., 'Административная панель')]")
        # elem.click()
        #
        # they_exist = driver.find_elements(By.XPATH, "//div[@class='v-toolbar__title'][contains(.,'АДМИНИСТРАТИВНАЯ ПАНЕЛЬ')]")
        # assert len(they_exist) != 0, "Did not Log in ;("

        driver.close()


def get_build(capabilities, test_plan):
    # driver = webdriver.Remote(command_executor="http://localhost:4444/wd/hub",
    #                           desired_capabilities=capabilities)
    # driver.get("http://demo1.cyber.rt-solar.ru")
    # wait = WebDriverWait(driver, 10)
    # elem = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']")))
    # now get the build from the webUI, let's say it is '0.1.34'
    app_build = '0.1.34'

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


# ------------------------------------------------------------- Constants

R_PASS = 'p'
R_BLOCK = 'b'
R_FAIL = 'f'
results = {R_PASS: "pass", R_BLOCK: "block", R_FAIL: "fail"}

CAP_CHROME = default_capabilities("chrome")
CAP_OPERA = default_capabilities("opera")
CAP_FIREFOX = default_capabilities("firefox")
CAP_FIREFOX["version"] = "75.0"

# ------------------------------------------------------------- MAIN
"""
Plan:
    . Script is started with Test Plan ID as argument
    . Get the list of Tests attached to the Test Plan
    . For each Test:
        . get list of Browsers or Capabilities to run
        . get name of the script 
        . run the script with arguments: Capabilities, Test ID
        . When the test ends it writes the results into the Test in Testlink
"""

# print(tls.whatArgs('createBuild'))
# exit(1)

test_plan = 257

# get the build for this run
G_BUILD = get_build(CAP_CHROME, test_plan)

for test_id, script in iterate_scripts_for_test_plan(test_plan):
    TestFactory.run(script, CAP_OPERA, test_id, test_plan)
    # print(f"Test {test_id}, script {script}")

# event_run_button

# test_name = "test_ma_values"
# TestFactory.run (test_name, CAP_CHROME, 1, 257)
# TestFactory.run (test_name, CAP_OPERA, 1, 257)



