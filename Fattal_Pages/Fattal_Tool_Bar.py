from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import TimeoutException, StaleElementReferenceException
import logging

class FattalToolBar:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def logo_mainpage(self):
        """Try clicking the homepage logo, or fallback to reload."""
        try:
            self.wait = WebDriverWait(self.driver, 5)
            logo = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='/'] img"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", logo)
            self.driver.execute_script("arguments[0].click();", logo)
            logging.info("🏠 Clicked homepage logo successfully.")
        except Exception as e:
            logging.warning(f"❌ Failed to click homepage logo: {e}")
            logging.info("🔁 Reloading homepage manually...")
            self.driver.get("https://www.fattal.co.il")

    def customer_support(self):
        link = self.driver.find_element(By.CSS_SELECTOR, 'a.sc-d3198970-0.MBsfR')
        self.driver.execute_script("arguments[0].click();", link)
        return link

    def currency_button(self):
        currency = self.driver.find_element(By.CSS_SELECTOR, 'button.sc-b9bbe4b8-5')
        currency.click()

    def contact_button(self):
        contact = self.driver.find_element(By.CSS_SELECTOR, 'button.sc-b9bbe4b8-5.gGCgzS')
        contact.click()

    def hotels_israel(self):
        self.driver.find_element(By.XPATH, "//button[text()='מלונות בישראל']").click()

    def hotels_europe(self):
        self.driver.find_element(By.XPATH, "//button[text()='מלונות באירופה']").click()

    def our_brands(self):
        self.driver.find_element(By.XPATH, "//button[text()='המותגים שלנו']").click()

    def club_fattal(self):
        self.driver.find_element(By.XPATH, "//button[text()='מועדון פתאל וחברים']").click()

    def club_info(self):
        self.driver.find_element(By.CSS_SELECTOR, 'button.sc-ffcf4f64-10.jkZJWV').click()

    def deals_packages(self):
        self.driver.find_element(By.XPATH, "//button[text()='דילים וחבילות']").click()

    def fattal_gift(self):
        self.driver.find_element(By.CSS_SELECTOR, 'a.sc-3edcab97-9.dkgkdj').click()

    def more_button(self):
        self.driver.find_element(By.CSS_SELECTOR, 'button.sc-3edcab97-8.grLZGu').click()

    def personal_zone(self):
        self.driver.find_element(By.CSS_SELECTOR, 'button.sc-5ece21b1-1.hsasZd').click()

    def user_id_input(self):
        return self.driver.find_element(By.CSS_SELECTOR, 'input#idNumber.MuiInputBase-input.MuiFilledInput-input.mui-style-rtl-2bxn45')

    def user_password_input(self):
        return self.driver.find_element(By.CSS_SELECTOR, 'input#idLogin.MuiInputBase-input.MuiFilledInput-input.mui-style-rtl-2bxn45')

    def login_button(self):
        self.driver.find_element(By.CSS_SELECTOR, 'button.sc-e0eef0cb-2.jcQsHL').click()

    def single_use_code(self):
        self.driver.find_element(By.CSS_SELECTOR, 'button.sc-997dfd98-1.gNOVTs').click()

    def city_hotel_input(self):
        return self.driver.find_element(By.ID, 'main-input')

    def date_field(self):
        self.driver.find_element(By.CSS_SELECTOR, 'button.sc-ea37072c-0.hsJnAe').click()

    def room_field(self):
        self.driver.find_element(By.ID, 'main-search-rooms-select').click()

    def search_button(self):
        self.driver.find_element(By.CSS_SELECTOR, 'button.sc-4c638bf5-3.hukPDB').click()

    def hotel_list_israel(self):
        return self.driver.find_elements(By.CSS_SELECTOR, 'body > div.sc-f2b8f215-4.krWrfJ > div.sc-3edcab97-0.bSWdPC > div > div > div')

    def hotel_list_europe(self):
        return self.driver.find_elements(By.CSS_SELECTOR, 'body > div.sc-f2b8f215-4.krWrfJ > div.sc-3edcab97-0.bSWdPC > div > div')

    def brands_element_list(self):
        return self.driver.find_elements(By.CSS_SELECTOR, 'body > div.sc-f2b8f215-4.krWrfJ > div.sc-3edcab97-0.bSWdPC > div > div')

    def deal_element_list(self):
        return self.driver.find_elements(By.CSS_SELECTOR, 'body > div.sc-f2b8f215-4.krWrfJ > div.sc-3edcab97-0.bSWdPC > div')

    def more_element_list(self):
        return self.driver.find_elements(By.CSS_SELECTOR, 'body > div.sc-f2b8f215-4.krWrfJ > div.sc-3edcab97-4.kXLiBV > div.sc-3edcab97-5.gOMYYC > div > button:nth-child(7) > div.sc-3edcab97-11.HByCA')
