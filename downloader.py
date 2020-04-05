import os

from shutil import rmtree
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup as bs
from tqdm import tqdm


# Initial display settings for headless browser. Any manga in this
# resolution will be opened correctly and with the best quality.
MAX_DISPLAY_SETTINGS = [1440, 2560]
# Path to headless driver
EXEC_PATH = 'chromedriver.exe'
# Root directory for manga downloader
ROOT_MANGA_DIR = 'manga'
# Timeout to page loading in seconds
TIMEOUT = 1
 

def program_exit():
    print('Program exit.')
    exit()

By.CSS_SELECTOR

class FDownloader():
    """
    Class which allows download manga. 
    The main idea of download - using headless browser and just saving
    screenshot from that. Because canvas in fakku.net is protected
    from download via simple .toDataURL js function etc.
    """
    def __init__(self,
        urls_file, 
        driver_path=EXEC_PATH, 
        default_display=MAX_DISPLAY_SETTINGS,
        timeoot=TIMEOUT):
        """
        param: urls_file -- string name of .txt file with urls 
            Contains list of manga urls, that's to be downloaded
        param: driver_path -- string
            Path to the headless driver
        param: default_display -- list of two int (width, height)    
            Initial display settings. After loading the page, they will be changed
        param: timeout -- int
            Timeout in seconds beetween pages downloading. 
            If <1 may be poor quality.
        """
        self.urls = self.__get_urls_list(urls_file)
        options = Options()
        options.headless = True
        self.browser = webdriver.Chrome(
            executable_path=driver_path,
            chrome_options=options)
        self.browser.set_window_size(*default_display)
        self.timeout = timeoot


    def auth(self, login, password):
        pass


    def load_all(self):
        """
        Just main function witch opening each page and save it in .png
        """
        if not os.path.exists(ROOT_MANGA_DIR):
            os.mkdir(ROOT_MANGA_DIR)
        for url in self.urls:
            manga_name = url.split('/')[-1]
            manga_folder = f'{ROOT_MANGA_DIR}\\{manga_name}'
            if not os.path.exists(manga_folder):
               os.mkdir(manga_folder)
            self.browser.get(url)
            self.waiting_loading_page(is_main_page=True)
            page_count = self.__get_page_count(self.browser.page_source)
            print(f'Downloading "{manga_name}" manga.')
            for page_num in tqdm(range(1, page_count + 1)):
                self.browser.get(f'{url}/read/page/{page_num}')
                self.waiting_loading_page(is_main_page=False)

                # Resizing window size for exactly manga page size
                width = self.browser.execute_script("return document.getElementsByTagName('canvas')[1].width")
                height = self.browser.execute_script("return document.getElementsByTagName('canvas')[1].height")
                self.browser.set_window_size(width, height)

                # Delete all UI
                self.browser.execute_script("document.getElementsByClassName('layer')[2].remove()")
                self.browser.save_screenshot(f'{manga_folder}\\{page_num}.png')
            print('>> manga done!')


    def __get_page_count(self, page_source):
        """
        param: page_sourse -- string
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


    def __get_urls_list(self, urls_file):
        """
        Get list of urls from .txt file
        param: urls_file -- string
            Name or path of .txt file with manga urls
        return: urls -- list
            List of urls from urls_file
        """
        urls = []
        with open(urls_file, 'r') as f:
            for line in f:
                urls.append(line.replace('\n',''))
        return urls        


    def waiting_loading_page(self, is_main_page=True):
        """
        Awaiting while page will load
        param: is_main_page -- bool
            False -- awaiting of main manga page
            True -- awaiting of others manga pages
        """
        if is_main_page:
            elem_xpath = "//link[@type='image/x-icon']"
        else:
            sleep(self.timeout)
            elem_xpath = "//div[@data-name='PageView']"
        try:
            element = EC.presence_of_element_located((By.XPATH, elem_xpath))
            WebDriverWait(self.browser, TIMEOUT).until(element)
        except TimeoutException:
            print('Error: timed out waiting for page to load.')
            program_exit()


