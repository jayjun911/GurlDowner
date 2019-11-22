import os
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait


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

        if not self.is_page_valid(driver):
            return

        # if reached to download page, handle it
        self.handle_download_page(driver)

        # if reached to virus check page, handle it
        self.handle_virus_check_page(driver)

        # wait downloading
        self.wait_until_download_completed(driver)
        print("Done. Bring the next file on!\n")

        driver.quit()

    def handle_virus_check_page(self, driver):

        for handle in driver.window_handles:
            driver.switch_to_window(handle)
            if driver.title == 'Google Drive - Virus scan warning':
                try:
                    driver.find_element_by_id("uc-download-link").click()
                    return
                except NoSuchElementException:
                    print("Download link not found, continue..")
        print('Virus check page not reached')


    def handle_download_page(self, driver):

        if driver.title.find("- Google Drive") != -1:
            try:
                driver.find_elements_by_xpath("//*[contains(text(), 'Download')]")[0].click()
            except NoSuchElementException:
                print("Download Button not found by css_selector, continue..")

    def is_page_valid(self, driver):

        # page title says Not Found return
        if driver.title == 'Not Found':
            print("Page Not Found: moving on to the next request...\n")
            return False

        # if error-code object is seen return false
        try:
            error_code = driver.find_element_by_class_name("error-code")
            print("Err: " + error_code.Text + " moving on to the next request\n")
        except NoSuchElementException:
            pass

        # if loaded empty page
        if driver.title == '':
            print("Reached empty page. moving on to the next request!\n")

        return True


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