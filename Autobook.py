a = " "
import time
from token import EXACT_TOKEN_TYPES
import chromedriver_autoinstaller
chromedriver_autoinstaller.install()
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
# Selenium Options
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from typing import Union, Tuple, Optional

class Booker:
    """
    Booker is used to automatically book class rooms using TimeEdit
    """
    def __init__(self, 
                username: str, 
                password: str,
                start_time:str="10",
                end_time:str="15",
                headless: bool = True,
                room:str="NAT.A1.321",
                msg:str=""):
        """
        :param username: Username to login with
        :param password: Password to login with
        :param headless: Run in headless mode
        """
        self.sleep_duration = 0.2
        self.username = username
        self.password = password
        self.headless = headless
        self.room = room
        self.start_time = start_time
        self.end_time = end_time
        self.msg = msg
        self.init = True
        self.booked_dates = []
        assert isinstance(self.username, str)
        assert isinstance(self.password, str)
        assert isinstance(self.headless, bool)
        assert isinstance(self.room, str)
        assert isinstance(self.start_time, str) and self.start_time.isdigit(), "Start time must be a string of digits"
        assert isinstance(self.end_time, str) and end_time.isdigit(), "End time must be a number"
        assert int(self.start_time) < int(self.end_time), "Start time must be before end time. Note! CET 24:00 is 00:00"
        self.driver = self._setup_driver()
        self._login()
        self._set_up_page()
    def _setup_driver(self) -> webdriver.Chrome:
        """
        Setup the driver
        :return: Driver
        """
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
        driver.get("https://cloud.timeedit.net/umu/web/studres2/")
        return driver
    def _login(self):
        login_field = self.driver.find_element(By.XPATH, "//a[contains(text(),'Logga in med Umu-id')]")
        login_field.click()
        # Input username
        username_field = self.driver.find_element(By.ID, "userNameInput")
        username_field.send_keys(self.username)
        # Input password
        password_field = self.driver.find_element(By.ID, "passwordInput")
        password_field.send_keys(self.password)
        # Click login
        login_button = self.driver.find_element(By.ID, "submitButton")
        login_button.click()
        # Click Group room link
    def _set_up_page(self):
        link = self.driver.find_element(By.XPATH, '//*[@id="contents"]/div[2]/div[5]/div[1]/div[3]/a[2]/div/h2')
        link.click()
        # Search for room
        time.sleep(self.sleep_duration)
        search = self.driver.find_element(By.XPATH, "//*[@class='objectinput objectinputtext']")
        # Clear search bar
        time.sleep(self.sleep_duration)
        search.clear()
        search.send_keys(self.room)
        # Click search button
        time.sleep(self.sleep_duration)
        search_button = self.driver.find_element(By.XPATH, "//*[@class='objectinputsearchbutton objectinputsearchbuttonSecond']")
        search_button.click()
        # Select day calendar
        time.sleep(self.sleep_duration)
        day_button = self.driver.find_element(By.XPATH,'//*[@class = "weekZoomFirst weekZoomDay clickable"]')
        day_button.click()
    
    def book_all(self)->int:
        """
        Book all available times
        :return: Number of times booked
        """
        at_end = False
        booked = 0
        while not at_end:
            time.sleep(self.sleep_duration) # Wait for page to load
            self._date = self.driver.find_element(By.XPATH,'//*[@id="leftresdateurl"]').get_property("value")
            elements = self.driver.find_elements(By.CLASS_NAME, "weekDiv")
            comp_book = False
            for element in elements:
                # try:
                #     date = element.get_attribute("data-dates")
                # except:
                #     continue
                if element.is_displayed():
                    date = element.get_attribute("data-dates")
                else:
                    continue
                if date == self._date:
                    width = element.size["width"]
                    ActionChains(self.driver).move_to_element_with_offset(element, width//2-10, 0).click().perform()
                    time.sleep(self.sleep_duration)
                    comp_book = self._book()
                    if comp_book:
                        booked += 1
                        self.booked_dates.append(self._date)            
                    self._close_window()
                    # try:
                    #     ActionChains(self.driver).move_to_element_with_offset(element, width//2-10, 0).click().perform()
                    #     time.sleep(self.sleep_duration)
                    #     comp_book = self._book()
                    #     if comp_book:
                    #         booked += 1
                    #         self.booked_dates.append(self._date)            
                    #     self._close_window()
                    #     # try:
                    #     #     comp_book = self._book()
                    #     # except Exception as e:
                    #     #     # TODO: FIgure out what cases this might occure.
                    #     #     print(f"Mid Book Error : {e}")
                    #     #     if not comp_book: # If the booking failed there is probably a popup window that has to be closed.
                    #     #         self._close_window()
                    # except Exception as e:
                    #     print(f"Could not press bar for date: {date}")
                    # TODO: Send message to bocker that the specified date has been booked.
                    # For now print message to terminal.
                    print(f"{'Completed' if comp_book else 'Failed'} to book: {date}")
                    booked += 1 if comp_book else 0
                    break # Move on to the next date.
                    
            # Check if at end
            next_date_button = self.driver.find_element(By.XPATH,'//*[@id="leftresdateinc"]')
            next_date_button.click()
            time.sleep(self.sleep_duration)
            new_date = self.driver.find_element(By.XPATH,'//*[@id="leftresdateurl"]').get_property("value")
            if new_date == self._date:
                at_end = True
        return booked
    def _set_interval(self)->bool:
        # try:
        time_start_list = self.driver.find_element(By.XPATH,("//select[@class = 'timedrop timeHourStart']"))
            # assert time_start_list is not None and time_start_list.is_displayed(), "Time start list is not displayed"
        if time_start_list is not None and time_start_list.is_displayed():
            time_start_list.click()
        else:
            return False
        # except Exception as e:
        #     print(f"Error: {e}")
        # Set start hour
        time_start_list.send_keys(self.start_time)
        time_start_list.send_keys(Keys.RETURN)
        time_start_minute = self.driver.find_element(By.XPATH,("//select[@class = 'timedrop timeMinuteStart']"))
        time_start_minute.send_keys("15") # Always 15 minutes, academic time
        # time_start_minute.send_keys(Keys.RETURN)
        time_end_list = self.driver.find_element(By.XPATH,("//select[@class = 'timedrop timeHourEnd']"))
        time_end_list.send_keys(self.end_time)
        # time_end_list.send_keys(Keys.RETURN)
        time_end_minute = self.driver.find_element(By.XPATH,("//select[@class = 'timedrop timeMinuteEnd']"))
        time_end_minute.send_keys("00") # Always 00 minutes, academic time
        # time_end_minute.send_keys(Keys.RETURN)
        return True # Success
    def _set_institution(self):
        # Set the institution
        search_classes = self.driver.find_elements(By.XPATH, '//*[@class = "resobjectsearch hasClick"]')
        for cls in search_classes:
            if cls.text.startswith("Insti"):
                cls.click()
                time.sleep(self.sleep_duration)
                inst_list =self.driver.find_element(By.XPATH,("//*[@class = 'infotable infotablenormal']"))
                time.sleep(self.sleep_duration)
                inst_list.click()
                self.init = False
    def _book(self)->bool:
        """
        Book a single time
        :return: True if booked, False if not
        """
        if self.init:
            self._set_institution()
        success = self._set_interval() # Set the interval that we want to book
        if not success:
            return False
        time.sleep(self.sleep_duration)
        # self._set_institution()
        # Add description of the booking
        public_comment =self.driver.find_element(By.XPATH, '//*[@class = "reset editfield niceinput resinputfield"]')
        public_comment.clear()
        public_comment.send_keys(self.msg)
        book_button = self.driver.find_element(By.XPATH,'//*[@class="continueRes greenbutton greenbottom"]')
        book_button.click()
        time.sleep(self.sleep_duration+0.2)
        if book_button.is_displayed():
            return False
        # self._close_window()
        return True
    def _close_window(self):
        close_button = self.driver.find_element(By.XPATH,'//*[@class="topclose"]')
        if close_button.is_displayed():
            close_button.click()
        else:
            close_button = self.driver.find_element(By.XPATH,'//*[@id="fancybox-close"]')
            if close_button.is_displayed():
                close_button.click()
    def display_booked_dates(self):
        print("Dates booked:")
        for date in self.booked_dates:
            # The date is an int in the format YYYYMMDD
            year = date[:4]
            month = date[4:6]
            day = date[6:]
            print(f"{day}/{month}/{year} time: {self.start_time}-{self.end_time}")
    def pause(self):
        input("Press any key to continue...")
    def close(self):
        self.driver.close()
    def __del__(self):
        self.driver.close()
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()
    def __enter__(self):
        return self
    def __str__(self):
        return f"Booker: {self.username}"
    def __repr__(self):
        return f"Booker: {self.username}"        
if __name__=="__main__":
    b = Booker(username="*****",
        password="*****",
        start_time="16",end_time="17",
        msg="43616e2774206265617420757321202354460d0a0d0a0d0a",
        headless=False)
    b.book_all()
    b.display_booked_dates()
    b.pause()
    b.close()