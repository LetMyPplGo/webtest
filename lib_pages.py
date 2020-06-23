"""This library contains Page-Classes
with all elements on pages
and related actions
"""
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from framework import BASE_URL
from time import time, sleep
import json

# month names in the UI
MONTHS = {
    1: "янв.",
    2: "февр.",
    3: "март",
    4: "апр.",
    5: "май",
    6: "июнь",
    7: "июль",
    8: "авг.",
    9: "сент.",
    10: "окт.",
    11: "нояб.",
    12: "дек.",
}

# load UI map from file - once for all pages
with open('ui.json') as json_file:
    UI_MAP = json.load(json_file)


# Parent for all pages
class Page:
    elements = {}

    def __init__(self, driver):
        self.driver = driver
        self.base_url = BASE_URL

    # def find_element_by_xpath(self, element, wait=10):
    #     assert element in self.elements, f"element {element} is not defined"
    #     locator = self.elements[element]
    #     return WebDriverWait(self.driver, wait).until(EC.presence_of_element_located(locator),
    #                                                   message=f"Can't find element {element} by locator {locator}")
    #
    # def find_elements(self, element, wait=10):
    #     assert element in self.elements, f"element {element} is not defined"
    #     locator = self.elements[element]
    #     return WebDriverWait(self.driver, wait).until(EC.presence_of_all_elements_located(locator),
    #                                                   message=f"Can't find elements {element} by locator {locator}")

    def build_xpath(self, element):
        # TODO: start using it in find_element_by_xpath or rewrite if all elements will have IDs
        page_name = self.__class__.__name__
        # try:
        if UI_MAP[page_name][element]["id"] != "":
            return "//*[@id='{}']".format(UI_MAP[page_name][element]["id"])

        if UI_MAP[page_name][element]["xpath"] != "":
            return UI_MAP[page_name][element]["xpath"]

        raise ValueError
        # except

    def find_element_by_xpath(self, element, **kwargs):
        """element is  either:
                            1) real xpath or
                            2) key in the self.elements dictionary where value is xpath
                            second option makes you write a little less code
        optional named arguments:
            wait - time to wait for an element
            format - tulip of values to insert into xpath. For cases when xpath contains {}
        """
        wait = 10
        if "wait" in kwargs.keys():
            wait = kwargs["wait"]

        xpath = element
        if element in self.elements:
            xpath = self.elements[element]
        if "format" in kwargs.keys():
            xpath = xpath.format(*kwargs["format"])
        locator = (By.XPATH, xpath)
        return WebDriverWait(self.driver, wait).until(EC.presence_of_element_located(locator),
                                                      message=f"Can't find element {element} by locator {locator}")

    def find_elements_by_xpath(self, element, **kwargs):
        wait = 10
        if "wait" in kwargs.keys():
            wait = kwargs["wait"]

        xpath = element
        if element in self.elements:
            xpath = self.elements[element]
        if "format" in kwargs.keys():
            xpath.format(*kwargs["format"])
        locator = (By.XPATH, xpath)
        return WebDriverWait(self.driver, wait).until(EC.presence_of_all_elements_located(locator),
                                                      message=f"Can't find elements {element} by locator {locator}")

    def enter_text(self, element, text):
        elem = self.find_element_by_xpath(element)
        elem.send_keys(text)

    def element_exists(self, element):
        elements = self.find_elements_by_xpath(element, wait=2)
        if len(elements) == 0:
            return False
        return True

    def open_main(self):
        return self.driver.get(self.base_url)


