from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time


class Bot:
    """
    Class holds all of the bot functionality
    """

    def __init__(self, username: str, password: str, exclusions: list[str]):
        self.username: str = username
        self.password: str = password
        self.exclusions: list[str] = exclusions
        self.followers: list[str] = []
        self.following: list[str] = []
        self.you_do_not_follow_back: list[str] = []
        self.do_not_follow_you_back: list[str] = []
        self.driver: WebDriver

        # Navigational strings
        self.insta_login_url = "https://www.instagram.com/accounts/login/"
        self.save_login_info_xpath = "//button[contains(text(), 'Save info')]"
        self.notifications_xpath = "//button[contains(text(), 'Not Now')]"
        self.profile_css = '[href*="' + self.username + '"]'
        self.followers_css = '[href*="' + self.username + '/followers/"]'
        self.followers_scroll_box_xpath = "/html/body/div[6]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]"
        self.scroll_js = """
            arguments[0].scrollTo(0, arguments[0].scrollHeight);
            return arguments[0].scrollHeight;
            """
        self.scroll_box_user_css = '[class*="_ap3a _aaco _aacw _aacx _aad7 _aade"]'
        self.close_button_css = '[aria-label="Close"]'
        self.following_css = '[href*="' + self.username + '/following/"]'
        self.following_scroll_box_xpath = "/html/body/div[6]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[4]"

    def run(self):
        """
        runs the bot from start to finish
        """

        # Open a safari window and navigate to insta
        self.driver = webdriver.Safari()
        self.driver.set_window_size(1400, 800)
        self.driver.get(self.insta_login_url)

        # attempt to login
        self.login()
        print("Successfull Login")

        # click past the 'save login info' pop up
        self.click_button_xpath(self.save_login_info_xpath)
        print("Successfully clicked past save login info popup")

        # click past the 'turn on notifications pop up'
        self.click_button_xpath(self.notifications_xpath)
        print("Successfully clicked past notifications popup")

        # navigate to profile
        self.click_button_css(self.profile_css)
        print("Successfully navigated to profile")

        # get all followers, store in self.followers
        self.get_followers()
        print(f"Successfully found all {len(self.followers)} followers")

        # close out of followers dialog
        self.click_button_css(self.close_button_css)
        print("Successfully closed out of followers dialog")

        # get entire following, store in self.following
        self.get_following()
        print(f"Successfully found all {len(self.following)} followings")

        # exit Instagram
        self.driver.quit()
        print("Exiting Instagram")

        # copmpute compute
        self.compute_results()
        print("Computing reults")

        # export reults

        print("Exporting results")
        self.export_results()

    def login(self):
        """
        functinon attepts to login using the username and password fields
        """

        print("Attempting to enter username")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        self.driver.find_element(by=By.NAME, value="username").send_keys(self.username)
        print("Username entered successfully")

        print("Attempting to enter password")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        # This is really strange, after entering the first character of the
        # password field, the cursor jumps back to the username field
        # we need to bypass this behavior by first entering the first character
        # then entering the rest of the password
        self.driver.find_element(by=By.NAME, value="password").send_keys(
            str(self.password[0])
        )
        self.driver.find_element(by=By.NAME, value="password").send_keys(
            self.password[1:]
        )
        self.driver.find_element(by=By.NAME, value="password").send_keys("\ue007")
        print("Password entered successfully")

    def click_button_css(self, css: str):
        """
        Attepts to clicks the button specified by 'css' parameter
        """
        element = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css))
        )
        element.click()

    def click_button_xpath(self, xpath: str):
        """
        Attepts to click the button specified by 'xpath' parameter
        """
        element = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        element.click()

    def get_followers(self):
        """
        Attempts to get all followers by scrolling through entire followers
        list
        """

        # open followers dialog
        self.click_button_css(self.followers_css)

        time.sleep(2)

        # find the scroll box and scroll to the bottom
        scroll_box = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, self.followers_scroll_box_xpath))
        )
        self.scroll(scroll_box)

        # collect all of the user once we've loaded them all in through scrolling
        list_elems = scroll_box.find_elements(
            by=By.CSS_SELECTOR, value=self.scroll_box_user_css
        )

        # store in class attribute
        self.followers = [elem.text for elem in list_elems]

    def scroll(self, scroll_box: WebElement):
        """
        scrolls to the bottom of the followers and following dialogs
        """
        last_ht, ht = 0, 1
        while last_ht != ht:
            last_ht = ht
            time.sleep(2.5)
            ht = self.driver.execute_script(
                self.scroll_js,
                scroll_box,
            )
        time.sleep(2)

    def get_following(self):
        """
        Attempts to get entire following by scrolling through entire following
        list
        """

        # open following dialog
        self.click_button_css(self.following_css)

        time.sleep(2)

        # find the scroll box and scroll to the bottom
        scroll_box = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, self.following_scroll_box_xpath))
        )
        self.scroll(scroll_box)

        # collect all of the user once we've loaded them all in through scrolling
        list_elems = scroll_box.find_elements(
            by=By.CSS_SELECTOR, value=self.scroll_box_user_css
        )

        # store in class attribute
        self.following = [elem.text for elem in list_elems]

    def compute_results(self):
        """
        finds list of those who don't follow you and list of people you
        don't follow back
        """

        followers_set = set(self.followers)
        following_set = set(self.following)
        exclusions_set = set(self.exclusions)

        self.do_not_follow_you_back = list(
            following_set - followers_set - exclusions_set
        )

        self.you_do_not_follow_back = list(followers_set - following_set)

    def export_results(self):
        """
        Exports reults to .txt files
        """
        with open("doesn't-follow-you-back.txt", "w", encoding="utf-8") as file:
            file.writelines(name + "\n" for name in self.do_not_follow_you_back)
        with open("you-don't-follow-back.txt", "w", encoding="utf-8") as file:
            file.writelines(name + "\n" for name in self.you_do_not_follow_back)
