import os
import pickle
import re
from shutil import rmtree
from time import sleep
from typing import Optional, List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, JavascriptException

from bs4 import BeautifulSoup as bs
from tqdm import tqdm


BASE_URL = "https://www.fakku.net"
LOGIN_URL = f"{BASE_URL}/login/"
# Initial display settings for headless browser. Any manga in this
# resolution will be opened correctly and with the best quality.
MAX_DISPLAY_SETTINGS = [1440, 2560]
# Path to headless driver
EXEC_PATH = "chromedriver.exe"
# File with manga urls
URLS_FILE = "urls.txt"
# File with completed urls
DONE_FILE = "done.txt"
# File with prepared cookies
COOKIES_FILE = "cookies.pickle"
# Root directory for manga downloader
ROOT_MANGA_DIR = "manga"
# Timeout to page loading in seconds
TIMEOUT = 5
# Wait between page loading in seconds
WAIT = 2
# Max manga to download in one session (-1 == no limit)
MAX = None
# User agent for web browser
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"


def program_exit():
    print("Program exit.")
    exit()


class FDownloader:
    """
    Class which allows download manga.
    The main idea of download - using headless browser and just saving
    screenshot from that. Because canvas in fakku.net is protected
    from download via simple .toDataURL js function etc.
    """

    def __init__(
        self,
        urls_file: str = URLS_FILE,
        done_file: str = DONE_FILE,
        cookies_file: str = COOKIES_FILE,
        root_manga_dir: str = ROOT_MANGA_DIR,
        driver_path:str = EXEC_PATH,
        default_display: List[int] = MAX_DISPLAY_SETTINGS,
        timeout: float = TIMEOUT,
        wait: float = WAIT,
        login: Optional[str] = None,
        password: Optional[str] = None,
        _max: Optional[int] = MAX,
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
            Timeout upon waiting for first page to load
            If <5 may be poor quality.
        param: wait -- float
            Wait in seconds beetween pages downloading.
            If <1 may be poor quality.
        param: login -- string
            Login or email for authentication
        param: password -- string
            Password for authentication
        """
        self.urls_file = urls_file
        self.urls = self.__get_urls_list(urls_file, done_file)
        self.done_file = done_file
        self.cookies_file = cookies_file
        self.root_manga_dir = root_manga_dir
        self.driver_path = driver_path
        self.browser = None
        self.default_display = default_display
        self.timeout = timeout
        self.wait = wait
        self.login = login
        self.password = password
        self.max = _max

    def init_browser(self, headless: Optional[bool] = False) -> None:
        """
        Initializing browser and authenticate if necessary
        Lots of obfuscation via: https://intoli.com/blog/making-chrome-headless-undetectable/
        ---------------------
        param: headless -- bool
            If True: launch browser in headless mode(for download manga)
            If False: launch usually browser with GUI(for first authenticate)
        """
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("headless")
        options.add_argument(f"user-agent={USER_AGENT}")

        self.browser = webdriver.Chrome(
            executable_path=self.driver_path,
            chrome_options=options,
        )

        # Note: not sure if this is actually working, or needs to be called later. Tough to verify.
        customJs = """
        // overwrite the `languages` property to use a custom getter
        Object.defineProperty(navigator, 'languages', {
          get: function() {
            return ['en-US', 'en'];
          },
        });

        // overwrite the `plugins` property to use a custom getter
        Object.defineProperty(navigator, 'plugins', {
          get: function() {
            // this just needs to have `length > 0`, but we could mock the plugins too
            return [1, 2, 3, 4, 5];
          },
        });

        // Spoof renderer checks
        const getParameter = WebGLRenderingContext.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
          // UNMASKED_VENDOR_WEBGL
          if (parameter === 37445) {
            return 'Intel Open Source Technology Center';
          }
          // UNMASKED_RENDERER_WEBGL
          if (parameter === 37446) {
            return 'Mesa DRI Intel(R) Ivybridge Mobile ';
          }

          return getParameter(parameter);
        };
        """

        self.browser.execute_script(customJs)

        if not headless:
            self.__auth()
        self.__set_cookies()
        self.browser.set_window_size(*self.default_display)

    def __set_cookies(self) -> None:
        self.browser.get(LOGIN_URL)
        with open(self.cookies_file, "rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                if "expiry" in cookie:
                    cookie["expiry"] = int(cookie["expiry"])
                    self.browser.add_cookie(cookie)

    def __init_headless_browser(self) -> None:
        """
        Recreating browser in headless mode(without GUI)
        """
        options = Options()
        options.headless = True
        self.browser = webdriver.Chrome(
            executable_path=self.driver_path, chrome_options=options
        )

    def __auth(self) -> None:
        """
        Authentication in browser with GUI for saving cookies in first time
        """
        self.browser.get(LOGIN_URL)
        if not (self.login is None and self.password is None):
            self.browser.find_element_by_id("username").send_keys(self.login)
            self.browser.find_element_by_id("6ccb8078a7").send_keys(self.password)
            self.browser.find_element_by_class_name("js-submit-login").click()

        ready = input("Tab Enter to continue after you login...")
        with open(self.cookies_file, "wb") as f:
            pickle.dump(self.browser.get_cookies(), f)

        self.browser.close()
        # Recreating browser in headless mode for next manga downloading
        self.__init_headless_browser()

    def load_all(self) -> None:
        """
        Just main function which opening each page and save it in .png
        """
        self.browser.set_window_size(*self.default_display)
        if not os.path.exists(self.root_manga_dir):
            os.mkdir(self.root_manga_dir)

        with open(self.done_file, "a") as done_file_obj:
            urls_processed = 0
            for url in self.urls:
                # If `url` is an empty string, skip it.
                if not url.strip():
                    continue

                manga_name = url.split("/")[-1]
                manga_folder = os.sep.join([self.root_manga_dir, manga_name])
                if not os.path.exists(manga_folder):
                    os.mkdir(manga_folder)

                self.browser.get(url)
                self.waiting_loading_page(is_reader_page=False)
                page_count = self.__get_page_count(self.browser.page_source)
                print(f'Downloading "{manga_name}" manga.')
                delay_before_fetching = True  # When fetching the first page, multiple pages load and the reader slows down

                for page_num in tqdm(range(1, page_count + 1)):
                    destination_file = os.sep.join([manga_folder, f"{page_num}.png"])
                    if os.path.isfile(destination_file):
                        delay_before_fetching = True  # When skipping files, the reader will load multiple pages and slow down again
                        continue

                    self.browser.get(f"{url}/read/page/{page_num}")
                    self.waiting_loading_page(
                        is_reader_page=True, should_add_delay=delay_before_fetching
                    )
                    delay_before_fetching = False

                    # Count of leyers may be 2 or 3 therefore we get different target layer
                    n = self.browser.execute_script(
                        "return document.getElementsByClassName('layer').length"
                    )
                    try:
                        # Resizing window size for exactly manga page size
                        width = self.browser.execute_script(
                            f"return document.getElementsByTagName('canvas')[{n-2}].width"
                        )
                        height = self.browser.execute_script(
                            f"return document.getElementsByTagName('canvas')[{n-2}].height"
                        )
                        self.browser.set_window_size(width, height)
                    except JavascriptException:
                        print(
                            "\nSome error with JS. Page source are note ready. You can try increase argument -t"
                        )

                    # Delete all UI and save page
                    self.browser.execute_script(
                        f"document.getElementsByClassName('layer')[{n-1}].remove()"
                    )
                    self.browser.save_screenshot(destination_file)
                print(">> manga done!")
                done_file_obj.write(f"{url}\n")
                urls_processed += 1
                if self.max is not None and urls_processed >= self.max:
                    break

    def load_urls_from_collection(self, collection_url: str) -> None:
        """
        Function which records the manga URLs inside a collection
        """
        self.browser.get(collection_url)
        self.waiting_loading_page(is_reader_page=False)
        page_count = self.__get_page_count_in_collection(self.browser.page_source)
        with open(self.urls_file, "a") as f:
            for page_num in tqdm(range(1, page_count + 1)):
                # Fencepost problem, the first page of a collection is already loaded
                if page_num != 1:
                    self.browser.get(f"{collection_url}/page/{page_num}")
                    self.waiting_loading_page(is_reader_page=False)
                soup = bs(self.browser.page_source, "html.parser")
                for div in soup.find_all("div", attrs={"class": "col-comic"}):
                    f.write(f"{BASE_URL}{div.find('a')['href']}\n")

    def __get_page_count(self, page_source: str) -> int:
        """
        Get count of manga pages from html code
        ----------------------------
        param: page_source -- string
            String that contains html code
        return: int
            Number of manga pages
        """
        print(type(page_source))
        soup = bs(page_source, "html.parser")
        values = soup.find_all('div', class_="table-cell w-full align-top text-left space-y-2 link:text-blue-700 dark:link:text-white")
        pages_info = None
        for val in values:
            try:
                pages_info = val.string.split(' ')
                if pages_info[1] == "pages":
                    break
            except (AttributeError, IndexError):
                continue
        if not pages_info:
            raise ValueError("Page count are not found.")

        # Work-around for 1-page posts
        try:
            return int(pages_info[0])
        except:
            return 1

    def __get_page_count_in_collection(self, page_source: str) -> int:
        """
        Get count of collection pages from html code
        ----------------------------
        param: page_source -- string
            String that contains html code
        return: int
            Number of collection pages
        """
        soup = bs(page_source, "html.parser")
        page_count = 1
        try:
            # Search for page links
            page_links=soup.find_all('a', {'href': re.compile(r"/page/(\d+)")})
 
            # If there are multiple pages...
            if len(page_links) > 0:
                # Find the maximum page number listed in link URLs
                page_count=max([
                        int(re.search(r"\/page\/(\d+)", pg['href']).group(1))
                        for pg in page_links
                    ])
        except Exception as ex:
            print(ex)
        return page_count

    def __get_urls_list(self, urls_file: str, done_file: str) -> List[str]:
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
        with open(done_file, "r") as donef:
            for line in donef:
                done.append(line.replace("\n", ""))

        urls = []
        with open(urls_file, "r") as f:
            for line in f:
                clean_line = line.replace("\n", "")
                if clean_line not in done:
                    urls.append(clean_line)
        return urls

    def waiting_loading_page(
        self,
        is_reader_page: bool = False,
        should_add_delay: bool = False,
    ) -> None:
        """
        Awaiting while page will load
        ---------------------------
        param: is_non_reader_page -- bool
            False -- awaiting of main manga page
            True -- awaiting of others manga pages
        param: should_add_delay -- bool
            False -- the page num != 1
            True -- this is the first page, we need to wait longer to get good quality
        """
        if not is_reader_page:
            sleep(self.wait)
            elem_xpath = "//link[@rel='icon']"
        elif should_add_delay:
            sleep(self.wait * 3)
            elem_xpath = "//div[@data-name='PageView']"
        else:
            sleep(self.wait)
            elem_xpath = "//div[@data-name='PageView']"
        try:
            element = EC.presence_of_element_located((By.XPATH, elem_xpath))
            WebDriverWait(self.browser, self.timeout).until(element)
        except TimeoutException:
            print(
                "\nError: timed out waiting for page to load. + \
                You can try increase param -t for more delaying."
            )
            program_exit()
