import os
import sys
import time
import os.path
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from sys import platform as _platform


class GurlDownSelenium:

    def __init__(self, headless_option):
        self.timed_out_list = []
        self.failed_list = []
        self.url = None
        self.download_location = None
        self.headless = headless_option

    def set_url(self, url):
        self.url = url
        return self

    def set_download_location(self, location):
        self.download_location = location
        if not self.download_location:
            self.download_location = self.get_download_path()

    def download_file(self):
        if os.name == 'nt':
            chrome_path = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
            chrome_driver_path = ".\\chromedriver.exe"
        else:
            chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
            chrome_driver_path = './chromedriver'

        WINDOW_SIZE = "1024,700"

        chrome_options = webdriver.ChromeOptions()
        if self.headless:
            chrome_options.add_argument("--headless")
        if self.download_location:
            prefs = {
                "download.default_directory": self.download_location,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True
            }
            chrome_options.add_experimental_option('prefs', prefs)
        chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
        chrome_options.binary_location = chrome_path

        driver = webdriver.Chrome(executable_path=chrome_driver_path,
                                  chrome_options=chrome_options
                                  )
        # driver.minimize_window()
        driver.get(self.url)

        if self.download_location:
            self.enable_download_in_headless_chrome(driver, self.download_location)
        else:
            self.enable_download_in_headless_chrome(driver, self.get_download_path())

        if not self.is_page_valid(driver):
            self.failed_list.append(self.url)
            driver.quit()
            return
        self.cleanup_download_location()

        # if reached to download page, handle it
        self.handle_download_page(driver)

        # if reached to virus check page, handle it
        self.handle_virus_check_page(driver)

        # wait downloading
        if self.headless:
            state = self.wait_until_download_completed_headless(driver)
        else:
            state = self.wait_until_download_completed(driver)

        if state:
            sys.stdout.write("\rDownload completed, Moving on to the next file")
            sys.stdout.flush()
            print("\r")

        driver.quit()

    def cleanup_download_location(self):
        crd_files = [file for file in os.listdir(self.download_location) if file.endswith("crdownload")]
        try:
            for file in crd_files:
                os.remove(os.path.join(self.download_location, file))
        except PermissionError:
            print("crdlownload is being used {0}".format(file))

    def wait_until_download_completed_headless(self, driver):
        max_time = 60  # 1 min idle timeout
        end_time = time.time() + max_time
        time.sleep(2)
        sum_before = -1

        while True:
            # if download in progress
            sum_after = sum([os.stat(os.path.join(self.download_location, file)).st_size for file in
                             os.listdir(self.download_location)])
            if sum_before != sum_after:
                sum_before = sum_after
                crd_size = sum([os.stat(os.path.join(self.download_location, file)).st_size for file in
                                os.listdir(self.download_location) if file.endswith("crdownload")]) / 1024
                sys.stdout.write("\rDownload Progress {:.2f} KB".format(crd_size))
                sys.stdout.flush()
                end_time = time.time() + max_time  # time out extend

            time.sleep(0.5)
            crd_size = [os.stat(os.path.join(self.download_location, file)).st_size for file in
                        os.listdir(self.download_location) if
                        file.endswith("crdownload")]

            if len(crd_size) == 0:
                return True

            if time.time() > end_time:
                self.timed_out_list.append(self.url)
                print('Download timed out')
                return False

    def wait_until_download_completed(self, driver):
        max_time = 60  # 1분 timeout
        driver.execute_script("window.open()")
        # switch to new tab
        driver.switch_to.window(driver.window_handles[-1])
        # navigate to chrome downloads
        driver.get('chrome://downloads')
        # define the end_time
        end_time = time.time() + max_time
        while True:
            try:
                # get the download percentage
                status, progress = self.get_top_download_state(driver)

                if status == 'COMPLETE':
                    return True
                elif status == 'IN_PROGRESS':
                    sys.stdout.write("\rDownload Progress {0}".format(progress))
                    sys.stdout.flush()
                    end_time = time.time() + max_time
                elif status == 'PAUSED':
                    sys.stdout.write("\rPaused..")
                    sys.stdout.flush()
                    end_time = time.time() + max_time  # timeout extend
                elif status == 'INTERRUPTED':
                    sys.stdout.write("\rInterrupted! Wait...")
                    sys.stdout.flush()
                elif status == 'CANCELLED':
                    print("Cancelled")
                    self.failed_list.append(self.url)
                    return False
            except:
                pass
            # wait for 1 second before checking the percentage next time
            time.sleep(1)
            # exit method if the download not completed with in MaxTime.
            if time.time() > end_time:
                self.timed_out_list.append(self.url)
                print('Download timed out')
                return False

    def save_log(self):
        if len(self.failed_list) > 0:
            f = open("failed.txt", "w+")
            f.write("\n".join(self.failed_list))

        if len(self.timed_out_list) > 0:
            f = open("timed_out.txt", "w+")
            f.write("\n".join(self.timed_out_list))

    @staticmethod
    def handle_virus_check_page(driver):

        for handle in driver.window_handles:
            driver.switch_to_window(handle)
            if driver.title == 'Google Drive - Virus scan warning':
                try:
                    driver.find_element_by_id("uc-download-link").click()
                    return
                except NoSuchElementException:
                    print("Download link not found, continue..")
        print('Virus check page not reached')

    @staticmethod
    def handle_download_page(driver):

        if driver.title.find("- Google Drive") != -1:
            try:
                driver.find_elements_by_xpath("//*[contains(text(), 'Download')]")[0].click()
            except NoSuchElementException:
                print("Download Button not found by css_selector, continue..")

    @staticmethod
    def is_page_valid(driver):

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

    # https://stackoverflow.com/questions/45631715/downloading-with-chrome-headless-and-selenium
    @staticmethod
    def enable_download_in_headless_chrome(driver, download_dir):
        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd': 'Page.setDownloadBehavior',
                  'params': {'behavior': 'allow', 'downloadPath': download_dir}}
        command_result = driver.execute("send_command", params)

    @staticmethod
    def get_top_download_state(driver):
        """Call this after running driver.get("chrome://downloads")."""

        [state, progress] = driver.execute_script("""
        var item = downloads.Manager.get().items_[0];
        var state = item.state;        
        var progress = item.progressStatusText;
        return [state, progress];
        """)

        return state, progress

    @staticmethod
    def get_download_path():
        """Returns the default downloads path for linux or windows"""
        if _platform == "win32" or _platform == "win64":
            import winreg
            sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
            downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                location = winreg.QueryValueEx(key, downloads_guid)[0]
            return location
        elif _platform == "darwin":
            return os.path.join(os.path.expanduser('~'), 'downloads')
        elif _platform == "linux" or _platform == "linux2":
            return os.path.join(os.path.expanduser('~'), 'Downloads')
