from selenium.webdriver.common.keys import Keys
import lib_pages


class User:
    first_name = ""
    second_name = ""
    surname = ""
    email = ""
    password = ""
    role = ""
    organization = ""
    job_title = ""

    is_active = True
    curation = []
    photo = ""


class Organization:
    name = ""
    is_active = True


class Event:
    name = ""
    organization = ""
    begin_date = ""
    begin_time = ""
    teacher = ""
    students = []
    observers = []


class Actions:
    def __init__(self, driver):
        self.driver = driver

    def login(self, name, password):
        page = lib_pages.PageLogin(self.driver)
        page.open_main()
        page.enter_name(name)
        page.enter_pass(password + Keys.RETURN)

    def login_admin(self):
        self.login("admin@example.com", "1qaz@WSX")

    def add_user(self, user):
        pass

