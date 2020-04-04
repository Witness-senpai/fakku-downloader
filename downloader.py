from time import sleep
from selenium import webdriver

URL = 'https://www.fakku.net/hentai/just-a-moment-english/read/page/1'
# Initial display settings for phantomjs browser. Any manga in this
# resolution will be opened correctly and with the best quality.
MAX_DISPLAY_SETTINGS = [1440, 2560]
# Path to phantomjs.exe
EXEC_PATH = 'chromedriver.exe'


class FDownloader():
    """
    Class which allows download manga. 
    The main idea of download - using headless browser and just saving
    screenshot from that. Because canvas in fakku.net is protected
    from download via simple .toDataURL js function etc.
    """
    def __init__(self, urls, driver_path=EXEC_PATH, default_display=MAX_DISPLAY_SETTINGS):
        """
        param: urls -- list of string 
            List of manga urls, that's to be downloaded
        param: exec_path -- string
            Path to the PhantomJS folder
        """
        self.urls = urls
        options = Options()
        options.headless = True
        self.browser = webdriver.Chrome(executable_path=driver_path,
            chrome_options=options)
        self.browser.set_window_size(*default_display)


    def auth(self, login, password):
        pass


    def load_all(self):
        for url in self.urls:
            
            
