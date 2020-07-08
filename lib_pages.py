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
import globals

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
        # TODO: explicitly specify name of the json section in ui.json in every class. As they can be reused
        page_name = self.__class__.__name__

        # first check if xpath is explicitly specified in the elements dictionary
        if element in self.elements:
            return self.elements[element]

        # now check that ui.json has id for this element
        if "id" in UI_MAP[page_name]["elements"][element]:
            return "//*[@id='{}']".format(UI_MAP[page_name]["elements"][element]["id"])

        # check if ui.json has xpath for this element
        if "xpath" in UI_MAP[page_name]["elements"][element]:
            return UI_MAP[page_name]["elements"][element]["xpath"]

        # finally return the element itself
        return element

    def find_element_by_xpath(self, element, **kwargs):
        """element is  either:
                            1) real xpath or
                            2) key in the self.elements dictionary where value is xpath
                            second option makes you write a little less code
        optional named arguments:
            wait - time to wait for an element, default value = 10
            format - tulip of values to insert into xpath. For cases when xpath contains {}
            ec - wait for object to exist (globals.EC_EXISTS) or to become clickable (globals.EC_CLICKABLE)
        """
        wait = kwargs.get('wait', 10)
        xpath = self.build_xpath(element)
        # if element in self.elements:
        #     xpath = self.elements[element]
        if "format" in kwargs.keys():
            xpath = xpath.format(*kwargs["format"])
        locator = (By.XPATH, xpath)
        ec = kwargs.get('ec', globals.EC_EXISTS)
        wait_func = getattr(EC, ec)
        return WebDriverWait(self.driver, wait).until(wait_func(locator),
                                                      message=f"Can't find element {element} by locator {locator}")
        # return WebDriverWait(self.driver, wait).until(EC.presence_of_element_located(locator),
        #                                               message=f"Can't find element {element} by locator {locator}")

    def find_elements_by_xpath(self, element, **kwargs):
        wait = kwargs.get('wait', 10)
        xpath = self.build_xpath(element)
        # if element in self.elements:
        #     xpath = self.elements[element]
        if "format" in kwargs.keys():
            xpath.format(*kwargs["format"])
        locator = (By.XPATH, xpath)
        return WebDriverWait(self.driver, wait).until(EC.presence_of_all_elements_located(locator),
                                                      message=f"Can't find elements {element} by locator {locator}")

    def enter_text(self, element, text):
        elem = self.find_element_by_xpath(element)
        elem.send_keys(text)

    def element_exists(self, element):
        elements = self.driver.find_elements(By.XPATH, self.build_xpath(element))
        if len(elements) == 0:
            return False
        return True

    def open_main(self):
        return self.driver.get(self.base_url)


class PageLogin(Page):
    def enter_name(self, name):
        self.enter_text("email", name)

    def enter_pass(self, password):
        self.enter_text("password", password)

    def click_enter(self):
        self.find_element_by_xpath("btn_enter").click()
        return PageEvents(self.driver)

    def click_forgot_pass(self):
        self.find_element_by_xpath("lnk_forgot_pass").click()

    def forgot_pass_enter_email(self, email):
        self.enter_text("forgot_pass_email", email)

    def forgot_pass_click_cancel(self):
        self.find_element_by_xpath("btn_forgot_pass_cancel").click()

    def forgot_pass_click_send(self):
        self.find_element_by_xpath("btn_forgot_pass_enter").click()

    def forgot_pass_get_error(self):
        return self.element_exists("forgot_pass_email_error")

    def todo(self):
        # TODO: login/pass error check
        pass


