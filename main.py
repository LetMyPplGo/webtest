from framework import *
import tst_users
from  lib_mail import iterate_emails

# ------------------------------------------------------------- CONSTANTS

# capabilities = {"chrome": default_capabilities("chrome")}
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

for email in iterate_emails():
    if email.email['id'] == 'bcXgJ0Te':
        print(email.links)

# print(tls.whatArgs('createBuild'))
exit(1)

test_plan = 740 #257

# get the build for this run, create if it doesn't exist
app_build = get_build(test_plan)
assert app_build is not None

for test_id, script in iterate_scripts_for_test_plan(test_plan):
    TestFramework.run(script, CAP_OPERA, test_id, test_plan, app_build)
    # TestFramework.run(script, default_capabilities(browser), test_id, test_plan, app_build)
    # print(f"Test {test_id}, script {script}")

# test_name = "test_ma_values"
# TestFactory.run (test_name, CAP_CHROME, 1, 257)
# TestFactory.run (test_name, CAP_OPERA, 1, 257)

