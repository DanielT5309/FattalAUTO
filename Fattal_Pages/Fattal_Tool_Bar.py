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
            logging.info("Clicked homepage logo successfully.")
        except Exception as e:
            logging.warning(f"Failed to click homepage logo: {e}")
            logging.info("Reloading homepage manually...")
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
        try:
            wait = WebDriverWait(self.driver, 10)

            # 1️⃣ Try direct button with visible text (best case)
            try:
                btn = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[.//div[text()='לאזור האישי']]"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                self.driver.execute_script("arguments[0].click();", btn)
                logging.info("✅ Clicked personal zone button via inner text <div>")
                return
            except Exception as e:
                logging.warning(f"⚠️ XPATH strategy failed: {e}")

            # 2️⃣ Try by aria-label (reliable fallback)
            try:
                btn = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='אזור אישי']"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                self.driver.execute_script("arguments[0].click();", btn)
                logging.info("✅ Clicked personal zone button via aria-label")
                return
            except Exception as e:
                logging.warning(f"⚠️ Aria-label strategy failed: {e}")

            # 3️⃣ Try by looping visible header buttons
            personal_buttons = self.driver.find_elements(By.CSS_SELECTOR, "header button")
            for btn in personal_buttons:
                if "אזור אישי" in btn.text:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    self.driver.execute_script("arguments[0].click();", btn)
                    logging.info("✅ Clicked personal zone button by scanning header buttons")
                    return

            raise Exception("🔍 Could not locate the personal zone button using any method.")

        except Exception as e:
            logging.error(f"❌ Failed to click personal zone button: {e}")
            raise

    def user_id_input(self):
        try:
            # Try multiple approaches to find the ID input field
            try:
                # First try by ID (most reliable if available)
                input_field = self.wait.until(
                    EC.visibility_of_element_located((By.ID, "idNumber"))
                )
                return input_field
            except:
                # Try by placeholder text
                input_field = self.wait.until(
                    EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='תעודת זהות']"))
                )
                return input_field
                
        except Exception as e:
            logging.error(f"Failed to find ID input field: {e}")
            # Last resort - try to find any visible input that might be the ID field
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            for input_field in inputs:
                if input_field.is_displayed() and "id" in input_field.get_attribute("id").lower():
                    return input_field
            
            # If we got here, we couldn't find the field
            raise

    def user_password_input(self):
        try:
            # Try multiple approaches to find the password input field
            try:
                # First try by ID (most reliable if available)
                input_field = self.wait.until(
                    EC.visibility_of_element_located((By.ID, "idLogin"))
                )
                return input_field
            except:
                # Try by type or placeholder
                input_field = self.wait.until(
                    EC.visibility_of_element_located((By.XPATH, "//input[@type='password' or @placeholder='סיסמה']"))
                )
                return input_field
                
        except Exception as e:
            logging.error(f"Failed to find password input field: {e}")
            # Last resort - try to find any password input
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            for input_field in inputs:
                if input_field.is_displayed() and input_field.get_attribute("type") == "password":
                    return input_field
            
            # If we got here, we couldn't find the field
            raise

    def login_button(self):
        try:
            # 1️⃣ Try by visible text "כניסה" (login)
            try:
                btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(text())='כניסה']"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                self.driver.execute_script("arguments[0].click();", btn)
                logging.info("✅ Clicked login button via visible text 'כניסה'")
                return
            except Exception as e:
                logging.warning(f"🔍 Text-based login button not found: {e}")

            # 2️⃣ Try by ID
            try:
                btn = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "login-with-password-button"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                self.driver.execute_script("arguments[0].click();", btn)
                logging.info("✅ Clicked login button via ID 'login-with-password-button'")
                return
            except Exception as e:
                logging.warning(f"🔍 ID-based login button not found: {e}")

            # 3️⃣ Try fallback in form button list
            form_buttons = self.driver.find_elements(By.CSS_SELECTOR, "form button")
            for btn in form_buttons:
                if "כניסה" in btn.text:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    self.driver.execute_script("arguments[0].click();", btn)
                    logging.info("✅ Clicked login button from form (text match)")
                    return

            # 4️⃣ Try JavaScript brute-force fallback
            clicked = self.driver.execute_script("""
                const buttons = Array.from(document.querySelectorAll('button'));
                const loginBtn = buttons.find(btn => btn.textContent.includes('כניסה'));
                if (loginBtn) {
                    loginBtn.scrollIntoView({block: 'center'});
                    loginBtn.click();
                    return true;
                }
                return false;
            """)
            if clicked:
                logging.info("✅ Clicked login button via JavaScript fallback")
                return

            # 5️⃣ Give up
            raise Exception("❌ Could not find login button via any strategy")

        except Exception as e:
            logging.error(f"🚨 Failed to click login button: {e}")
            raise

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
