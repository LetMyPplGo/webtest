from framework import *
import tst_users

# ------------------------------------------------------------- CONSTANTS

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

# get the build for this run, create if it doesn't exist
G_BUILD = get_build(test_plan)
assert G_BUILD is not None

for test_id, script in iterate_scripts_for_test_plan(test_plan):
    TestFramework.run(script, CAP_OPERA, test_id, test_plan, G_BUILD)
    # print(f"Test {test_id}, script {script}")

# test_name = "test_ma_values"
# TestFactory.run (test_name, CAP_CHROME, 1, 257)
# TestFactory.run (test_name, CAP_OPERA, 1, 257)

