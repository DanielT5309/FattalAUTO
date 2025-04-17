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
            logging.info("👤 Opening personal zone (mobile login)...")

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
                logging.info("✅ Login menu opened via JavaScript interaction.")
            else:
                raise Exception("Login button not found in DOM.")

        except Exception as e:
            logging.error(f"❌ Failed to open login menu using JS: {e}")
            raise

    def user_id_input(self):
        return self.wait.until(EC.presence_of_element_located((By.ID, "idNumber")))

    def user_password_input(self):
        return self.wait.until(EC.presence_of_element_located((By.ID, "idLogin")))

    def click_login_button(self):
        logging.info("🔐 Clicking login button (mobile)...")
        btn = self.wait.until(EC.element_to_be_clickable((By.ID, "login-with-password-button")))
        btn.click()
        logging.info("✅ Login button clicked.")

    def close_post_login_popup(self):
        try:
            logging.info("📦 Checking for post-login popup...")
            close_btn = self.wait.until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, "div.sc-4a11a149-3.dVxqFs"
            )))
            self.driver.execute_script("arguments[0].click();", close_btn)
            logging.info("✅ Post-login popup closed.")
        except TimeoutException:
            logging.info("ℹ️ No post-login popup appeared.")

    def click_deals_and_packages_tab(self):
        """
        📦 Clicks on the 'דילים וחבילות' tab (Deals & Packages) using visible text, not ID.
        """
        try:
            logging.info("🧭 Clicking on 'דילים וחבילות' tab...")

            deals_tab = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'דילים וחבילות')]"))
            )

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", deals_tab)
            self.driver.execute_script("arguments[0].click();", deals_tab)

            logging.info("✅ Clicked on 'דילים וחבילות' tab successfully.")

        except Exception as e:
            logging.error(f"❌ Failed to click 'דילים וחבילות' tab: {e}")
            self.driver.save_screenshot("click_deals_tab_error.png")
            raise

