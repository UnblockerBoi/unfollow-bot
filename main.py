from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time
import sys
import json

username = ""
password = ""
exclude: list[str] = []


def load_exclusions(file_path):
    global exclude
    with open(file_path, "r") as file:
        names = file.readlines()
    exclude = [name.strip() for name in names]


def load_credentials(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def login(driver: WebDriver):
    # wait until username field is available then enter username
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        driver.find_element(by=By.NAME, value="username").send_keys(username)
    except:
        print("Error with username field on login")
        sys.exit(1)
    print("Username entered successfully")

    # wait untill password field is available then enter password
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        # This is really strange, after entering the first character of the
        # password field, the cursor jumps back to the username field
        # we need to bypass this behavior by first entering the first character
        # then entering the rest of the password
        driver.find_element(by=By.NAME, value="password").send_keys(str(password[0]))
        driver.find_element(by=By.NAME, value="password").send_keys(password[1:])
        driver.find_element(by=By.NAME, value="password").send_keys("\ue007")
    except:
        print("Error with password field on login")
        sys.exit(1)
    print("Password entered successfully")


def click_button_css(driver, css, desc):
    try:
        element = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css))
        )
        element.click()
    except:
        print(f'button "{desc}" not found.')


def click_button_xpath(driver, xpath, desc):
    try:
        element = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        element.click()
    except:
        print(f'button "{desc}" not found.')


def navigate_to_profile(driver):
    # save login info
    login_popup_css = '[class*="_acan _acap _acas _aj1- _ap30"]'

    # click past the notification popup
    notif_css = '[class*="_a9-- _ap36 _a9_1"]'

    # click the link to the profile
    profile_css = '[href*="' + username + '"]'

    click_button_css(driver, login_popup_css, "Save Login Info")
    click_button_css(driver, notif_css, "Turn on Notifications")
    click_button_css(driver, profile_css, f"{username}'s Profile")


def get_followers(driver: WebDriver):

    # various css and xpath identifiers
    followers_css = '[href*="' + username + '/followers/"]'
    scroll_box_xpath = "/html/body/div[6]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]"
    username_css = '[class*="_ap3a _aaco _aacw _aacx _aad7 _aade"]'
    close_css = '[aria-label="Close"]'

    # click the followers button to open the followers dialog
    click_button_css(driver, followers_css, f"{username}'s followers")

    time.sleep(2)

    # find the scroll box and scroll to the bottom
    scroll_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, scroll_box_xpath))
    )
    scroll(driver, scroll_box)

    list_elems = scroll_box.find_elements(by=By.CSS_SELECTOR, value=username_css)
    users = [elem.text for elem in list_elems]

    # close out of the followers list
    click_button_css(driver, close_css, "Close followers")

    return users


def get_following(driver: WebDriver):

    # various css and xpath identifiers
    scroll_box_xpath = "/html/body/div[6]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[4]"
    following_css = '[href*="' + username + '/following/"]'
    username_css = '[class*="_ap3a _aaco _aacw _aacx _aad7 _aade"]'
    close_css = '[aria-label="Close"]'

    # click the following button to open the following dialog
    click_button_css(driver, following_css, f"{username}'s following")

    time.sleep(2)

    # find the scroll box and scroll to the bottom
    scroll_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, scroll_box_xpath))
    )
    scroll(driver, scroll_box)

    list_elems = scroll_box.find_elements(by=By.CSS_SELECTOR, value=username_css)

    users = [elem.text for elem in list_elems]

    # close out of the following list
    click_button_css(driver, close_css, "Close")

    return users


def scroll(driver: WebDriver, scroll_box: WebElement):
    last_ht, ht = 0, 1
    while last_ht != ht:
        last_ht = ht
        time.sleep(2.5)
        ht = driver.execute_script(
            """
        arguments[0].scrollTo(0, arguments[0].scrollHeight);
        return arguments[0].scrollHeight;
        """,
            scroll_box,
        )
    time.sleep(2)


def run():
    global password

    print("Loading exclusions")
    load_exclusions("exclude.txt")
    print("Successfully loaded exclusions")

    print("Getting Credentials")
    credentials = load_credentials("credentials.json")
    password = credentials.get(username)

    if password is "":
        print(f'ERROR: password not found for username: "{username}"')
        sys.exit(1)
    else:
        print("Successfully received password")

    # goto insta login page
    driver = webdriver.Safari()
    driver.set_window_size(1400, 800)
    driver.get("https://www.instagram.com/accounts/login/")

    # attempt to login
    login(driver)
    print("Successfull Login")

    # go to your profile
    navigate_to_profile(driver)
    print("Successfully navigated to Profile")

    # get your followers
    who_follows_you = get_followers(driver)
    print(
        f"Successfully found all {len(who_follows_you)} followers. Writing them to 'followers.txt'"
    )
    with open("followers.txt", "w") as file:
        file.writelines(name + "\n" for name in who_follows_you)

    # get your following
    who_you_follow = get_following(driver)
    print(
        f"Successfully found all {len(who_you_follow)} followings. Writing them to 'followings.txt'"
    )
    with open("followings.txt", "w") as file:
        file.writelines(name + "\n" for name in who_you_follow)

    print("Exiting the web now")
    # exit instagram
    driver.quit()

    followers = set(who_follows_you)
    following = set(who_you_follow)
    exclude_set = set(exclude)

    snakes = list(following - followers - exclude_set)
    un_followed_back = list(followers - following)

    print("Publishing results")
    with open("snakes.txt", "w") as file:
        file.writelines(name + "\n" for name in snakes)
    with open("un_followed_back.txt", "w") as file:
        file.writelines(name + "\n" for name in un_followed_back)

    print("Finished")


if __name__ == "__main__":
    run()
