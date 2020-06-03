from framework import TestFramework, test_case_web
from lib_actions import Actions
from lib_pages import *
from time import sleep


class Tests(TestFramework):
    @staticmethod
    @test_case_web
    def event_run_button(driver):
        act = Actions(driver)
        act.login_admin()

        # p_header = PageHeader(driver)
        # p_missions = p_header.click_missions()
        p_mission = PageHeader(driver).click_missions().get_mission_by_name("SOC - 1")
        data = p_mission.get_mission_data()
        print(data)
        p_event_edit = p_mission.click_new_event()
        p_event_edit.set_name("Test1")
        p_event_edit.set_organization("134 test")
        p_event_edit.set_date(2021, 7, 12)
        p_event_edit.set_time("12:34")

        sleep(10)

        # p_events = PageEvents(driver)
        # p_event = p_events.get_event_by_name("1111")
        # data = p_event.get_event_data()
        # print(data)

        # page.click_forgot_pass()
        # page.enter_email("pupkin@email.ru")
        # page.click_send_email()

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