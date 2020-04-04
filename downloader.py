from time import sleep
from selenium import webdriver

URL = 'https://www.fakku.net/hentai/just-a-moment-english/read/page/1'


class FDownloader():
    def __init__(self, urls, exec_path='phantomjs'):
        self.urls = urls
        self.browser = webdriver.PhantomJS(
            executable_path=exec_path)

    def auth(self, login, password):
        pass

    def load_all(self):
        pass

