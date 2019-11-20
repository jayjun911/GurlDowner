import os
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options


class GurlDownSelenium:

    def __init__(self):
        self.url = None

    def set_url(self, url):
        self.url = url
        return self

    def download_file(self):
        if os.name == 'nt':
            chrome_path = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
            chrome_driver_path = ".\\chromedriver.exe"
        else:
            chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
            chrome_driver_path = './chromedriver'

        WINDOW_SIZE = "1024,768"

        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
        chrome_options.binary_location = chrome_path

        driver = webdriver.Chrome(executable_path=chrome_driver_path,
                                  chrome_options=chrome_options
                                  )
        driver.get(self.url)
        if driver.title == 'Not Found':
            print("File doesn't exist! Continuing with next request...\n")
        elif driver.title == 'Google Drive - Virus scan warning':
            driver.find_element_by_id("uc-download-link").click()
            self.wait_until_download_completed(driver)
            print("Done. Bring the next file on!\n")
        elif driver.title == '':
            print("Done. Bring the next file on!\n")
        else:
            try:
                error_code = driver.find_element_by_class_name("error-code")
                print(error_code.Text + " moving on to the next request")
            except NoSuchElementException:
                print('Reached the page {0}. Download not successful, moving on'.format(driver.title))

        driver.quit()

    def wait_until_download_completed(self, driver):
        maxTime = 600  # 10분 timeout
        driver.execute_script("window.open()")
        # switch to new tab
        driver.switch_to.window(driver.window_handles[-1])
        # navigate to chrome downloads
        driver.get('chrome://downloads')
        # define the endTime
        endTime = time.time() + maxTime
        while True:
            try:
                # get the download percentage
                downloadPercentage = driver.execute_script(
                    "return document.querySelector('downloads-manager').shadowRoot.querySelector('#downloadsList downloads-item').shadowRoot.querySelector('#progress').value")
                # check if downloadPercentage is 100 (otherwise the script will keep waiting)
                if downloadPercentage == 100:
                    # exit the method once it's completed
                    return downloadPercentage
            except:
                pass
            # wait for 1 second before checking the percentage next time
            time.sleep(1)
            # exit method if the download not completed with in MaxTime.
            if time.time() > endTime:
                break