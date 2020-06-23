"""The Library contains
classes for main application entities
and typical actions, like login, create user, etc.
"""
from selenium.webdriver.common.keys import Keys
import lib_pages


class User:
    first_name = ""
    middle_name = ""
    last_name = ""
    email = ""
    password = ""
    role = ""
    organization = ""
    job_title = ""

    is_active = True
    curation = []
    photo = ""

    def create(self):
        pass

    def modify(self):
        pass

    def get(self):
        pass


class Organization:
    name = ""
    is_active = True

    def create(self):
        pass

    def modify(self):
        pass

    def get(self):
        pass


class Event:
    name = ""
    organization = ""
    begin_date = ""
    begin_time = ""
    teacher = ""
    students = []
    observers = []

    def create(self):
        pass

    def modify(self):
        pass

    def get(self):
        pass


class Actions:
    def __init__(self, driver):
        self.driver = driver

    def login(self, name, password):
        page = lib_pages.PageLogin(self.driver)
        page.open_main()
        page.enter_name(name)
        page.enter_pass(password + Keys.RETURN)
        page.click_enter()
        # page.enter_pass(password + Keys.RETURN)

    def login_admin(self):
        self.login("admin@example.com", "1qaz@WSX")


