import os
import pickle

from shutil import rmtree
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, JavascriptException

from bs4 import BeautifulSoup as bs
from tqdm import tqdm

LOGIN_URL = 'https://www.fakku.net/login/'
# Initial display settings for headless browser. Any manga in this
# resolution will be opened correctly and with the best quality.
MAX_DISPLAY_SETTINGS = [1440, 2560]
# Path to headless driver
EXEC_PATH = 'chromedriver.exe'
# File with manga urls
URLS_FILE = 'urls.txt'
# File with completed urls
DONE_FILE = 'done.txt'
# File with prepared cookies
COOKIES_FILE = 'cookies.pickle'
# Root directory for manga downloader
ROOT_MANGA_DIR = 'manga'
# Timeout to page loading in seconds
TIMEOUT = 5
# Wait between page loading in seconds
WAIT = 1


def program_exit():
    print('Program exit.')
    exit()


class FDownloader():
    """
    Class which allows download manga.
    The main idea of download - using headless browser and just saving
    screenshot from that. Because canvas in fakku.net is protected
    from download via simple .toDataURL js function etc.
    """
    def __init__(self,
            urls_file=URLS_FILE,
            done_file=DONE_FILE,
            cookies_file=COOKIES_FILE,
            driver_path=EXEC_PATH,
            default_display=MAX_DISPLAY_SETTINGS,
            timeout=TIMEOUT,
            wait=WAIT,
            login=None,
            password=None,
        ):
        """
        param: urls_file -- string name of .txt file with urls
            Contains list of manga urls, that's to be downloaded
        param: done_file -- string name of .txt file with urls
            Contains list of manga urls that have successfully been downloaded
        param: cookies_file -- string name of .picle file with cookies
            Contains bynary data with cookies
        param: driver_path -- string
            Path to the headless driver
        param: default_display -- list of two int (width, height)
            Initial display settings. After loading the page, they will be changed
        param: timeout -- float
            Timeout upon waiting for page to load
            If <5 may be poor quality.
        param: wait -- float
            Wait in seconds beetween pages downloading.
            If <1 may be poor quality.
        param: login -- string
            Login or email for authentication
        param: password -- string
            Password for authentication
        """
        self.urls = self.__get_urls_list(urls_file, done_file)
        self.done_file = done_file
        self.cookies_file = cookies_file
        self.driver_path = driver_path
        self.browser = None
        self.default_display = default_display
        self.timeout = timeout
        self.wait = wait
        self.login = login
        self.password = password

    def init_browser(self, headless=False):
        """
        Initializing browser and authenticate if necessary
        ---------------------
        param: headless -- bool
            If True: launch browser in headless mode(for download manga)
            If False: launch usualy browser with GUI(for first authenticate)
        """
        options = Options()
        options.headless = headless
        self.browser = webdriver.Chrome(
            executable_path=self.driver_path,
            chrome_options=options
        )
        if not headless:
            self.__auth()
        self.__set_cookies()
        self.browser.set_window_size(*self.default_display)

    def __set_cookies(self):
        self.browser.get(LOGIN_URL)
        #self.browser.delete_all_cookies()
        with open(self.cookies_file, 'rb') as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                if 'expiry' in cookie:
                    cookie['expiry'] = int(cookie['expiry'])
                    self.browser.add_cookie(cookie)
        # self.browser.get(LOGIN_URL)

    def __init_headless_browser(self):
        """
        Recreating browser in headless mode(without GUI)
        """
        options = Options()
        options.headless = True
        self.browser = webdriver.Chrome(
            executable_path=self.driver_path,
            chrome_options=options)

    def __auth(self):
        """
        Authentication in browser with GUI for saving cookies in first time
        """
        self.browser.get(LOGIN_URL)
        if not self.login is None:
            self.browser.find_element_by_id('username').send_keys(self.login)
        if not self.password is None:
            self.browser.find_element_by_id('password').send_keys(self.password)
        self.browser.find_element_by_class_name('js-submit').click()

        ready = input("Tab Enter to continue after you login...")
        with open(self.cookies_file, 'wb') as f:
            pickle.dump(self.browser.get_cookies(), f)

        self.browser.close()
        # Recreating browser in headless mode for next manga downloading
        self.__init_headless_browser()

    def load_all(self):
        """
        Just main function witch opening each page and save it in .png
        """
        self.browser.set_window_size(*self.default_display)
        if not os.path.exists(ROOT_MANGA_DIR):
            os.mkdir(ROOT_MANGA_DIR)
        with open(self.done_file, 'a') as done_file_obj:
            for url in self.urls:
                manga_name = url.split('/')[-1]
                manga_folder = os.sep.join([ROOT_MANGA_DIR, manga_name])
                if not os.path.exists(manga_folder):
                   os.mkdir(manga_folder)
                self.browser.get(url)
                self.waiting_loading_page(is_main_page=True)
                page_count = self.__get_page_count(self.browser.page_source)
                print(f'Downloading "{manga_name}" manga.')
                for page_num in tqdm(range(1, page_count + 1)):
                    self.browser.get(f'{url}/read/page/{page_num}')
                    self.waiting_loading_page(is_main_page=False)

                    # Count of leyers may be 2 or 3 therefore we get different target layer
                    n = self.browser.execute_script("return document.getElementsByClassName('layer').length")
                    try:
                        # Resizing window size for exactly manga page size
                        width = self.browser.execute_script(f"return document.getElementsByTagName('canvas')[{n-2}].width")
                        height = self.browser.execute_script(f"return document.getElementsByTagName('canvas')[{n-2}].height")
                        self.browser.set_window_size(width, height)
                    except JavascriptException:
                        print('\nSome error with JS. Page source are note ready. You can try increase argument -t')

                    # Delete all UI
                    self.browser.execute_script(f"document.getElementsByClassName('layer')[{n-1}].remove()")
                    self.browser.save_screenshot(os.sep.join([manga_folder, f'{page_num}.png']))
                print('>> manga done!')
                done_file_obj.write(f'{url}\n')

    def __get_page_count(self, page_source):
        """
        Get count of manga pages from html code
        ----------------------------
        param: page_source -- string
            String that contains html code
        return: int
            Number of manga pages
        """
        soup = bs(page_source, 'html.parser')
        page_count = None
        if not page_count:
            try:
                page_count = int(soup.find_all('div', attrs={'class': 'row'})[5]
                    .find('div', attrs={'class': 'row-right'}).text
                    .split(' ')[0])
            except Exception as ex:
                print(ex)
        return page_count

    def __get_urls_list(self, urls_file, done_file):
        """
        Get list of urls from .txt file
        --------------------------
        param: urls_file -- string
            Name or path of .txt file with manga urls
        param: done_file -- string
            Name or path of .txt file with successfully downloaded manga urls
        return: urls -- list
            List of urls from urls_file
        """
        done = []
        with open(done_file, 'r') as donef:
            for line in donef:
                done.append(line.replace('\n',''))

        urls = []
        with open(urls_file, 'r') as f:
            for line in f:
                clean_line = line.replace('\n','')
                if clean_line not in done:
                    urls.append(clean_line)
        return urls

    def waiting_loading_page(self, is_main_page=True):
        """
        Awaiting while page will load
        ---------------------------
        param: is_main_page -- bool
            False -- awaiting of main manga page
            True -- awaiting of others manga pages
        """
        if is_main_page:
            elem_xpath = "//link[@type='image/x-icon']"
        else:
            sleep(self.wait)
            elem_xpath = "//div[@data-name='PageView']"
        try:
            element = EC.presence_of_element_located((By.XPATH, elem_xpath))
            WebDriverWait(self.browser, self.timeout).until(element)
        except TimeoutException:
            print('\nError: timed out waiting for page to load. + \
                You can try increase param -t for more delaying.')
            program_exit()
