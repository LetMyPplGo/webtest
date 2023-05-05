from html.parser import HTMLParser
import json
import requests

MAIL_SERVER = ""


class EmailParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_data = ""
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr in attrs:
                if attr[0] == 'href':
                    self.links.append(attr[1])
        # print("Encountered a start tag:", tag)

    def handle_endtag(self, tag):
        pass
        # print("Encountered an end tag :", tag)

    def handle_data(self, data):
        self.text_data = self.text_data + " " + data
        # print("Encountered some data  :", data)


class Email:
    def __init__(self, json_email):
        self.email = json_email
        self.sender = self.email['headers']['from']
        self.recipient = self.email['headers']['to']
        self.subject = self.email['headers']['subject']
        self.html_body = self.email['html']
        self.mail_id = self.email['id']

        html_parser = EmailParser()
        html_parser.feed(self.html_body)

        self.text_body = html_parser.text_data
        self.links = html_parser.links


def iterate_emails():
    r = requests.get(f"{MAIL_SERVER}/email", auth=('user', '*******'))
    assert r.status_code == 200, f"Bad response from {MAIL_SERVER}: {r.status_code}"
    for one_mail in r.json():
        yield Email(one_mail)


def delete_email(mail_id):
    r = requests.delete(f"{MAIL_SERVER}/email/{mail_id}")
    assert r.status_code == 200, f"Bad response from {MAIL_SERVER}: {r.status_code}"
    return 0




