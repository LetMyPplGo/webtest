"""The Library contains
classes for main application entities
and typical actions, like login, create user, etc.
"""
from selenium.webdriver.common.keys import Keys
import lib_pages
import random
import string


class User:
    def __init__(self, driver):
        self.driver = driver
        self.first_name = ""
        self.middle_name = ""
        self.last_name = ""
        self.email = ""
        self.password = ""
        self.role = ""
        self.organization = ""
        self.job_title = ""

        self.is_active = True
        self.curation = []
        self.photo = ""

    def fill_random(self, string_length=10):
        letters_digits = string.ascii_letters + string.digits
        letters = string.ascii_letters

        self.first_name = ''.join((random.choice(letters) for i in range(string_length)))
        self.middle_name = ''.join((random.choice(letters) for i in range(string_length)))
        self.last_name = ''.join((random.choice(letters) for i in range(string_length)))
        self.email = ''.join((random.choice(letters) for i in range(string_length))) + '@' + ''.join((random.choice(letters) for i in range(string_length))) + '.com'
        self.password = ''.join((random.choice(letters_digits) for i in range(string_length)))
        self.job_title = ''.join((random.choice(letters) for i in range(string_length)))

        # self.role = ""
        # self.organization = ""
        # self.is_active = True
        # self.curation = []
        # self.photo = ""

    def create(self):
        page = lib_pages.PageMainHeader(self.driver).click_administration().click_users().click_create()
        page.enter_first_name(self.first_name)
        page.enter_middle_name(self.middle_name)
        page.enter_last_name(self.last_name)
        page.enter_email(self.email)
        page.set_organization(self.organization)
        page.set_role(self.role)
        page.click_create()
        page.click_created_ok()

    def modify(self):
        pass

    def get(self):
        pass


class Organization:
    def __init__(self, driver):
        self.driver = driver
        self.name = ""
        self.is_active = True

    def fill_random(self, string_length=10):
        self.name = ''.join((random.choice(string.ascii_letters) for i in range(10)))

    def create(self):
        page = lib_pages.PageMainHeader(self.driver).click_administration().click_organizations().click_create()
        page.enter_name(self.name)
        page.click_create()
        page.click_created_ok()

    def modify(self):
        pass

    def get(self):
        pass


class Event:
    def __init__(self, driver):
        self.driver = driver
        self.name = ""
        self.organization = ""
        self.begin_date = ""
        self.begin_time = ""
        self.teacher = ""
        self.students = []
        self.observers = []

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
        page.enter_pass(password)
        # page.enter_pass(password + Keys.RETURN)
        page.click_enter()

    def login_admin(self):
        self.login("admin@example.com", "1qaz@WSX")

    def create_organization(self):
        # TODO: logoff first
        self.login_admin()
        page = lib_pages.PageMainHeader.click_administration().click_organizations().click_create()
        page.enter_name(''.join((random.choice(string.ascii_letters) for i in range(10))))
        page.click_create()

