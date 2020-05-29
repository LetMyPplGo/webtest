from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class Page:
    elements = {}

    def __init__(self, driver):
        self.driver = driver
        self.base_url = "http://demo1.cyber.rt-solar.ru"

    def find_element(self, element, time=10):
        assert element in self.elements, f"element {element} is not defined"
        locator = self.elements[element]
        return WebDriverWait(self.driver, time).until(EC.presence_of_element_located(locator),
                                                      message=f"Can't find element {element} by locator {locator}")

    def find_elements(self, element, time=10):
        assert element in self.elements, f"element {element} is not defined"
        locator = self.elements[element]
        return WebDriverWait(self.driver, time).until(EC.presence_of_all_elements_located(locator),
                                                      message=f"Can't find elements {element} by locator {locator}")

    def enter_text(self, element, text):
        elem = self.find_element(element)
        elem.send_keys(text)

    def element_exists(self, element):
        elements = self.find_elements(element, 2)
        if len(elements) == 0:
            return False
        return True

    def open_main(self):
        return self.driver.get(self.base_url)


class PageLogin(Page):
    elements = {
        "edit_name": (By.XPATH, "//input[@type='text']"),
        "edit_pass": (By.XPATH, "//input[@type='password']"),
        "btn_enter": (By.XPATH, "//span[@class='v-btn__content'][contains(.,'войти')]"),
        "lnk_forgotPass": (By.XPATH, "//a[@class='black--text mt-4 d-block'][contains(.,'Забыли пароль?')]"),
        "edit_email": (By.XPATH, "(//input[@type='text'])[2]"),
        "btn_cancel": (By.XPATH, "//button[contains(., 'ОТМЕНИТЬ')]"),
        "btn_send": (By.XPATH, "//button[@type='button'][contains(.,'ДАЛЕЕ')]"),
        "err_wrong_email_format": (By.XPATH, "//div[@class='v-messages__message'][contains(.,'Неверный формат почты')]"),
        "err_user_not_found": (By.XPATH, "//div[@class='v-messages__message'][contains(.,'Пользователь с таким адресом не найден')]"),
    }

    def wait_page_load(self):
        self.find_element("lnk_forgotPass")

    def enter_name(self, name):
        self.enter_text("edit_name", name)

    def enter_pass(self, password):
        self.enter_text("edit_pass", password)

    def click_enter(self):
        self.find_element("btn_enter").click()

    def click_forgot_pass(self):
        self.find_element("lnk_forgotPass").click()

    def enter_email(self, email):
        self.enter_text("edit_email", email)

    def click_cancel(self):
        self.find_element("btn_cancel").click()

    def click_send_email(self):
        self.find_element("btn_send").click()

    def check_error(self):
        pass
