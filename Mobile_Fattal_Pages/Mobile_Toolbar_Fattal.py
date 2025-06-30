import os
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

            # Updated selector: use the new class names from your DOM
            close_btn = self.wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "div.sc-60b5ebd3-3.gMhFjt"
            )))

            self.driver.execute_script("arguments[0].click();", close_btn)
            logging.info("✅ Post-login popup closed.")

        except TimeoutException:
            logging.info("ℹ️ No post-login popup appeared.")
        except Exception as e:
            logging.error(f"❌ Failed to close popup: {e}")

    def close_post_login_popup_expired(self):
        try:
            logging.info("Checking for post-login popup...")

            # Updated selector: use the new class names from your DOM
            close_btn = self.wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, ".sc-4642954a-3.lnXKWk"
            )))

            self.driver.execute_script("arguments[0].click();", close_btn)
            logging.info("✅ Post-login popup closed.")

        except TimeoutException:
            logging.info("ℹ️ No post-login popup appeared.")
        except Exception as e:
            logging.error(f"❌ Failed to close popup: {e}")

    def handle_membership_renewal_popup(self):
        """Handles the optional 'membership renewal' popup by clicking the renewal button if it appears."""
        try:
            logging.info("Checking for membership renewal popup...")

            popup_container = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "search-expired-before-vacation-dialog-container"))
            )

            if popup_container.is_displayed():
                logging.info("Membership renewal popup is displayed.")
                try:
                    renew_button = self.wait.until(
                        EC.element_to_be_clickable((By.ID, "search-expired-before-vacation-dialog-button-main"))
                    )
                    renew_button.click()
                    logging.info("Clicked on 'לחידוש המועדון בתהליך ההזמנה' button.")
                except TimeoutException:
                    logging.warning("Renewal button not clickable even though popup is present.")
            else:
                logging.info("Membership renewal popup is not visible. Continuing test flow.")

        except TimeoutException:
            logging.info("Membership renewal popup did not appear. Proceeding without renewal.")
        except Exception as e:
            logging.error(f"Unexpected error while handling membership renewal popup: {e}")

    def click_deals_and_packages_tab(self):
        """
        Clicks on the 'דילים וחבילות' tab using its unique ID instead of unreliable text matching.
        """
        try:
            logging.info("Clicking on 'דילים וחבילות' tab using ID...")

            deals_tab = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.ID, "footer-mobile-tab_deals"))
            )

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", deals_tab)
            time.sleep(0.3)  # brief wait for potential animation
            self.driver.execute_script("arguments[0].click();", deals_tab)

            logging.info("✅ Clicked on 'דילים וחבילות' tab successfully.")

        except Exception as e:
            logging.error(f"❌ Failed to click 'דילים וחבילות' tab: {e}")
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
        Clicks the 'יצירת קשר' (Contact Us) tab in the mobile footer using the known element ID.
        """
        try:
            logging.info("Trying to click 'יצירת קשר' button in mobile footer using ID...")

            contact_btn = self.wait.until(
                EC.element_to_be_clickable((By.ID, "footer-mobile-more-menu-tab-headernull"))
            )

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", contact_btn)
            time.sleep(0.3)
            self.driver.execute_script("arguments[0].click();", contact_btn)

            logging.info("✅ Clicked 'יצירת קשר' (Contact Us) button successfully by ID.")

        except Exception as e:
            logging.error(f"❌ Failed to click 'יצירת קשר' button by ID: {e}")
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            screenshot_path = f"screenshots/contact_us_click_error_{timestamp}.png"
            self.driver.save_screenshot(screenshot_path)
            logging.error(f"📸 Screenshot saved: {screenshot_path}")
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

    def click_renew_membership_link(self, timeout=10):
        """
        Clicks the 'חידוש המועדון' link using class and href.
        """
        try:
            logging.info("Waiting for renew link to be clickable by class + href...")
            selector = "a[href*='/fattal-and-friends/checkout']"
            link = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            link.click()
            logging.info("✅ Clicked 'חידוש המועדון' link successfully (via CSS selector).")
        except Exception as e:
            logging.error(f"❌ Failed to click renew link: {e}")
            raise

    def close_any_club_popup(self):
        """
        Attempts to close any club-related popup: either specific post-renewal or general one.
        """
        selectors = [
            # Try the specific confirmation popup first
            "div.sc-c18678ea-3.iOzwib",
            # Then try the more generic popup
            "div[class^='sc-c18678ea-3']"
        ]

        for selector in selectors:
            try:
                logging.info(f"Trying to close popup with selector: {selector}")
                close_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                self.driver.execute_script("arguments[0].click();", close_btn)
                logging.info(f"✅ Popup closed using selector: {selector}")
                return  # Exit after the first successful close
            except TimeoutException:
                logging.debug(f"ℹ️ Popup not found with selector: {selector}")
            except Exception as e:
                logging.warning(f"⚠️ Attempt with selector '{selector}' failed: {e}")

        logging.info("ℹ️ No club-related popup appeared.")

    def click_login_with_email_button(self):
        """
        Clicks the footer login button: 'כניסה באמצעות ת.ז וסיסמה'
        """
        try:
            logging.info("Trying to click 'כניסה באמצעות ת.ז וסיסמה' footer button...")

            button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "login-footer-button-type"))
            )

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(0.3)
            self.driver.execute_script("arguments[0].click();", button)

            logging.info("✅ Clicked 'כניסה באמצעות ת.ז וסיסמה' footer button successfully.")
        except Exception as e:
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            screenshot_path = os.path.join("Fattal_Tests", "Screenshots", f"click_footer_login_fail_{timestamp}.png")
            self.driver.save_screenshot(screenshot_path)
            logging.error(f"❌ Failed to click footer login button: {e}")
            logging.error(f"📸 Screenshot saved: {screenshot_path}")
            raise
