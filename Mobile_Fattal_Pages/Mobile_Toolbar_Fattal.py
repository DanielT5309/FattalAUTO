import time

from selenium.common import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import logging

class FattalMobileToolBar:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def open_login_menu(self):
        try:
            logging.info("Opening personal zone (mobile login)...")

            self.wait.until(lambda d: d.execute_script("""
                const el = document.querySelector('#header-user-section-button') || 
                           document.querySelector('.sc-cba239cf-1.ceoYye');
                if (!el) return false;
                el.scrollIntoView({behavior: 'smooth', block: 'center'});
                return true;
            """))


            # JS click (always)
            result = self.driver.execute_script("""
                const el = document.querySelector('#header-user-section-button') || 
                           document.querySelector('.sc-cba239cf-1.ceoYye');
                if (el) {
                    el.click();
                    return true;
                }
                return false;
            """)

            if result:
                logging.info("Login menu opened via JavaScript interaction.")
            else:
                raise Exception("Login button not found in DOM.")

        except Exception as e:
            logging.error(f"Failed to open login menu using JS: {e}")
            raise

    def user_id_input(self):
        return self.wait.until(EC.presence_of_element_located((By.ID, "idNumber")))

    def user_password_input(self):
        return self.wait.until(EC.presence_of_element_located((By.ID, "idLogin")))

    def click_login_button(self):
        logging.info("Clicking login button (mobile)...")
        btn = self.wait.until(EC.element_to_be_clickable((By.ID, "login-with-password-button")))
        btn.click()
        logging.info("Login button clicked.")

    def close_post_login_popup(self):
        try:
            logging.info("Checking for post-login popup...")
            close_btn = self.wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "div.sc-4a11a149-3.dVxqFs"
            )))
            self.driver.execute_script("arguments[0].click();", close_btn)
            logging.info("Post-login popup closed.")
        except TimeoutException:
            logging.info("No post-login popup appeared.")

    def click_deals_and_packages_tab(self):
        """
        Clicks on the 'דילים וחבילות' tab (Deals & Packages) using visible text, not ID.
        """
        try:
            logging.info("Clicking on 'דילים וחבילות' tab...")

            deals_tab = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'דילים וחבילות')]"))
            )

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", deals_tab)
            self.driver.execute_script("arguments[0].click();", deals_tab)

            logging.info("Clicked on 'דילים וחבילות' tab successfully.")

        except Exception as e:
            logging.error(f"Failed to click 'דילים וחבילות' tab: {e}")
            self.driver.save_screenshot("click_deals_tab_error.png")
            raise

    def click_more_tab_mobile(self):
        """
        Clicks the 'עוד' (More) footer tab on mobile.
        """
        try:
            logging.info("Trying to click on 'עוד' (More) tab in footer (mobile)...")

            # Wait for the element to be present & clickable
            more_tab = self.wait.until(
                EC.element_to_be_clickable((By.ID, "footer-mobile-tab_more"))
            )

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", more_tab)
            self.driver.execute_script("arguments[0].click();", more_tab)

            logging.info(" Clicked 'עוד' (More) footer tab successfully.")

        except Exception as e:
            logging.error(f"Failed to click 'עוד' (More) tab: {e}")
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            screenshot_path = f"click_more_tab_error_{timestamp}.png"
            self.driver.save_screenshot(screenshot_path)
            logging.error(f"Screenshot saved: {screenshot_path}")
            raise

    def click_contact_us_button_mobile(self):
        """
        Clicks the 'יצירת קשר' (Contact Us) tab under the 'More' footer menu in mobile view.
        """
        try:
            logging.info("Trying to click on the correct 'יצירת קשר' button in mobile footer...")

            xpath = ("//div[@id='footer-mobile-more-menu-main-content']"
                     "//div[contains(text(), 'יצירת קשר') and contains(@class, 'sc-e27ad7fa-10')]")

            contact_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", contact_btn)
            time.sleep(0.3)
            self.driver.execute_script("arguments[0].click();", contact_btn)

            logging.info("Clicked the correct 'יצירת קשר' (Contact Us) button successfully.")

        except Exception as e:
            logging.error(f"Failed to click correct 'יצירת קשר' button: {e}")
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            screenshot_path = f"click_contact_us_correct_error_{timestamp}.png"
            self.driver.save_screenshot(screenshot_path)
            logging.error(f"Screenshot saved: {screenshot_path}")
            raise

    def click_fattal_friends_club_tab(self):
        """
        Clicks the 'מועדון פתאל וחברים' (Fattal & Friends Club) tab in the mobile footer menu.
        """
        try:
            logging.info("Clicking 'מועדון פתאל וחברים' tab in mobile footer...")

            tab_xpath = "//div[contains(@id, 'footer-mobile-more-menu-tab-inner') and contains(., 'מועדון פתאל וחברים')]"
            tab = self.wait.until(EC.element_to_be_clickable((By.XPATH, tab_xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tab)
            time.sleep(0.3)
            tab.click()

            logging.info("'מועדון פתאל וחברים' tab clicked successfully.")
        except Exception as e:
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            path = os.path.join("Fattal_Tests", "Screenshots", f"click_fattal_friends_fail_{timestamp}.png")
            self.driver.save_screenshot(path)
            logging.error(f"Failed to click 'מועדון פתאל וחברים' tab. Screenshot saved: {path}")
            raise
