from framework import TestFramework, test_case_web
from lib_actions import *
from lib_pages import *
from time import sleep
import globals


class Tests(TestFramework):
    @staticmethod
    @test_case_web
    def always_fail(driver, context):
        assert False, 'The test failed because it always fails'

    @staticmethod
    @test_case_web
    def test_test(driver, context):
        act = Actions(driver)
        act.login_admin()

        PageMainHeader(driver).click_administration()
        PageAdminHeader(driver).click_infrastructure()
        sleep(2)
        PageAdminHeader(driver).click_organizations()
        sleep(2)
        PageAdminHeader(driver).click_users()
        sleep(2)


    @staticmethod
    @test_case_web
    def create_org_by_admin(driver, context):
        act = Actions(driver)
        act.login_admin()

        org = Organization(driver)
        org.fill_random()
        org.create()
        context['organization'] = org.name
        # DBG
        sleep(10)
        context['organization'] = 'Тестовая организация 3'

    @staticmethod
    @test_case_web
    def create_tutor_by_admin(driver, context):
        act = Actions(driver)
        act.login_admin()
        
        tutor = User(driver)
        tutor.fill_random()
        tutor.role = globals.ROLE_TUTOR

        if "organization" in context:
            tutor.organization = context['organization']
        else:
            org = Organization(driver)
            org.fill_random()
            org.create()
            tutor.organization = org.name
            context['organization'] = org.name
        # tutor.photo = ""
        tutor.create()

        # TODO: Receive email, get pass link, open it, set pass
        tutor.email = 'lector@example.com'
        tutor.password = '1qaz@WSX'
        context['organization'] = 'Тестовая организация 3'

        context['tutor'] = tutor

        
    @staticmethod
    @test_case_web
    def create_users_by_lector(driver, context):
        act = Actions(driver)
        assert 'tutor' in context
        assert "organization" in context
        tutor = context['tutor']
        act.login(tutor.email, tutor.password)

        student = User(driver)
        student.fill_random()
        student.role = globals.ROLE_STUDENT
        student.organization = context['organization']
        student.create()

        observer = User(driver)
        observer.fill_random()
        observer.role = globals.ROLE_OBSERVER
        observer.organization = context['organization']
        observer.create()


    @staticmethod
    @test_case_web
    def event_run_button(driver, context):
        act = Actions(driver)
        act.login_admin()

        # p_header = PageHeader(driver)
        # p_missions = p_header.click_missions()
        p_mission = PageMainHeader(driver).click_missions().get_mission_by_name("SOC - 1")
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