class PageMainHeader(Page):
    """This is header of all pages"""
    def click_events(self):
        self.find_element_by_xpath("btn_menu").click()
        self.find_element_by_xpath("btn_events").click()
        return PageEvents(self.driver)

    def click_missions(self):
        self.find_element_by_xpath("btn_menu").click()
        self.find_element_by_xpath("btn_missions").click()
        return PageMissions(self.driver)

    def click_administration(self):
        self.find_element_by_xpath("btn_menu").click()
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
        self.event_container = self.build_xpath("event_container") + f"[contains(., '{name}')]"
        self.elements = {
            "event_container": self.event_container,
            "event_name": self.event_container + self.build_xpath("event_name"),
            "tutor": self.event_container + self.build_xpath("tutor"),
            "users_amount": self.event_container + self.build_xpath("users_amount"),
            "users_limit": self.event_container + self.build_xpath("users_limit"),
            "time_limit": self.event_container + self.build_xpath("time_limit"),
            "organization": self.event_container + self.build_xpath("organization"),
            "mission_name": self.event_container + self.build_xpath("mission_name"),
            "mission_description": self.event_container + self.build_xpath("mission_description"),
            "stars": self.event_container + self.build_xpath("stars_container") + "//button[contains(@class, 'mdi-star ')]",
            "btn_get_report": self.event_container + "//span[@class='v-btn__content'][contains(.,'Получить отчёт')]",
            "state": self.event_container + self.build_xpath("state"),
        }

    def get_event_data(self):
        """returns all data from the event by its name"""
        same_name_amount = len(self.find_elements_by_xpath("event_container"))
        ret = {
            "event_name": self.find_element_by_xpath("event_name").text,
            "users_amount": self.find_element_by_xpath("users_amount").text,
            "users_limit": self.find_element_by_xpath("users_limit").text,
            "time_limit": self.find_element_by_xpath("time_limit").text,
            "organization": self.find_element_by_xpath("organization").text,
            "mission_name": self.find_element_by_xpath("mission_name").text,
            "mission_description": self.find_element_by_xpath("mission_description").text,
            "tutor": self.find_element_by_xpath("tutor").text,
            "state": self.find_element_by_xpath("state").text,
            "report_exists": self.element_exists("btn_get_report"),
            "stars": int(len(self.find_elements_by_xpath("stars")) / same_name_amount),
            "same_name_amount": same_name_amount
        }
        return ret

    def click_event(self):
        self.find_element_by_xpath("event_name").click()

    def click_teacher(self):
        self.find_element_by_xpath("tutor").click()

    def click_report(self):
        self.find_element_by_xpath("btn_get_report").click()


class PageEvents(Page):
    """Someday this class will contain Search Event methods"""
    pass


class PageMissionInList(Page):
    def __init__(self, driver, name):
        super().__init__(driver)
        self.name = name
        self.mission_container = self.build_xpath("mission_container") + f"[contains(., '{name}')]"
        self.elements = {
            "mission_container": self.mission_container,
            "mission_name": self.mission_container + self.build_xpath("mission_name"),
            "industry": self.mission_container + self.build_xpath("industry"),
            # "mode_single": self.mission_container + self.build_xpath(""),
            "stars": self.mission_container + self.build_xpath("stars_container") + "//button[contains(@class, 'mdi-star ')]",
            "infra_template": self.mission_container + self.build_xpath("infra_template"),
            "users_limit": self.mission_container + self.build_xpath("users_limit"),
            "time_limit": self.mission_container + self.build_xpath("time_limit"),
            "description": self.mission_container + self.build_xpath("mission_description"),
            "btn_new_event": self.mission_container + self.build_xpath("btn_new_event"),
            # "mission_name": self.mission_container + "//div[contains(@class, 'v-list-item--two-line')]//div[contains(@class, 'v-list-item__title')]",
            # "industry": self.mission_container + "//div[contains(@class, 'v-list-item--two-line')]//div[contains(@class, 'v-list-item__subtitle')]",
            "mode_single": self.mission_container + "//i[contains(@class,'mdi-shield')]",
            # "stars": self.mission_container + "//div[contains(@class, 'v-rating')]//button[contains(@class, 'mdi-star ')]",
            # "infra_template": self.mission_container + "//div[contains(@class, 'card-footer-background')]//div[contains(@class, 'v-list-item__title')]",
            # "users_limit": self.mission_container + "//span[contains(@class, 'mr-10')]",
            # "duration_limit": self.mission_container + "//span[contains(@class, 'mr-2')]",
            # "description": self.mission_container + "//div[contains(@class, 'col-sm-10')]",
            # "lnk_new_event": self.mission_container + "//a[contains(@class, 'v-btn')]",
        }

    def get_mission_data(self):
        """returns all data from the event by its name"""
        same_name_amount = len(self.find_elements_by_xpath("mission_container"))
        ret = {
            "mission_name": self.find_element_by_xpath("mission_name").text,
            "industry": self.find_element_by_xpath("industry").text,
            "stars": int(len(self.find_elements_by_xpath("stars")) / same_name_amount),
            "infra_template": self.find_element_by_xpath("infra_template").text,
            "users_limit": self.find_element_by_xpath("users_limit").text,
            "time_limit": self.find_element_by_xpath("time_limit").text,
            "description": self.find_element_by_xpath("description").text,
            "same_name_amount": same_name_amount,
        }
        if self.element_exists("mode_single"):
            ret["mode"] = globals.MODE_SINGLE

        return ret

    def click_new_event(self):
        self.find_element_by_xpath("btn_new_event").click()
        return PageEventEdit(self.driver)


class PageMissions(Page):
    """This class will contain Missions search actions"""
    pass