class PageLogin(Page):
    elements = {
        "edit_name": "//input[@type='text']",
        "edit_pass": "//input[@type='password']",
        "btn_enter": "//span[@class='v-btn__content'][contains(.,'войти')]",
        "lnk_forgotPass": "//a[@class='black--text mt-4 d-block'][contains(.,'Забыли пароль?')]",
        "edit_email": "(//input[@type='text'])[2]",
        "btn_cancel": "//button[contains(., 'ОТМЕНИТЬ')]",
        "btn_send": "//button[@type='button'][contains(.,'ДАЛЕЕ')]",
        "err_wrong_email_format": "//div[@class='v-messages__message'][contains(.,'Неверный формат почты')]",
        "err_user_not_found": "//div[@class='v-messages__message'][contains(.,'Пользователь с таким адресом не найден')]",
    }

    def enter_name(self, name):
        self.enter_text("edit_name", name)

    def enter_pass(self, password):
        self.enter_text("edit_pass", password)

    def click_enter(self):
        self.find_element_by_xpath("btn_enter").click()
        return PageEvents(self.driver)

    def click_forgot_pass(self):
        self.find_element_by_xpath("lnk_forgotPass").click()

    def enter_email(self, email):
        self.enter_text("edit_email", email)

    def click_cancel(self):
        self.find_element_by_xpath("btn_cancel").click()

    def click_send_email(self):
        self.find_element_by_xpath("btn_send").click()

    def error_wrong_format(self):
        return self.element_exists("err_wrong_email_format")

    def error_user_not_found(self):
        return self.element_exists("err_user_not_found")


class PageMainHeader(Page):
    """This is header of all pages"""
    elements = {
        "btn_events": "//span[@class='v-btn__content'][contains(.,'Мероприятия')]",
        "btn_missions": "//span[@class='v-btn__content'][contains(.,'Миссии')]",
        "btn_administration": "//span[@class='v-btn__content'][contains(.,'Административная панель')]",
        "btn_exit": "//i[contains(@class,'v-icon notranslate mdi mdi-exit-to-app theme--dark')]",
        "text_welcome": "//span[contains(@class,'white--text')]",
    }

    def click_events(self):
        self.find_element_by_xpath("btn_events").click()
        return PageEvents(self.driver)

    def click_missions(self):
        self.find_element_by_xpath("btn_missions").click()
        return PageMissions(self.driver)

    def click_administration(self):
        self.find_element_by_xpath("btn_administration").click()
        return PageAdminHeader(self.driver)

    def click_exit(self):
        self.find_element_by_xpath("btn_exit").click()

    def get_welcome_text(self):
        elem = self.find_element_by_xpath("text_welcome")
        return elem.text()


class PageEventInList(Page):
    def __init__(self, driver, name):
        super().__init__(driver)
        self.name = name
        self.div_event_by_name = f"//div[contains(@class, 'v-card v-sheet')][contains(., '{name}')]"
        self.elements = {
            "div_event_by_name": self.div_event_by_name,
            "lnk_event_name": self.div_event_by_name + "//a[contains(@href, 'event')]",
            "lnk_teacher": self.div_event_by_name + "//span[contains(@class,'ml-3')]",
            "text_users_amount": self.div_event_by_name + "//span[contains(@class, 'mr-10')]",
            "text_duration": self.div_event_by_name + "//span[contains(@class, 'mr-2')]",
            "text_organization": self.div_event_by_name + "//div[contains(@class, 'v-list-item__content text-right')]",
            "text_mission_name": self.div_event_by_name + "//div[contains(@class, 'pa-0 col-sm-4 col-12')]//h4",
            "text_mission_text": self.div_event_by_name + "//div[contains(@class, 'pa-1 col-sm-5 col-12')]//div//p",
            "div_stars": self.div_event_by_name + "//div[contains(@class, 'v-rating')]//button[contains(@class, 'mdi-star ')]",
            "btn_get_report": self.div_event_by_name + "//span[@class='v-btn__content'][contains(.,'Получить отчёт')]",
            "text_state": self.div_event_by_name + "//span[contains(@class,'mr-3')]",
        }

    def get_event_data(self):
        """returns all data from the event by its name"""
        same_name_amount = len(self.find_elements_by_xpath("div_event_by_name"))
        ret = {
            "event_name": self.find_element_by_xpath("lnk_event_name").text,
            "users_amount": self.find_element_by_xpath("text_users_amount").text,
            "duration": self.find_element_by_xpath("text_duration").text,
            "organization": self.find_element_by_xpath("text_organization").text,
            "mission_name": self.find_element_by_xpath("text_mission_name").text,
            "mission_text": self.find_element_by_xpath("text_mission_text").text,
            "teacher": self.find_element_by_xpath("lnk_teacher").text,
            "state": self.find_element_by_xpath("text_state").text,
            "report_exists": self.element_exists("btn_get_report"),
            "stars": int(len(self.find_elements_by_xpath("div_stars")) / same_name_amount)
        }
        return ret

    def click_event(self):
        self.find_element_by_xpath("lnk_event_name").click()

    def click_teacher(self):
        self.find_element_by_xpath("lnk_teacher").click()

    def click_report(self):
        self.find_element_by_xpath("btn_get_report").click()


