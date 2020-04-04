import os

from shutil import rmtree
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs

URL = 'https://www.fakku.net/hentai/just-a-moment-english'
# Initial display settings for phantomjs browser. Any manga in this
# resolution will be opened correctly and with the best quality.
MAX_DISPLAY_SETTINGS = [1440, 2560]
# Path to phantomjs.exe
EXEC_PATH = 'chromedriver.exe'
# Root directory for manga downloader
ROOT_MANGA_DIR = 'manga'


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
    def __init__(self, urls_file, driver_path=EXEC_PATH, default_display=MAX_DISPLAY_SETTINGS):
        """
        param: urls -- list of string 
            List of manga urls, that's to be downloaded
        param: exec_path -- string
            Path to the headless driver
        """
        self.urls = self.__get_urls_list(urls_file)
        options = Options()
        options.headless = True
        self.browser = webdriver.Chrome(executable_path=driver_path,
            chrome_options=options)
        self.browser.set_window_size(*default_display)


    def auth(self, login, password):
        pass


    def load_all(self):
        try:
            os.mkdir(ROOT_MANGA_DIR)
        except FileExistsError:
            print(f'Folder {ROOT_MANGA_DIR} are already exist and will be overwriten, continue?(y/n)')
            response = input('>> ')
            if 'y' in response: 
                rmtree(ROOT_MANGA_DIR)
                os.mkdir(ROOT_MANGA_DIR)
            else:
                print('Program exit.')
                exit()
        for url in self.urls:
            manga_name = url.split('/')[-1]
            manga_folder = ROOT_MANGA_DIR + '\\' + manga_name
            os.mkdir(manga_folder)
            self.browser.get(url)
            sleep(4)
            page_count = self.__get_page_count(self.browser.page_source)
            print(f'Detect "{manga_name}" manga.')
            for page_num in range(1, page_count + 1):
                self.browser.get(f'{url}/read/page/{page_num}')
                sleep(1)
                width = self.browser.execute_script("return document.getElementsByTagName('canvas')[1].width")
                height = self.browser.execute_script("return document.getElementsByTagName('canvas')[1].height")
                self.browser.set_window_size(width, height)
                # Delete all UI
                self.browser.execute_script("document.getElementsByClassName('layer')[2].remove()")
                self.browser.save_screenshot(f'{manga_folder}\\{page_num}.png')
                print(f'{page_num}/{page_count}: page done')
            print('manga done!')


    def __get_page_count(self, page_source):
        """
        param: page_sourse -- string
            String that contains html code
        return: int
            Number of manga pages
        """
        soup = bs(page_source, 'html.parser')
        page_count = None
        while not page_count:
            try:
                page_count = int(soup.find_all('div', attrs={'class': 'row'})[5]
                    .find('div', attrs={'class': 'row-right'}).text
                    .split(' ')[0])
            except Exception as ex:
                print(ex)
        return page_count


    def __get_urls_list(self, urls_file):
        """
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


    def __page_is_ready(self):
        pass