class PageAdminHeader(Page):
    def click_users(self):
        self.find_element_by_xpath("btn_users").click()
        return PageAdminUsers(self.driver)

    def click_organizations(self):
        self.find_element_by_xpath("btn_organizations").click()
        return PageAdminOrganizations(self.driver)

    def click_infrastructure(self):
        self.find_element_by_xpath("btn_infrastructure").click()

    def check_infra_error(self):
        if self.element_exists("infrastructure_has_error"):
            return True
        return False


class PageAdminUsers(Page):
    # //div[contains(@class, 'v-menu__content')]//div[contains(@class, 'v-list-item__content')][contains(., '134')]
    elements = {
        'btn_create': "//span[contains(.,'Создать пользователя')]"
    }

    def click_create(self):
        self.find_element_by_xpath("btn_new_user").click()
        return PageCreateUser(self.driver)


class PageCreateUser(Page):
    elements = {
        'edit_last_name': "//label[.='Фамилия*']/following-sibling::input",
        'edit_middle_name': "//label[.='Отчество*']/following-sibling::input",
        'edit_first_name': "//label[.='Имя*']/following-sibling::input",
        'edit_email': "//label[.='Логин/Email*']/following-sibling::input",
        "role_open_list": "//label[.='Роль*']/following-sibling::div//i[contains(@class, 'mdi-menu-down')]",
        "role_list_items": "//div[contains(@class, 'v-menu__content')][contains(@class, 'menuable__content__active')]",
        "role_list_item": "//div[@class='v-list-item__title'][contains(.,'{}')]",
        "organization_open_list": "//label[.='Организация*']/following-sibling::div//i[contains(@class, 'mdi-menu-down')]",
        "organization_list_items": "//div[contains(@class, 'v-menu__content')][contains(@class, 'menuable__content__active')]",
        "organization_list_item": "//div[@class='v-list-item__title'][contains(.,'{}')]",
        'edit_job': "//label[.='Должность']/following-sibling::input",
        'edit_status': "//label[.='Статус']/following-sibling::textarea",
        'btn_clear_status': "//div[contains(@class, 'status-container')]/button",
        'label_symbols_count': "//div[contains(., 'символов')][contains(@class, 'v-text-field__details')]",
        "btn_cancel": "//span[contains(.,'Отменить')]",
        "btn_create": "//button[contains(.,'Отменить')]/following-sibling::button",
        "btn_created_ok": "//button[contains(., 'ОК')]"
        # TODO: add error text fields
        # TODO: add timezone selector
        # TODO: add photo and password buttons
    }

    def enter_first_name(self, text):
        self.enter_text('edit_first_name', text)

    def enter_last_name(self, text):
        self.enter_text('edit_last_name', text)

    def enter_middle_name(self, text):
        self.enter_text('edit_middle_name', text)

    def enter_email(self, text):
        self.enter_text('edit_email', text)

    def enter_job(self, text):
        self.enter_text('edit_job', text)

    def enter_status(self, text):
        self.enter_text('edit_status', text)

    def clear_status(self):
        self.find_element_by_xpath("btn_clear_status").click()

    def click_cancel(self):
        self.find_element_by_xpath("btn_cancel").click()

    def click_create(self):
        self.find_element_by_xpath("btn_create").click()

    def click_created_ok(self):
        self.find_element_by_xpath("btn_created_ok", ec=globals.EC_CLICKABLE).click()

    def set_organization(self, name):
        self.find_element_by_xpath("organization_open_list").click()
        self.find_element_by_xpath("organization_list_item", format=(name, )).click()

    def set_role(self, name):
        self.find_element_by_xpath("role_open_list").click()
        self.find_element_by_xpath("role_list_item", format=(name, )).click()


class PageAdminOrganizations(Page):
    elements = {
        "btn_create": "//span[contains(.,'Создать организацию')]"
    }

    def click_create(self):
        self.find_element_by_xpath("btn_create").click()
        return PageCreateOrganization(self.driver)


class PageCreateOrganization(Page):
    elements = {
        "edit_name": "//label[contains(., 'Организация')]/following-sibling::input",
        "btn_cancel": "//span[contains(.,'Отменить')]",
        "btn_create": "//button[contains(.,'Отменить')]/following-sibling::button",
        "btn_created_ok": "//button[contains(., 'ОК')]"
    }

    def enter_name(self, name):
        self.enter_text("edit_name", name)

    def click_cancel(self):
        self.find_element_by_xpath("btn_cancel").click()

    def click_create(self):
        self.find_element_by_xpath("btn_create", ec=globals.EC_CLICKABLE).click()

    def click_created_ok(self):
        self.find_element_by_xpath("btn_created_ok", ec=globals.EC_CLICKABLE).click()


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