class PageEvents(Page):
    div_event = "//div[contains(@class, 'v-card v-sheet')]"
    div_event_by_name = "//div[contains(@class, 'v-card v-sheet')][contains(., '{}')]"

    def get_event_by_name(self, name):
        """return the PageEvent object from the list by its name"""
        element = self.find_elements_by_xpath(self.div_event_by_name.format(name))
        if len(element) == 0:
            return None
        return PageEventInList(self.driver, name)


class PageMission(Page):
    def __init__(self, driver, name):
        super().__init__(driver)
        self.name = name
        self.div_mission_by_name = f"//div[contains(@class, 'v-card v-sheet')][contains(., '{name}')]"
        self.elements = {
            "div_mission_by_name": self.div_mission_by_name,
            "mission_name": self.div_mission_by_name + "//div[contains(@class, 'v-list-item--two-line')]//div[contains(@class, 'v-list-item__title')]",
            "industry": self.div_mission_by_name + "//div[contains(@class, 'v-list-item--two-line')]//div[contains(@class, 'v-list-item__subtitle')]",
            "mode_single": self.div_mission_by_name + "//i[contains(@class,'mdi-shield')]",
            "stars": self.div_mission_by_name + "//div[contains(@class, 'v-rating')]//button[contains(@class, 'mdi-star ')]",
            "infra_template": self.div_mission_by_name + "//div[contains(@class, 'card-footer-background')]//div[contains(@class, 'v-list-item__title')]",
            "users_limit": self.div_mission_by_name + "//span[contains(@class, 'mr-10')]",
            "duration_limit": self.div_mission_by_name + "//span[contains(@class, 'mr-2')]",
            "description": self.div_mission_by_name + "//div[contains(@class, 'col-sm-10')]",
            "lnk_new_event": self.div_mission_by_name + "//a[contains(@class, 'v-btn')]",
        }

    def get_mission_data(self):
        """returns all data from the event by its name"""
        same_name_amount = len(self.find_elements_by_xpath("div_mission_by_name"))
        ret = {
            "mission_name": self.find_element_by_xpath("mission_name").text,
            "industry": self.find_element_by_xpath("industry").text,
            # "mode_single": self.find_element_by_xpath("mode_single").text,
            "stars": int(len(self.find_elements_by_xpath("stars")) / same_name_amount),
            "infra_template": self.find_element_by_xpath("infra_template").text,
            "users_limit": self.find_element_by_xpath("users_limit").text,
            "duration_limit": self.find_element_by_xpath("duration_limit").text,
            "description": self.find_element_by_xpath("description").text,
        }
        if self.element_exists("mode_single"):
            ret["mode"] = "single"

        return ret

    def click_new_event(self):
        self.find_element_by_xpath("lnk_new_event").click()
        return PageEventEdit(self.driver)


class PageMissions(Page):
    div_mission = "//div[contains(@class, 'v-card v-sheet')]"
    div_mission_by_name = "//div[contains(@class, 'v-card v-sheet')][contains(., '{}')]"

    def get_mission_by_name(self, name):
        """return the PageEvent object from the list by its name"""
        element = self.find_elements_by_xpath(self.div_mission_by_name.format(name))
        if len(element) == 0:
            return None
        return PageMission(self.driver, name)


class PageAdminHeader(Page):
    elements = {
        "lnk_users": "//div[contains(.,'Учетные записи')]",
        "lnk_organizations": "//div[contains(.,'Организации')]",
        "lnk_infrastructure": "//div[contains(.,'Инфраструктура')]",
    }

    def click_users(self):
        self.find_element_by_xpath("lnk_users").click()
        return PageAdminUsers(self.driver)

    def click_organizations(self):
        self.find_element_by_xpath("lnk_organizations").click()

    def click_infrastructure(self):
        self.find_element_by_xpath("lnk_infrastructure").click()


class PageAdminUsers(Page):
    # //div[contains(@class, 'v-menu__content')]//div[contains(@class, 'v-list-item__content')][contains(., '134')]
    elements = {

    }


class PageEventEdit(Page):
    elements = {
        "mode_vs": "//div[contains(@class, 'v-list-item--two-line')]//span[contains(., 'VS')]",
        "infra_template": "(//div[contains(@class, 'v-list-item__title')])[1]",
        "users_limit": "(//div[contains(@class, 'v-list-item__title')])[2]",
        "duration_limit": "(//div[contains(@class, 'v-list-item__title')])[3]",
        "stars": "//div[contains(@class, 'v-rating')]//button[contains(@class, 'mdi-star ')]",
        "event_name": "//label[.='Название мероприятия*']/following-sibling::input",
        "event_name_error": "(//div[contains(@class, 'v-text-field__details')])[1]",
        "organization_open_list": "//label[.='Организация*']/following-sibling::div//i[contains(@class, 'mdi-menu-down')]",
        "organization_list_items": "//div[contains(@class, 'v-menu__content')][contains(@class, 'menuable__content__active')]",
        "organization_list_item": "//div[@class='v-list-item__title'][contains(.,'{}')]",
        "organization_error": "(//div[contains(@class, 'v-text-field__details')])[2]",
        "begin_date": "//label[.='Дата начала*']/following-sibling::input",
        "begin_date_header": "//div[contains(@class, 'v-date-picker-header__value')]//button",
        "begin_date_year": "//div[contains(@class, 'v-picker')]//li[.='{}']",
        "begin_date_month": "//div[contains(@class, 'v-date-picker-table')]//div[.='{}']",
        "begin_date_day": "//div[contains(@class, 'v-date-picker-table')]//div[.='{}']",
        "begin_date_error": "(//div[contains(@class, 'v-text-field__details')])[3]",
        "begin_time": "//label[.='Время начала*']/following-sibling::input",
        "begin_time_error": "(//div[contains(@class, 'v-text-field__details')])[4]",
        "teacher": "",
        "lnk_add_students": "",
        "lnk_add_observers": "",
        "lnk_save": "",
    }

    def set_name(self, name):
        self.find_element_by_xpath("event_name").send_keys(name)

    def set_organization(self, name):
        self.find_element_by_xpath("organization_open_list").click()
        self.find_element_by_xpath("organization_list_item", format=(name, )).click()

    def set_date(self, year, month, day):
        self.find_element_by_xpath("begin_date").click()
        self.find_element_by_xpath("begin_date_header").click()
        sleep(1)
        self.find_element_by_xpath("begin_date_header").click()
        self.find_element_by_xpath("begin_date_year", format=(year, )).click()
        self.find_element_by_xpath("begin_date_month", format=(MONTHS[month], )).click()
        self.find_element_by_xpath("begin_date_day", format=(day, )).click()

    def set_time(self, time_to_set):
        for s in time_to_set:
            self.find_element_by_xpath("begin_time").send_keys(s)

